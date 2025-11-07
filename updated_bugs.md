# Detailed Bug Catalog - Fintech Project

This document provides comprehensive information about all intentionally planted bugs in the Fintech project. Each bug entry is designed to enable an automated judge (LLM) to understand the bug, identify its presence in code, and validate whether a contestant's solution correctly fixes it.

---

## Bug List


### [B01] Dashboard Data Not Displaying

**Type:** Medium
**Category:** UI Rendering / Data Flow
**File:** `frontend/src/pages/Dashboard.jsx`
**Location:** `useEffect` hook and JSX rendering section.
**Line Numbers:** ~11-12, ~15-16, ~30-45, ~53-55

**Bug Description:**
When the user visits the dashboard, only section titles like Savings, Credit Score, Returns, and Tax liability are visible, but the corresponding numeric values are missing. The analytics graph area is also empty, suggesting that data is not being fetched, parsed, or bound correctly to UI components.

**Root Cause:**
The `useEffect` hook correctly calls the API endpoints `/api/dashboard/kpis` and `/api/dashboard/portfolio_series`. However, immediately after fetching the data, the `setKpis({})` and `setSeries([])` calls are made, which explicitly reset the state variables `kpis` and `series` to empty objects/arrays. This overwrites the fetched data, preventing it from being displayed in the UI.

**Impact:**
- **Severity:** High
- **User Impact:** The dashboard displays no meaningful financial data, rendering it useless for the user. Key Performance Indicators (KPIs) and portfolio trends are absent.
- **System Impact:** The frontend fails to correctly display critical information, leading to a broken user experience. The backend API calls are made unnecessarily if their results are immediately discarded.
- **Affected Components:** Dashboard KPI display, Portfolio Trend chart.

**Expected Symptom:**
- The "Savings", "Credit Score", "Returns (est.)", and "Tax Liability" sections show placeholder values (e.g., "₹ -", "-") instead of actual numbers.
- The "Portfolio Trend" graph area is completely empty, showing no lines or data points.
- Network requests to `/api/dashboard/kpis` and `/api/dashboard/portfolio_series` succeed (visible in browser dev tools), but the UI does not update.

**Validation Criteria for Fix:**
A valid solution must:
1. Remove the `setKpis({})` and `setSeries([])` calls that immediately follow successful API data fetching within the `useEffect` hook.
2. Ensure that the fetched data from `kpiRes` is correctly assigned to the `kpis` state variable (e.g., `setKpis(kpiRes)`).
3. Ensure that the fetched data from `dataRes` is correctly assigned to the `series` state variable (e.g., `setSeries(dataRes)`).
4. Verify that the `kpis` and `series` state variables are then correctly used in the JSX to display the data.
5. The dashboard should display actual numeric values for KPIs and a populated portfolio trend graph.

**Technical Details:**
- React's `useState` hook manages component-level state.
- The `useEffect` hook is used for side effects, including data fetching.
- The `api` utility function is responsible for making HTTP requests.
- The `AreaChart` component from `recharts` expects an array of data to render the graph.
- The KPI values are rendered using `{}` and `div` elements that currently display static placeholders.

**Related Code Context:**
- `api.js` in `frontend/src/lib` handles API calls.
- The `kpis` object is expected to contain properties like `savings`, `creditScore`, `returns`, `taxLiability`.
- The `series` array is expected to contain objects with `date` and `value` properties for the chart.

**Test Cases:**
1. **Basic Reproduction Test:**
  - Navigate to the dashboard page.
  - **With bug:** Observe that all KPI values are placeholders and the graph is empty.
  - **After fix:** Observe that KPI values are populated with numbers and the graph displays a trend line.
2. **Data Integrity Test:**
  - Verify that the displayed KPI values and graph data match the data returned by the backend API calls (e.g., using browser network inspector).
3. **Empty Data Test:**
  - Simulate an empty response from the backend APIs (e.g., `kpiRes = {}`, `dataRes = []`).
  - **After fix:** The dashboard should gracefully handle empty data, perhaps showing "N/A" or "No data available" without crashing.
4. **Error Handling Test:**
  - Simulate an API error (e.g., network failure, 500 error).
  - **After fix:** The `onToast` function should be called with the error message, and the UI should not crash.

---

...existing code...

### [B17] SGDRegressor Removed from ROI Pipeline

**Type:** Medium  
**Category:** Model Pipeline / Estimator Missing  
**File:** `backend/app/routes/roi.py`  
**Location:** Model pipeline definition  
**Line Numbers:** ~20-30

**Bug Description:**  
The ROI prediction pipeline previously included `SGDRegressor` as the final estimator in a `Pipeline`. However, the SGDRegressor step was removed, leaving only preprocessing or other steps. This causes the pipeline to lack a final estimator, resulting in errors during model fitting and prediction.

**Root Cause:**  
The last step of the pipeline must implement `fit`. Without an estimator, `Pipeline.fit()` raises a `ValueError`.

**Impact:**  
- **Severity:** High  
- **User Impact:** Model training and inference fail with a ValueError.  
- **System Impact:** The ROI prediction feature is broken.

