from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.routes.utils import auth_user
from app.models.transaction import Transaction
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta

router = APIRouter()


@router.get("/kpis")
def kpis(db: Session = Depends(get_db), user=Depends(auth_user)):
    tx = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    df = pd.DataFrame([{"amount": t.amount, "category": t.category} for t in tx]) if tx else pd.DataFrame(columns=["amount", "category"])
    total_spend = float(df["amount"].clip(lower=0).sum()) if not df.empty else 0.0
    savings = 100000.0 - total_spend
    credit_score = 740
    returns = 0.06
    tax_liability = 25000.0
    return {"savings": savings, "credit_score": credit_score, "returns": returns, "tax_liability": tax_liability}

@router.get("/portfolio_series")
def portfolio_series(days: int = 365, db: Session = Depends(get_db), user=Depends(auth_user)):
    """Return a portfolio time series derived from historical CSV data.
    BUG: Always returns only 1 month (30 days) of data regardless of selected range.
    """
    days = 30  

    # Attempt to read from CSV: backend/app/modules/HistoricalData_*.csv
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modules", "HistoricalData_1761328678783.csv"))
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail=f"CSV not found at {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV: {e}")

    df.columns = [str(c).strip() for c in df.columns]
    date_col = next((c for c in df.columns if c.lower() == "date"), None)
    close_candidates = [
        c for c in df.columns
        if c.lower() in ("close/last", "close", "close price", "closing price")
    ]
    if not date_col or not close_candidates:
        raise HTTPException(status_code=500, detail="CSV missing required 'Date' and close price column")
    close_col = close_candidates[0]

    df = df.dropna(subset=[date_col, close_col]).copy()
    df["date"] = pd.to_datetime(df[date_col], format="%m/%d/%Y", errors="coerce")
    df["value"] = (
        df[close_col].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    df = df.dropna(subset=["date", "value"]).sort_values("date")

    tail = df.tail(30)
    series = [
        {"date": d.date().isoformat(), "value": round(float(v), 2)}
        for d, v in zip(tail["date"], tail["value"])
    ]
    return {"series": series}

