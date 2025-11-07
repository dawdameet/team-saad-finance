import random
import time


def normalize_symbol(symbol: str) -> str:
    """Normalize a market symbol string."""
    return (symbol or "").strip().upper()


def get_mock_price(symbol: str) -> float:
    """Return a stable-ish mock price per symbol for demo purposes."""
    s = normalize_symbol(symbol)
    # Create a pseudo-stable seed based on symbol
    rnd = random.Random(hash(s) & 0xFFFFFFFF)
    base = rnd.uniform(10, 500)
    # Add small temporal oscillation so it feels alive
    oscillation = (time.time() % 10) / 10.0  # 0..1
    price = base * (0.98 + 0.04 * oscillation)
    return round(price, 2)

from app.core.config import settings

# Simple in-process cache for live prices
PRICE_CACHE = {}  # symbol -> (price: float, ts: float)
CACHE_TTL = 60.0

def _fetch_alphavantage_price(symbol: str) -> float:
    s = normalize_symbol(symbol)
    if not s:
        raise ValueError("empty symbol")
    api_key = settings.ALPHAVANTAGE_API_KEY
    if not api_key:
        raise RuntimeError("ALPHAVANTAGE_API_KEY not configured")
    # Use GLOBAL_QUOTE for current price
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": s, "apikey": api_key}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    quote = data.get("Global Quote") or {}
    price_str = quote.get("05. price")
    if not price_str:
        # AlphaVantage often rate-limits; signal to fallback
        raise RuntimeError(f"No price in AlphaVantage response: {data}")
    return float(price_str)

def get_price(symbol: str) -> float:
    """Return a price, using AlphaVantage when configured, else mock; caches for TTL."""
    s = normalize_symbol(symbol)
    now = time.time()
    if s in PRICE_CACHE:
        p, ts = PRICE_CACHE[s]
        if (now - ts) < CACHE_TTL:
            return p
    # Try live, then fallback
    try:
        if settings.ALPHAVANTAGE_API_KEY:
            p = _fetch_alphavantage_price(s)
            PRICE_CACHE[s] = (p, now)
            return p
    except Exception:
        pass
    p = get_mock_price(s)
    PRICE_CACHE[s] = (p, now)
    return p

# Snapshot cache: includes price, %change, SMA20, RSI14 and prediction
SNAPSHOT_CACHE = {}  # symbol -> (payload: dict, ts: float)