**Expected Symptom:**  
- Attempting to train or predict ROI raises:  
  `ValueError: Last step of Pipeline should implement fit or be the string 'passthrough'.`

**Validation Criteria for Fix:**  
- Restore `SGDRegressor` (or another estimator) as the final step in the pipeline.

**Test Cases:**  
- Attempt to train the pipeline.  
  - **With bug:** ValueError is raised.  
  - **After fix:** Model trains and predicts as expected.

---

### [B18] get_model Generates Corrupted Pickle File

**Type:** Medium  
**Category:** Model Serialization / File Handling  
**File:** `backend/app/routes/roi.py`  
**Location:** `get_model` function  
**Line Numbers:** ~50-60

**Bug Description:**  
The `get_model` function is responsible for serializing and saving the trained ROI model as a pickle file. However, due to improper file handling (e.g., writing in text mode, not using binary mode, or incomplete object serialization), the generated pickle file is corrupted and cannot be loaded later.

**Root Cause:**  
The pickle file is not written in binary mode, or the model object is not fully serialized.

**Impact:**  
- **Severity:** High  
- **User Impact:** Loading the saved model fails with EOFError, UnpicklingError, or "invalid load key" errors.  
- **System Impact:** Model persistence and deployment are broken.

**Expected Symptom:**  
- Loading the saved model with `pickle.load()` or `joblib.load()` fails.

**Validation Criteria for Fix:**  
- Ensure the pickle file is written in binary mode (`'wb'`) and the full model object is serialized.

**Test Cases:**  
- Save and load the model.  
  - **With bug:** Loading fails.  
  - **After fix:** Model loads successfully.

---

### [B19] Logistic Regression Replaced with Linear Regression

**Type:** Medium  
**Category:** Model Type / Classification vs Regression  
**File:** `backend/app/modules/ml_credit.py`  
**Location:** Model definition and training  
**Line Numbers:** ~20-30

**Bug Description:**  
The credit scoring module originally used `LogisticRegression` for binary classification of credit risk. It was mistakenly replaced with `LinearRegression`, which is not suitable for classification tasks. This leads to poor probability calibration and invalid risk predictions.

**Root Cause:**  
`LinearRegression` is used instead of `LogisticRegression`.

**Impact:**  
- **Severity:** High  
- **User Impact:** Model outputs continuous values outside the [0,1] range, and classification accuracy drops.  
- **System Impact:** Probability-based features (e.g., `prob_default`) become unreliable.

**Expected Symptom:**  
- The model outputs values outside [0,1] and performs poorly on classification metrics.

**Validation Criteria for Fix:**  
- Restore `LogisticRegression` as the model for credit risk classification.

**Test Cases:**  
- Train and evaluate the model.  
  - **With bug:** Poor classification performance.  
  - **After fix:** Proper probability outputs and improved accuracy.

---

### [B20] Train/Test Split Misconfiguration

**Type:** Medium  
**Category:** Data Partitioning / Model Training  
**File:** `backend/app/modules/ml_credit.py`  
**Location:** `train_test_split` call  
**Line Numbers:** ~40

**Bug Description:**  
In the `train_test_split` call, the `test_size` parameter was accidentally replaced with `train_size`, causing the majority of data to be used for testing and only a small fraction for training. This results in underfitting and poor model performance.

**Root Cause:**  
`train_size` is used instead of `test_size`.

**Impact:**  
- **Severity:** High  
- **User Impact:** Model training produces low accuracy, and evaluation metrics are unstable.  
- **System Impact:** The training set is much smaller than intended.

**Expected Symptom:**  
- Model performance is poor due to insufficient training data.

**Validation Criteria for Fix:**  
- Use `test_size` to specify the proportion of data for testing.

**Test Cases:**  
- Check the sizes of train and test splits.  
  - **With bug:** Training set is too small.  
  - **After fix:** Proper split and improved performance.

---

### [B21] Missing Gradient Steps in LSTM Training Loop

**Type:** Medium  
**Category:** Neural Network Optimization / Training Loop  
**File:** `backend/app/modules/ml_investments.py`  
**Location:** `train_baselines` function, LSTM training block  
**Line Numbers:** ~80-90

**Bug Description:**  
The training loop for the LSTM model in `train_baselines()` was modified to remove the essential gradient steps: `zero_grad()`, `loss.backward()`, and `optim.step()`. Without these, the model parameters are never updated, and the network does not learn from the data.

**Root Cause:**  
Gradient update steps are missing from the training loop.

**Impact:**  
- **Severity:** High  
- **User Impact:** Training loss remains constant, and model predictions do not improve over epochs.  
- **System Impact:** The LSTM model fails to learn any meaningful patterns.

**Expected Symptom:**  
- The model does not learn; loss does not decrease.

**Validation Criteria for Fix:**  
- Restore the gradient update steps inside the training loop.

**Test Cases:**  
- Train the LSTM model.  
  - **With bug:** Loss remains constant.  
  - **After fix:** Loss decreases and model learns.

---
