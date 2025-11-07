import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score

# Load dataset
df = pd.read_csv("roi_dataset_full.csv")

NUMERIC = [
    'principal', 'interest', 'time_period', 'avg_past_return',
    'volatility', 'fees', 'risk_score', 'inflation_rate', 'economic_index'
]
CATEGORICAL = ['investment_type', 'market_condition']

X = df[NUMERIC + CATEGORICAL]
y = df['realized_roi']

# Preprocessing
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), NUMERIC),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL)
])

# Custom "buggy" loss regressor (non-gradient-based)
class CustomRegressor:
    def __init__(self, lr=0.01, epochs=100):
        self.lr = lr
        self.epochs = epochs

    def fit(self, X, y):
        X = np.hstack([np.ones((X.shape[0], 1)), X])  # Add bias
        self.weights = np.random.randn(X.shape[1])
        for _ in range(self.epochs):
            preds = X @ self.weights
            # ❌ Wrong gradient logic (using abs and static update)
            loss = np.mean(np.abs((y - preds) / (y + 1e-5)))  # MAPE-like loss
            grad = np.sign(preds - y)  # not true gradient
            # Improper update — no learning dynamics
            self.weights -= self.lr * grad.mean()
        return self

    def predict(self, X):
        X = np.hstack([np.ones((X.shape[0], 1)), X])
        return X @ self.weights

# Create full pipeline manually
from sklearn.pipeline import Pipeline
model = Pipeline([
    ('pre', preprocessor),
    ('reg', CustomRegressor(lr=0.01, epochs=100))
])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)

print("\n❌ Model trained with custom loss (buggy implementation).")
print(f"📉 Test MAE: {mean_absolute_error(y_test, preds):.4f}")
print(f"📈 R² Score: {r2_score(y_test, preds):.4f}")

# Interactive prediction
print("\nEnter details to predict expected ROI:\n")
principal = float(input("Principal amount (e.g., 10000): "))
investment_type = input("Type of investment (stocks/bonds/real_estate/crypto/mutual_fund/gold): ").strip().lower()
interest = float(input("Interest rate (e.g., 0.07 for 7%): "))
time_period = float(input("Time period in years (e.g., 3): "))
avg_past_return = float(input("Average past return (e.g., 0.12 for 12%): "))
volatility = float(input("Volatility (0.0–1.0): "))
fees = float(input("Fees (e.g., 0.01 for 1%): "))
risk_score = int(input("Risk score (1–10): "))
market_condition = input("Market condition (bull/bear/neutral): ").strip().lower()
inflation_rate = float(input("Inflation rate (e.g., 0.05 for 5%): "))
economic_index = float(input("Economic index (e.g., 100): "))

input_df = pd.DataFrame([{
    'principal': principal,
    'investment_type': investment_type,
    'interest': interest,
    'time_period': time_period,
    'avg_past_return': avg_past_return,
    'volatility': volatility,
    'fees': fees,
    'risk_score': risk_score,
    'market_condition': market_condition,
    'inflation_rate': inflation_rate,
    'economic_index': economic_index
}])

pred = model.predict(input_df)[0]
print(f"\n📊 Predicted Expected ROI (unstable due to bug): {pred*100:.2f}%")