def get_stock_snapshot(symbol: str) -> dict:
    """Return a rich stock snapshot for a symbol.
    Shape: {symbol, price, percent_change, SMA20, RSI14, pred_return, pred_model}
    """
    s = normalize_symbol(symbol)
    now = time.time()
    if s in SNAPSHOT_CACHE:
        data, ts = SNAPSHOT_CACHE[s]
        if (now - ts) < CACHE_TTL:
            return data

    api_key = settings.ALPHAVANTAGE_API_KEY
    # Try live data if API key is configured
    if api_key:
        try:
            url = "https://www.alphavantage.co/query"
            # Use intraday for recent price and previous close approximation
            p_params = {"function":"TIME_SERIES_INTRADAY","symbol":s,"interval":"5min","apikey":api_key}
            d_price = requests.get(url, params=p_params, timeout=12).json()
            series = d_price.get("Time Series (5min)", {})
            keys = list(series.keys())
            if len(keys) >= 2:
                last_ts, prev_ts = keys[0], keys[1]
                last_price = float(series[last_ts]["4. close"])  # type: ignore[index]
                prev_close = float(series[prev_ts]["4. close"])  # type: ignore[index]
                pct_change = ((last_price - prev_close) / prev_close) * 100.0
            else:
                last_price = get_price(s)
                pct_change = 0.0

            # SMA20 daily
            sma_params = {"function":"SMA","symbol":s,"interval":"daily","time_period":20,"series_type":"close","apikey":api_key}
            d_sma = requests.get(url, params=sma_params, timeout=12).json()
            sma_vals = d_sma.get("Technical Analysis: SMA", {})
            sma20 = float(list(sma_vals.values())[0]["SMA"]) if sma_vals else None

            # RSI14 daily
            rsi_params = {"function":"RSI","symbol":s,"interval":"daily","time_period":14,"series_type":"close","apikey":api_key}
            d_rsi = requests.get(url, params=rsi_params, timeout=12).json()
            rsi_vals = d_rsi.get("Technical Analysis: RSI", {})
            rsi14 = float(list(rsi_vals.values())[0]["RSI"]) if rsi_vals else None

            pred = predictor.predict_next() if 'predictor' in globals() else None
            payload = {
                "symbol": s,
                "price": round(float(last_price), 2),
                "percent_change": round(float(pct_change), 2),
                "SMA20": round(float(sma20), 2) if sma20 is not None else None,
                "RSI14": round(float(rsi14), 2) if rsi14 is not None else None,
                "pred_return": round(float(pred.next_return), 4) if pred else 0.0,
                "pred_model": getattr(pred, 'model', 'naive') if pred else 'naive',
            }
            SNAPSHOT_CACHE[s] = (payload, now)
            return payload
        except Exception:
            # fallthrough to mock
            pass

    # Fallback mock snapshot
    price = get_mock_price(s)
    # Create deterministic fake metrics per symbol for consistency
    rnd = random.Random(hash(s) & 0xFFFFFFFF)
    pct_change = rnd.uniform(-2.5, 2.5)
    sma20 = price * rnd.uniform(0.9, 1.1)
    rsi14 = rnd.uniform(30, 70)
    pred = predictor.predict_next() if 'predictor' in globals() else None
    payload = {
        "symbol": s,
        "price": price,
        "percent_change": round(pct_change, 2),
        "SMA20": round(sma20, 2),
        "RSI14": round(rsi14, 2),
        "pred_return": round(float(pred.next_return), 4) if pred else 0.0,
        "pred_model": getattr(pred, 'model', 'naive') if pred else 'naive',
    }
    SNAPSHOT_CACHE[s] = (payload, now)
    return payload

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any
from loguru import logger
import requests
import time

# -------------------- Optional ML dependencies --------------------
try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
    nn = None

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None

# -------------------- Prediction Models --------------------
@dataclass
class PredictionResult:
    model: str
    next_return: float
    details: Dict[str, Any]

class SimpleLSTM(nn.Module if nn else object):
    def __init__(self, input_size=1, hidden=16, layers=1):
        if nn:
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden, num_layers=layers, batch_first=True)
            self.fc = nn.Linear(hidden, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)

class InvestmentPredictor:
    def __init__(self):
        self.lstm = None
        self.xgb = None

    def _gen_sine_series(self, n=300, noise=0.05):
        t = np.arange(n)
        y = np.sin(0.05 * t) + np.random.normal(0, noise, size=n)
        return pd.Series(y)

    def train_baselines(self):
        series = self._gen_sine_series()
        returns = series.pct_change().fillna(0)

        # LSTM if torch available
        if torch and nn:
            seq_len = 20
            X, Y = [], []
            arr = returns.values.astype(np.float32).reshape(-1, 1)
            for i in range(len(arr) - seq_len):
                X.append(arr[i : i + seq_len])
                Y.append(arr[i + seq_len])
            X = np.stack(X)
            Y = np.stack(Y)
            X_t = torch.tensor(X)
            Y_t = torch.tensor(Y)
            model = SimpleLSTM(1, 16, 1)
            optim = torch.optim.Adam(model.parameters(), lr=0.01)
            loss_fn = nn.MSELoss()
            for _ in range(30):
                optim.zero_grad()
                pred = model(X_t)
                loss = loss_fn(pred, Y_t)
                loss.backward()
                optim.step()
            self.lstm = model
        else:
            logger.warning("Torch not available; skipping LSTM training.")

        # XGBoost (optional)
        if XGBRegressor:
            X_feat = np.arange(len(returns)).reshape(-1, 1)
            y = returns.values
            model = XGBRegressor(
                n_estimators=200,
                max_depth=3,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
            )
            model.fit(X_feat, y)
            self.xgb = model
        else:
            logger.warning("xgboost not installed; skipping XGBoost model.")

    def predict_next(self) -> PredictionResult:
        if self.xgb:
            n = 400
            pred = float(self.xgb.predict(np.array([[n]])).item())
            return PredictionResult(model="xgboost", next_return=pred, details={"note": "synthetic series"})

        if self.lstm and torch:
            seq = torch.zeros((1, 20, 1), dtype=torch.float32)
            with torch.no_grad():
                pred = float(self.lstm(seq).item())
            return PredictionResult(model="lstm", next_return=pred, details={"note": "zero-seq input"})

        # Naive fallback
        pred = float(np.random.normal(0, 0.01))
        return PredictionResult(model="naive", next_return=pred, details={"fallback": True})

