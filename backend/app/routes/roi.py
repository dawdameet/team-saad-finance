from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, constr, conint, confloat
from typing import Literal
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

router = APIRouter(prefix="/api/roi", tags=["roi"])

# Define request schema
class RoiRequest(BaseModel):
    principal: confloat(ge=0) = Field(..., description="Principal amount")
    investment_type: Literal['stocks','bonds','real_estate','crypto','mutual_fund','gold']
    interest: confloat(ge=0) = Field(..., description="Annual interest rate as decimal e.g. 0.07")
    time_period: confloat(gt=0) = Field(..., description="Time in years")
    avg_past_return: confloat(ge=0) = Field(..., description="Historical avg return decimal")
    volatility: confloat(ge=0, le=1) = Field(..., description="0..1")
    fees: confloat(ge=0) = Field(..., description="Decimal e.g. 0.01")
    risk_score: conint(ge=1, le=10)
    market_condition: Literal['bull','bear','neutral']
    inflation_rate: confloat(ge=0) = Field(..., description="Decimal e.g. 0.05")
    economic_index: confloat(ge=0)

# Load and train model once on import
NUMERIC = [
    'principal', 'interest', 'time_period', 'avg_past_return',
    'volatility', 'fees', 'risk_score', 'inflation_rate', 'economic_index'
]
CATEGORICAL = ['investment_type', 'market_condition']

_model: Pipeline | None = None


def _train_model() -> Pipeline:
    data_path = Path(__file__).resolve().parents[1] / 'modules' / 'new2' / 'roi_dataset_full.csv'
    if not data_path.exists():
        raise FileNotFoundError(f"ROI dataset not found at {data_path}")
    df = pd.read_csv(data_path)
    X = df[NUMERIC + CATEGORICAL]
    y = df['realized_roi']
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), NUMERIC),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL)
    ])
    model = Pipeline([
        ('pre', preprocessor)
    ])
    # Train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    # Optionally evaluate (not returned)
    _ = mean_absolute_error(y_test, model.predict(X_test))
    return model


def _get_model() -> Pipeline:
    global _model
    if _model is None:
        with open('model.pkl', 'r') as model_file:
            _model = joblib.load(model_file)
    return _model


@router.post('/predict')
def predict_roi(req: RoiRequest):
    try:
        model = _get_model()
        input_df = pd.DataFrame([{**req.model_dump()}])
        pred = float(model.predict(input_df)[0])
        return {
            'predicted_roi': pred,
            'predicted_roi_percent': pred * 100.0
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
