import numpy as np
import pandas as pd
import os
from dataclasses import dataclass
from typing import Dict, Any
from loguru import logger

# Optional heavy deps
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
    def __init__(self, csv_file: str = "HistoricalData_1761328678783.csv"):
        self.lstm = None
        self.xgb = None
        self.csv_file = csv_file
        self.series = None  # store closing price series

    def _load_historical_series(self):
        """Load historical closing prices from CSV."""
        try:
            df = pd.read_csv(self.csv_file, parse_dates=["date"])
            df = df.sort_values("date")  # ensure chronological order
            self.series = df["closing price"].astype(float)
            return self.series
        except Exception:
            def try_read(path: str):
                df = pd.read_csv(path)
                cols = {c.lower().strip(): c for c in df.columns}
                if "date" not in cols:
                    raise ValueError("date column not found")
                dcol = cols["date"]
                df[dcol] = pd.to_datetime(df[dcol])
                if "close/last" in cols:
                    pcol = cols["close/last"]
                    price = pd.to_numeric(df[pcol].replace({"$": "", ",": ""}, regex=True), errors="coerce")
                elif "close" in cols:
                    pcol = cols["close"]
                    price = pd.to_numeric(df[pcol], errors="coerce")
                elif "closing price" in cols:
                    pcol = cols["closing price"]
                    price = pd.to_numeric(df[pcol], errors="coerce")
                else:
                    raise ValueError("price column not found")
                return price.dropna().astype(float)

            try:
                self.series = try_read(self.csv_file)
                return self.series
            except Exception:
                alt = os.path.join(os.path.dirname(__file__), os.path.basename(self.csv_file))
                try:
                    self.series = try_read(alt)
                    return self.series
                except Exception as e2:
                    logger.error(f"Failed to load historical CSV: {e2}")
                    return None

    def _gen_sine_series(self, n: int = 300, noise: float = 0.05) -> pd.Series:
        t = np.arange(n)
        y = np.sin(0.05 * t) + np.random.normal(0, noise, size=n)
        return pd.Series(y)

    def train_baselines(self):
        """Train models on historical closing prices."""
        series = self._load_historical_series()
        if series is None:
            logger.warning("Using synthetic sine series fallback")
            series = self._gen_sine_series()
            self.series = series
        else:
            self.series = series

        returns = series.pct_change().fillna(0)

        # --- BUG #3: Insufficient Training Data ---
        # This bug is intentionally unsolvable. If the dataset is too small, both LSTM and XGBoost will skip training.
        # The correct fix is to explain the data limitation and suggest data augmentation or simpler models.

        # LSTM if torch available
        if torch and nn:
            seq_len = 20
            X, Y = [], []
            arr = returns.values.astype(np.float32).reshape(-1, 1)
            for i in range(max(0, len(arr) - seq_len)):
                X.append(arr[i : i + seq_len])
                Y.append(arr[i + seq_len])
            if len(X) > 0:
                X = np.stack(X)
                Y = np.stack(Y)
                X_t = torch.tensor(X)
                Y_t = torch.tensor(Y)
                model = SimpleLSTM(1, 16, 1)
                optim = torch.optim.Adam(model.parameters(), lr=0.01)
                loss_fn = nn.MSELoss()
                for _ in range(30):
                    pred = model(X_t)
                    loss = loss_fn(pred, Y_t)
                self.lstm = model
            else:
                logger.warning("Not enough data to train LSTM; skipping. (See BUG #3)")
        else:
            logger.warning("Torch not available; skipping LSTM training.")

        # XGBoost (optional)
        if XGBRegressor:
            if len(returns) >= 10:
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
                logger.warning("Not enough data to train XGBoost; skipping. (See BUG #3)")
        else:
            logger.warning("xgboost not installed; skipping XGBoost model.")

    def predict_next(self) -> PredictionResult:
        """Predict the next period return with whichever model is available."""
        if self.series is None:
            self._load_historical_series()

        if self.xgb:
            n = len(self.series)  # predict next step
            pred = float(self.xgb.predict(np.array([[n]])).item())
            return PredictionResult(model="xgboost", next_return=pred, details={"note": "historic series"})

        if self.lstm and torch:
            # use last 20 returns as input
            last_seq = self.series.pct_change().fillna(0).values[-20:].astype(np.float32).reshape(1, 20, 1)
            seq = torch.tensor(last_seq)
            with torch.no_grad():
                pred = float(self.lstm(seq).item())
            return PredictionResult(model="lstm", next_return=pred, details={"note": "last 20 returns input"})

        # Naive fallback if no models available
        pred = float(np.random.normal(0, 0.01))
        return PredictionResult(model="naive", next_return=pred, details={"fallback": True})
