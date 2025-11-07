from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.routes.utils import auth_user
from app.modules.trial import normalize_symbol, get_stock_snapshot

router = APIRouter()

_watchlist: List[str] = []

class AddSymbol(BaseModel):
    symbol: str

@router.get("/", summary="Get current watchlist with snapshots")
def get_watchlist(user = Depends(auth_user)):
    items = [get_stock_snapshot(s) for s in _watchlist]
    return {"items": items}

@router.post("/", summary="Add a symbol to watchlist")
def add_symbol(payload: AddSymbol, user = Depends(auth_user)):
    s = normalize_symbol(payload.symbol)
    if not s:
        raise HTTPException(400, "Symbol required")
    if s not in _watchlist:
        _watchlist.append(s)
    return {"ok": True, "symbol": s, "count": len(_watchlist)}

@router.delete("/{symbol}", summary="Remove a symbol from watchlist")
def remove_symbol(symbol: str, user = Depends(auth_user)):
    s = normalize_symbol(symbol)
    if s in _watchlist:
        _watchlist.remove(s)
    return {"ok": True, "symbol": s, "count": len(_watchlist)}