# -------------------- Stock Watchlist --------------------
API_KEY = "ZA31IRU45FPLV0ZN"
UPDATE_INTERVAL = 60  # seconds between updates
watchlist = []
predictor = InvestmentPredictor()
predictor.train_baselines()  # train synthetic models once

def get_stock_data(symbol):
    url = "https://www.alphavantage.co/query"
    
    # Intraday price
    params_price = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": API_KEY
    }
    response_price = requests.get(url, params=params_price)
    data_price = response_price.json()
    
    # SMA(20)
    params_sma = {
        "function": "SMA",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 20,
        "series_type": "close",
        "apikey": API_KEY
    }
    response_sma = requests.get(url, params=params_sma)
    data_sma = response_sma.json()
    
    # RSI(14)
    params_rsi = {
        "function": "RSI",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 14,
        "series_type": "close",
        "apikey": API_KEY
    }
    response_rsi = requests.get(url, params=params_rsi)
    data_rsi = response_rsi.json()
    
    try:
        # Latest intraday price
        last_timestamp = list(data_price["Time Series (1min)"].keys())[0]
        last_price = float(data_price["Time Series (1min)"][last_timestamp]["4. close"])
        prev_close_timestamp = list(data_price["Time Series (1min)"].keys())[1]
        prev_close = float(data_price["Time Series (1min)"][prev_close_timestamp]["4. close"])
        pct_change = ((last_price - prev_close) / prev_close) * 100
        
        # Latest SMA
        sma_values = data_sma["Technical Analysis: SMA"]
        latest_sma = float(list(sma_values.values())[0]["SMA"])
        
        # Latest RSI
        rsi_values = data_rsi["Technical Analysis: RSI"]
        latest_rsi = float(list(rsi_values.values())[0]["RSI"])
        
        # Prediction
        prediction = predictor.predict_next()
        
        return {
            "symbol": symbol,
            "price": last_price,
            "%change": pct_change,
            "SMA20": latest_sma,
            "RSI14": latest_rsi,
            "pred_return": prediction.next_return,
            "pred_model": prediction.model
        }
    except KeyError:
        return {"symbol": symbol, "error": "Could not fetch data"}

def print_watchlist():
    print("\n----- Live Stock Watchlist + Prediction -----")
    print(f"{'Symbol':<10}{'Price':<10}{'%Change':<10}{'SMA20':<10}{'RSI14':<10}{'Pred(Next)':<12}{'Model':<10}")
    print("-"*80)
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "error" in data:
            print(f"{symbol:<10}Error fetching data")
        else:
            print(f"{data['symbol']:<10}{data['price']:<10.2f}{data['%change']:<10.2f}"
                  f"{data['SMA20']:<10.2f}{data['RSI14']:<10.2f}{data['pred_return']:<12.4f}{data['pred_model']:<10}")
    print("-"*80)

# -------------------- Main Program --------------------
def main():
    print("Welcome to Terminal Stock Watchlist + Predictor!")
    print("Type stock symbols to add to your watchlist (e.g., AAPL, TSLA). Type 'start' to begin updates.\n")
    
    while True:
        user_input = input("Enter symbol or 'start': ").strip().upper()
        if user_input == "START":
            break
        elif user_input:
            if user_input not in watchlist:
                watchlist.append(user_input)
                print(f"{user_input} added to watchlist.")
            else:
                print(f"{user_input} is already in the watchlist.")

    print("\nStarting live watchlist. Press Ctrl+C to exit.\n")
    
    try:
        while True:
            print_watchlist()
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("\nExiting watchlist. Goodbye!")

if __name__ == "__main__":
    main()
