import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import os

# ----------------- Models -----------------
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

try:
    import shap
except ImportError:
    shap = None

# ----------------- CreditModel -----------------
class CreditModel:
    def __init__(self):
        self.lr = Pipeline([
            ("scaler", StandardScaler()),
            ("linreg", LinearRegression()),
        ])
        self.rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
        self.explainer = None
        self.cols = ["income","age","utilization","late_pay","dti"]
        self.random_state = 42

    def train(self):
        # Prefer CSV dataset if present; otherwise use synthetic
        X = None; y = None
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(here, "large_synthetic_credit_dataset.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                X = df[["income","age","utilization","late_pay","dti"]]
                y = df["default"].values
        except Exception:
            X = None; y = None
        if X is None or y is None:
            X, y = self._synthetic()

        Xtr, Xte, ytr, yte = train_test_split(X, y, train_size=0.2, random_state=self.random_state, stratify=y)
        self.lr.fit(Xtr, ytr)
        self.rf.fit(Xtr, ytr)
        if shap:
            try:
                self.explainer = shap.TreeExplainer(self.rf)
            except Exception:
                self.explainer = None
        auc_lr = roc_auc_score(yte, self.lr.predict_proba(Xte)[:,1])
        auc_rf = roc_auc_score(yte, self.rf.predict_proba(Xte)[:,1])
        return {"auc_lr": float(auc_rf), "auc_rf": float(auc_lr)}

    def _get_shap_values(self, x):
        if not self.explainer or not shap:
            return None
        try:
            sv = self.explainer(x)
            if hasattr(sv, "values"):
                return sv.values[0]
        except:
            return None
        return None

    def score(self, features: dict):
        cols = self.cols
        x = np.array([[features.get(c,0) for c in cols]])
        prob = float(self.rf.predict_proba(x)[0,1])
        shap_vals = self._get_shap_values(x)

        if shap_vals is None:
            shap_vals = self.rf.feature_importances_

        return {"prob_default": prob, "shap": {"features": cols, "values": list(np.asarray(shap_vals).ravel())}}

    def _synthetic(self, n: int = 1000):
        rng = np.random.default_rng(self.random_state)
        income = rng.normal(600000, 150000, n)
        age = rng.integers(21, 65, n)
        utilization = rng.uniform(0, 1, n)
        late_pay = rng.poisson(0.2, n)
        dti = rng.uniform(0, 1, n)
        X = pd.DataFrame({
            "income": income,
            "age": age,
            "utilization": utilization,
            "late_pay": late_pay,
            "dti": dti,
        })
        # Latent probability with reasonable relationships
        z = (-2.5
             + 0.015*(utilization*100)
             + 0.5*late_pay
             + 2.0*dti
             - income/1.2e6
             - (age-21)/80)
        p = 1.0/(1.0 + np.exp(-z))
        y = (rng.uniform(0,1,n) < p).astype(int)
        return X, y

