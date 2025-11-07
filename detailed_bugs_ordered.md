# Detailed Bug Catalog - Fintech Project

This document provides comprehensive information about all 20 intentionally planted bugs in the Fintech project. Each bug entry is designed to enable an automated judge (LLM) to understand the bug, identify its presence in code, and validate whether a contestant's solution correctly fixes it.

---

## Bug List

### [B01] Portfolio Trend Graph Always Shows 1 Month of Data

**Type:** Easy
**Category:** Logic Error
**File:** `backend/app/routes/dashboard.py`
**Location:** `portfolio_series` function
**Line Numbers:** ~30

**Bug Description:**
The portfolio trend graph has multiple time range buttons (1M, 3M, 6M, 1Y) meant to display portfolio data over different time periods. However, due to a logic bug, the code only reads 1 month of data from the CSV file regardless of the selected button. As a result, clicking 3M, 6M, or 1Y shows the same 1-month graph instead of updating based on the selected range.

**Root Cause:**
The `portfolio_series` function accepts a `days` parameter, which is intended to control the number of days of data returned. However, on line 30, the `days` variable is immediately overwritten with a hardcoded value of `30`. This effectively ignores the `days` parameter passed by the frontend, always returning data for only 30 days (approximately 1 month).

**Impact:**
- **Severity:** Medium
- **User Impact:** Users cannot view their portfolio trend over different time ranges, making the time range selection buttons on the frontend non-functional and providing an incomplete view of their financial history.
- **System Impact:** The API does not fulfill its intended purpose of providing flexible time-series data, leading to a poor user experience and potentially incorrect financial analysis by the user.
- **Affected Endpoints:** `GET /api/dashboard/portfolio_series`

**Expected Symptom:**
- Regardless of the `days` parameter provided in the API request (e.g., `?days=90`, `?days=180`), the response always contains approximately 30 days of data.
- On the frontend, clicking "3M", "6M", or "1Y" buttons for the portfolio trend graph shows the exact same 1-month data.

**Validation Criteria for Fix:**
A valid solution must:
1. Remove or comment out the line `days = 30` in the `portfolio_series` function.
2. Ensure that the `days` parameter passed to the function is correctly used to determine the number of historical data points to return.
3. The `df.tail(days)` operation should dynamically use the `days` parameter.
4. The API should return a number of data points corresponding to the `days` parameter provided in the request.

**Technical Details:**
- The `days` parameter is an integer representing the number of days of historical data requested.
- The `df.tail(days)` pandas function is used to select the last `days` rows from the DataFrame.
- The bug is a simple variable reassignment that overrides the intended input.

**Related Code Context:**
- The `days` parameter has a default value of `365`, which is also overridden by the bug.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Make an API call: `GET /api/dashboard/portfolio_series?days=90`.
   - **With bug:** The response `series` array will contain approximately 30 items.
   - **After fix:** The response `series` array will contain approximately 90 items.
2. **Edge Cases:**
   - `GET /api/dashboard/portfolio_series?days=1`: Should return 1 day of data.
   - `GET /api/dashboard/portfolio_series?days=365`: Should return 365 days of data (or all available if less than 365).
   - `GET /api/dashboard/portfolio_series` (no `days` parameter): Should use the default `days=365` and return 365 days of data.
3. **Failing Scenarios:**
   - **With bug:** Any request with `days > 30` will incorrectly return only 30 days of data.
4. **Success Scenarios:**
   - **After fix:** The number of items in the `series` array in the response should match the `days` parameter (up to the total available data).
   - **After fix:** The frontend time range buttons should correctly update the graph based on the selected range.

---
### [B02] All Outgoing Transactions Categorized as "Groceries"

**Type:** Medium
**Category:** Logic Error / ML Integration
**File:** `backend/app/modules/ml_budget.py`
**Location:** `categorize_expenses` function
**Line Numbers:** ~10-11

**Bug Description:**
The `categorize_expenses` function is designed to automatically classify outgoing transactions into different expense types (e.g., Food, Travel, Bills, Shopping) based on their description. However, due to a logic error, the system currently classifies all outgoing transactions into the same single category, specifically "groceries". This causes the expense breakdown on the Budgets page to display incorrect category totals and percentages, as all expenses are lumped into one category regardless of their actual nature.

**Root Cause:**
The `categorize_expenses` function correctly extracts the transaction description and normalizes it. It also initializes a classifier (`clf = build_text_classifier()`). However, within the loop that processes each item, the `category` variable is hardcoded to `"groceries"` on line 11. The `clf` (classifier) is never actually used to predict the category based on the `text` (normalized description).

**Impact:**
- **Severity:** High
- **User Impact:** Users receive inaccurate and unhelpful expense categorization, making it impossible to track their spending across different categories. This undermines the core functionality of the budgeting feature.
- **System Impact:** The machine learning classifier, though built, is never utilized, wasting computational resources and failing to deliver its intended value. The budgeting system provides misleading data.
- **Affected Functionality:** Expense categorization on the Budgets page.

**Expected Symptom:**
- All outgoing transactions, regardless of their description, are assigned the category "groceries".
- The expense breakdown on the Budgets page shows 100% of outgoing expenses under "groceries" (or a very high percentage if there are other hardcoded categories not visible in this snippet), even for transactions clearly related to other categories (e.g., "Uber ride" or "Electricity bill").

**Validation Criteria for Fix:**
A valid solution must:
1. Remove the hardcoded assignment `category = "groceries"`.
2. Integrate the `clf` (text classifier) to predict the category based on the `text` (normalized description) of each transaction.
3. Ensure the predicted category is then assigned to the `category` variable.
4. The function should return a variety of categories based on the input descriptions, not just "groceries".

**Technical Details:**
- The `build_text_classifier()` function (imported from `app.utils.classifier`) is expected to return a trained model capable of text classification.
- The `normalize_text()` function preprocesses the transaction description.
- The `category_pred` key in the result dictionary is intended to store the predicted category.

**Related Code Context:**
- `app.utils.classifier.py` likely contains the implementation of `build_text_classifier` and `normalize_text`.
- The `clf` object is a global variable, suggesting it's loaded once.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Call `categorize_expenses` with a list of diverse transactions (e.g., "Coffee shop", "Electricity bill", "Flight ticket").
   - **With bug:** All returned `category_pred` values will be "groceries".
   - **After fix:** Transactions should be categorized into different, appropriate categories (e.g., "Food", "Bills", "Travel").
2. **Edge Cases:**
   - Empty description: The classifier should handle this gracefully (e.g., assign a "Uncategorized" or "Miscellaneous" category or leave uncategorized).
   - Descriptions with numbers/special characters: `normalize_text` should handle these, and the classifier should still attempt to categorize.
   - Income transactions: These should be skipped by the `if it.get("type", "expense") != "expense": continue` condition.
3. **Failing Scenarios:**
   - **With bug:** Any attempt to get a granular breakdown of expenses will fail due to universal misclassification.
4. **Success Scenarios:**
   - **After fix:** The expense categorization accurately reflects the nature of each transaction.
   - **After fix:** The budgeting UI displays a correct breakdown of expenses by category.

---

### [B03] Credit Score Calculator Returns Static Score

**Type:** Medium
**Category:** Logic Error / Input Handling
**File:** `backend/app/modules/credit_score.py`
**Location:** `calculate_credit_score` function
**Line Numbers:** ~15-17

**Bug Description:**
On the Credits page, the credit score calculator is designed to compute a credit score based on various user inputs like payment history, credit utilization, and credit age. However, the function always returns the same score (650) regardless of the input values provided. This bug stems from a logic error where the input parameters are intentionally ignored, and a fixed, static variable is used for the score calculation. As a result, the displayed credit score remains constant, making the calculator non-functional and misleading.

**Root Cause:**
The `calculate_credit_score` function explicitly ignores all its input parameters (`payment_history`, `credit_utilization`, `credit_age_years`, `credit_types_count`, `recent_inquiries_count`). Instead, it defines a hardcoded `STATIC_SCORE = 650` and always returns this value. The comment `⚠️ BUG: ignore the provided inputs entirely` confirms this intentional misbehavior.

**Impact:**
- **Severity:** High
- **User Impact:** Users cannot get a personalized credit score based on their financial profile. The feature is broken, providing no value and potentially frustrating users who expect dynamic results.
- **System Impact:** The credit score calculation logic is completely bypassed. Any frontend components or downstream systems relying on a dynamic credit score will receive a static value, leading to incorrect behavior or analysis.
- **Affected Functionality:** Credit score calculation on the Credits page.

**Expected Symptom:**
- No matter what values are entered for payment history, credit utilization, etc., the calculated credit score displayed is always 650.
- The credit score does not change even when input sliders or fields are adjusted.

**Validation Criteria for Fix:**
A valid solution must:
1. Remove the hardcoded `STATIC_SCORE` variable and the line `return int(max(300, min(850, STATIC_SCORE)))`.
2. Implement a calculation logic within `calculate_credit_score` that uses the provided input parameters (`payment_history`, `credit_utilization`, `credit_age_years`, `credit_types_count`, `recent_inquiries_count`) to compute a dynamic credit score.
3. The calculated score should vary based on the input parameters.
4. The returned score must be an integer between 300 and 850 (inclusive).

**Technical Details:**
- The function signature correctly defines the expected float input parameters.
- A simple linear combination or a more complex formula using these inputs would be a valid way to calculate a dynamic score.
- The `max(300, min(850, ...))` ensures the score stays within the FICO range.

**Related Code Context:**
- The `_prompt_float` helper function and `if __name__ == "__main__":` block demonstrate how the inputs are collected and passed to `calculate_credit_score` when run as a script.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Call `calculate_credit_score` with different sets of valid input parameters.
   - **With bug:** All calls return 650.
   - **After fix:** Different inputs should yield different scores.
2. **Edge Cases:**
   - Minimum valid inputs (e.g., `payment_history=0`, `credit_utilization=0`, `credit_age_years=0`, `credit_types_count=1`, `recent_inquiries_count=0`): Should yield a low score (e.g., 300-400 range).
   - Maximum valid inputs (e.g., `payment_history=100`, `credit_utilization=0`, `credit_age_years=30`, `credit_types_count=10`, `recent_inquiries_count=0`): Should yield a high score (e.g., 800-850 range).
   - Inputs that would result in a score outside the 300-850 range: The function should still return a score clamped within this range.
3. **Failing Scenarios:**
   - **With bug:** Any attempt to get a personalized credit score will fail due to the static output.
4. **Success Scenarios:**
   - **After fix:** The credit score dynamically updates based on user inputs.
   - **After fix:** The returned score is always an integer between 300 and 850.

---

### [B04] RSI Calculation Instability in Stock Advisor

**Type:** Medium
**Category:** Mathematical Error / Feature Engineering
**File:** `backend/app/modules/new/stock_advisor.py`
**Location:** `compute_rsi` function
**Line Numbers:** ~10-13

**Bug Description:**
The `compute_rsi` function, which is crucial for generating the Relative Strength Index (RSI) feature used by the stock advisor model, contains a mathematical flaw. In scenarios of strong and sustained uptrends, the `loss` (average of downward price changes) over a given period can become zero. When `loss` is zero, the division `gain / (loss + 1e-9)` can still result in a very large number if `gain` is positive, pushing the RSI value to 100. While RSI can reach 100, the issue is that the `1e-9` epsilon is not robust enough to prevent `loss` from being effectively zero in the context of floating-point arithmetic, leading to `rs` becoming `inf` or `NaN` if `loss` is truly zero and `gain` is also zero, or an extremely large number if `gain` is positive. This can lead to an unstable `rs` calculation, which in turn causes the RSI to be inaccurately pinned at 100 or become `NaN`, providing a misleading or corrupted feature to the RandomForestClassifier. This affects the model's ability to generate reliable "Buy/Sell/Hold" recommendations.

**Root Cause:**
The `compute_rsi` function calculates `rs = gain / (loss + 1e-9)`. While adding `1e-9` to `loss` is an attempt to prevent division by zero, if `loss` is genuinely zero (meaning no downward movements in the period), and `gain` is positive, `rs` will become `gain / 1e-9`, which is an extremely large number. This large `rs` value will always push the RSI to 100. Conversely, if both `gain` and `loss` are zero, `rs` becomes `0 / 1e-9 = 0`, leading to an RSI of 100. The standard RSI calculation handles the zero `loss` case by setting `rs` to a very large number (effectively infinity) if `gain` is positive and `loss` is zero, which correctly results in an RSI of 100. However, the current implementation's use of `1e-9` can lead to `NaN` if `gain` is also zero, or an extremely large but finite number that might not be handled robustly by subsequent calculations or the model. A more robust approach is to explicitly check for `loss == 0` and handle it, or ensure `loss` is never exactly zero by adding a small constant *before* the division.

**Impact:**
- **Severity:** Medium
- **User Impact:** The stock advisor provides inaccurate or overly optimistic "BUY" signals (due to RSI being stuck at 100) or fails to provide recommendations due to `NaN` values, leading to poor investment decisions.
- **System Impact:** The feature engineering pipeline produces corrupted or misleading features, degrading the performance and reliability of the RandomForestClassifier. This can lead to model instability and incorrect predictions.
- **Affected Functionality:** Stock recommendation system, `compute_rsi` function.

**Expected Symptom:**
- During strong uptrends, the calculated RSI for a stock might consistently be 100, even if the price action doesn't warrant such an extreme value.
- The `add_indicators` function might produce `NaN` values in the 'RSI' column if both `gain` and `loss` are zero, which would then cause `dropna` to remove data points or the model to fail.
- The stock advisor model's predictions might be skewed, frequently recommending "BUY" when RSI is 100, regardless of other factors.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `compute_rsi` function to correctly handle cases where `loss` is zero.
2. Ensure that if `loss` is zero and `gain` is positive, `rs` effectively becomes infinity, leading to an RSI of 100.
3. Ensure that if both `gain` and `loss` are zero, `rs` is 0, leading to an RSI of 100.
4. Prevent `NaN` values from being generated in the RSI calculation due to division by zero or `0/0` scenarios.
5. The RSI calculation should be robust and align with standard financial RSI formulas.

**Technical Details:**
- RSI formula: `RSI = 100 - (100 / (1 + RS))`, where `RS = Average Gain / Average Loss`.
- If `Average Loss = 0`:
    - If `Average Gain > 0`, then `RS` is undefined (approaches infinity), and `RSI = 100`.
    - If `Average Gain = 0`, then `RS` is `0/0` (undefined), and `RSI = 100` (by convention, or previous period's RSI).
- The current `+ 1e-9` handles division by zero but can lead to `0/1e-9` which is 0, resulting in RSI 100. This is correct for `gain=0, loss=0`. But for `gain>0, loss=0`, it gives `gain/1e-9` which is a large number, also resulting in RSI 100. The issue is more about robustness and clarity.

**Related Code Context:**
- The `add_indicators` function calls `compute_rsi` to add the RSI column to the DataFrame.
- The `train_models` function uses these indicators as features for the RandomForestClassifier.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Create a `pd.Series` with a strong, sustained uptrend where `loss` over a 14-period window becomes 0.
   - Call `compute_rsi` on this series.
   - **With bug:** Observe if RSI is consistently 100 or if `NaN` values appear unexpectedly.
   - **After fix:** RSI should be 100 when `loss` is zero and `gain` is positive, and handle `gain=0, loss=0` robustly.
2. **Edge Cases:**
   - Series with only increasing prices (loss is always 0).
   - Series with only decreasing prices (gain is always 0).
   - Series with constant prices (both gain and loss are 0).
   - Series with mixed price movements.
3. **Failing Scenarios:**
   - **With bug:** RSI values are `NaN` or unexpectedly pinned at 100, leading to incorrect model behavior.
4. **Success Scenarios:**
   - **After fix:** RSI values are calculated correctly and robustly for all price scenarios, including zero `loss`.
   - **After fix:** The stock advisor model receives accurate RSI features.

---

### [B05] XGBoost Model Trained on Naive Time Index Feature

**Type:** Easy
**Category:** Feature Engineering / Model Design
**File:** `backend/app/modules/ml_investments.py`
**Location:** `train_baselines` function, XGBoost training block
**Line Numbers:** ~90-91

**Bug Description:**
The XGBoost model within the `InvestmentPredictor` is intended to forecast future investment returns based on historical data. However, the model is trained using a severely limited feature set: `X_feat = np.arange(len(returns)).reshape(-1, 1)`. This means the model's only input feature is a simple sequential index (0, 1, 2, ...), which represents the passage of time but contains no information about the actual price movements or returns. Consequently, the XGBoost model is merely learning a linear or simple non-linear trend over time, completely ignoring the rich dynamics present in the `returns` data itself. This simplistic approach leads to naive and unreliable predictions that fail to capture any meaningful time-series patterns.

**Root Cause:**
In the `train_baselines` function, within the XGBoost training block, the feature matrix `X_feat` is constructed using `np.arange(len(returns))`. This creates an array `[0, 1, 2, ..., len(returns)-1]`. This array serves as the sole input feature for the XGBoost model. While `y` is correctly set to `returns.values`, the model is effectively trying to predict `returns` based solely on the order of the data points, not their actual values or relationships. This is a fundamental flaw in feature engineering for time-series prediction.

**Impact:**
- **Severity:** High
- **User Impact:** The investment prediction feature, when using XGBoost, provides forecasts that are not based on the actual market behavior or historical price patterns. This leads to highly unreliable and potentially misleading investment advice.
- **System Impact:** The XGBoost model, despite being a powerful algorithm, is severely underutilized and misapplied. It consumes resources to train a model that provides little to no predictive value beyond a simple time trend.
- **Affected Functionality:** XGBoost model in `InvestmentPredictor`, investment prediction feature.

**Expected Symptom:**
- The XGBoost model's predictions will likely show a very smooth, monotonic trend (increasing or decreasing) over time, or simply predict the mean return, without reacting to actual fluctuations in the `returns` data.
- The `next_return` predicted by the XGBoost model will not reflect any complex patterns or recent market movements.
- The model's performance metrics (if evaluated) would be poor, indicating it's not learning from the actual data.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `train_baselines` function to create more informative features for the XGBoost model.
2. These features should be derived from the `returns` series itself, such as lagged returns (e.g., `returns.shift(1)`, `returns.shift(3)`), moving averages, or other relevant technical indicators.
3. The `X_feat` matrix should incorporate these new, meaningful features.
4. The XGBoost model should then be trained on these enhanced features, allowing it to learn from the time-series dynamics.

**Technical Details:**
- XGBoost (Extreme Gradient Boosting) is an ensemble learning method that can capture complex non-linear relationships.
- For time-series data, features often include lagged values of the target variable or other related series, as well as time-based features (e.g., day of week, month).
- `returns = series.pct_change().fillna(0)` correctly calculates percentage changes.

**Related Code Context:**
- The `predict_next` function prioritizes XGBoost if available, making this bug critical for its performance.
- The `series` variable holds the historical closing prices.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Run the `train_baselines` function and then `predict_next`.
   - **With bug:** Observe the `next_return` from the XGBoost model; it will likely be a simple extrapolation of a time trend.
   - **After fix:** The `next_return` should show more responsiveness to recent `returns` data.
2. **Feature Importance Analysis (if possible):**
   - After training, inspect the `feature_importances_` of the XGBoost model.
   - **With bug:** Only the single time-index feature will have importance.
   - **After fix:** Multiple engineered features should show varying levels of importance.
3. **Prediction Comparison:**
   - Compare XGBoost predictions with a simple moving average or a naive "last value" prediction.
   - **With bug:** XGBoost might not significantly outperform these simpler baselines.
   - **After fix:** XGBoost should demonstrate improved predictive power by leveraging the new features.

---

### [B06] Credit Model AUC Scores Swapped on Return

**Type:** Medium
**Category:** Logic Error / Metric Reporting
**File:** `backend/app/modules/ml_credit.py`
**Location:** `CreditModel.train` method
**Line Numbers:** ~45

**Bug Description:**
The `CreditModel.train()` method is responsible for training both a Logistic Regression and a Random Forest classifier for credit default prediction and then evaluating their performance using the Area Under the Receiver Operating Characteristic Curve (AUC) metric. While the AUC scores (`auc_lr` and `auc_rf`) are correctly calculated for each respective model, there is a logic bug where these two values are swapped immediately before being returned. This means that the reported `auc_lr` actually contains the AUC of the Random Forest model, and `auc_rf` contains the AUC of the Logistic Regression model. This leads to misleading evaluation results in any training summary or dashboard display that consumes these metrics, making it appear as if one model performs better than it actually does.

**Root Cause:**
On line 45, the return statement `return {"auc_lr": float(auc_rf), "auc_rf": float(auc_lr)}` explicitly swaps the values of `auc_lr` and `auc_rf` when assigning them to the keys in the returned dictionary. The value calculated for Logistic Regression (`auc_lr`) is assigned to the key `auc_rf`, and vice-versa.

**Impact:**
- **Severity:** High
- **User Impact:** Any user or system relying on these reported AUC scores to compare model performance will receive incorrect information. This could lead to flawed decisions about which model to deploy or trust for credit risk assessment.
- **System Impact:** Downstream systems (e.g., a dashboard displaying model performance, an automated model selection process) will operate on false metrics, potentially leading to suboptimal model choices or misinterpretations of model capabilities.
- **Affected Functionality:** Model evaluation and reporting for Logistic Regression and Random Forest in the credit prediction module.

**Expected Symptom:**
- When `CreditModel.train()` is executed, the returned dictionary will show `auc_lr` as the AUC of the Random Forest model and `auc_rf` as the AUC of the Logistic Regression model.
- If both models have significantly different AUC scores, the reported metrics will clearly be mismatched with their respective model names. For example, if Logistic Regression has an AUC of 0.75 and Random Forest has 0.85, the output will incorrectly report `auc_lr: 0.85, auc_rf: 0.75`.

**Validation Criteria for Fix:**
A valid solution must:
1. Correct the return statement in the `train` method.
2. Ensure that the `auc_lr` value (calculated for Logistic Regression) is assigned to the `auc_lr` key.
3. Ensure that the `auc_rf` value (calculated for Random Forest) is assigned to the `auc_rf` key.
4. The returned dictionary should accurately map each model's AUC score to its corresponding key.

**Technical Details:**
- `roc_auc_score` is a standard metric for binary classification model evaluation.
- `predict_proba(Xte)[:,1]` returns the probability of the positive class, which is required by `roc_auc_score`.
- The bug is a simple variable assignment error in the dictionary construction.

**Related Code Context:**
- The `self.lr.fit(Xtr, ytr)` and `self.rf.fit(Xtr, ytr)` lines train the respective models.
- The `roc_auc_score` calls correctly calculate the individual AUCs.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Instantiate `CreditModel` and call its `train()` method.
   - **With bug:** Observe the returned dictionary and verify that `auc_lr` holds the Random Forest's AUC and `auc_rf` holds the Logistic Regression's AUC.
   - **After fix:** Verify that `auc_lr` holds the Logistic Regression's AUC and `auc_rf` holds the Random Forest's AUC.
2. **Controlled AUC Values:**
   - If possible, manipulate the data or model parameters to ensure Logistic Regression and Random Forest produce distinctly different AUC scores (e.g., 0.6 and 0.9).
   - **With bug:** The reported scores will be swapped.
   - **After fix:** The reported scores will correctly correspond to their model names.
3. **Integration with Dashboard:**
   - If a dashboard displays these metrics, verify that the dashboard shows the correct AUC for each model after the fix.

---
### [B07] New Tax Regime Incorrectly Calculates Tax Below Threshold

**Type:** Easy
**Category:** Business Logic Error / Conditional Logic
**File:** `backend/app/modules/tax_india.py`
**Location:** `slab_tax_new` function
**Line Numbers:** ~20-23

**Bug Description:**
On the Taxes page, the system calculates income tax based on the user's selected regime (Old or New). According to the New Tax Regime rules in India, if the taxable income is less than ₹7,00,000 (not ₹12,00,000 as stated in the original bug description, which is an older threshold or a misunderstanding), no tax should be applied due to a rebate. However, the `slab_tax_new` function incorrectly calculates and displays a tax amount even when the income is below this threshold. The condition in the tax computation logic is incorrectly implemented, failing to account for the full tax rebate available under the new regime for incomes up to ₹7,00,000.

**Root Cause:**
The `slab_tax_new` function defines tax slabs and iterates through them to calculate tax. The first slab starts at `0` with a `0.0` rate. However, the function directly applies slab rates without first checking for the rebate under Section 87A, which effectively makes income up to ₹7,00,000 tax-free under the new regime. The current logic will calculate a non-zero tax for incomes between ₹3,00,000 and ₹7,00,000 (e.g., 5% on income between ₹3,00,000 and ₹6,00,000, and 10% on income between ₹6,00,000 and ₹7,00,000), which should be fully rebated. The bug is that the rebate logic is missing or not applied correctly within this function.

**Impact:**
- **Severity:** High
- **User Impact:** Users opting for the New Tax Regime will see an incorrect, higher tax liability than they actually owe, leading to confusion, distrust in the system, and potentially incorrect financial planning.
- **System Impact:** The tax calculation module provides erroneous results for a significant segment of taxpayers under the new regime, violating a key business rule.
- **Affected Functionality:** New Tax Regime calculation in `compute_tax` via `slab_tax_new`.

**Expected Symptom:**
- For a taxable income of, for example, ₹6,50,000 under the New Tax Regime, the system will calculate a non-zero tax amount.
- The expected tax for income up to ₹7,00,000 under the new regime should be ₹0 due to the rebate.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `slab_tax_new` function (or the `compute_tax` function that calls it) to correctly apply the tax rebate under Section 87A for the New Tax Regime.
2. Ensure that if the taxable income is up to ₹7,00,000, the final tax liability (before cess) is ₹0.
3. For incomes above ₹7,00,000, the tax should be calculated as per the slabs, and the rebate should not apply.
4. The fix should only affect the New Tax Regime calculation and not alter the Old Tax Regime logic.

**Technical Details:**
- The New Tax Regime (FY 2023-24 onwards) provides a rebate under Section 87A, making income up to ₹7,00,000 tax-free.
- The `slab_tax_new` function calculates tax based on predefined slabs.
- The `compute_tax` function calls `slab_tax_new` and then adds cess. The rebate needs to be applied before cess.

**Related Code Context:**
- The `compute_tax` function is the entry point for tax calculation.
- The `slab_tax_old` function handles the Old Tax Regime, which has different rules.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Call `compute_tax(income=650000, use_new=True)`.
   - **With bug:** Returns a non-zero tax amount.
   - **After fix:** Returns a total tax of ₹0.
2. **Edge Cases:**
   - `compute_tax(income=700000, use_new=True)`: Should return ₹0 tax.
   - `compute_tax(income=700001, use_new=True)`: Should return a non-zero tax amount based on the slabs.
   - `compute_tax(income=300000, use_new=True)`: Should return ₹0 tax.
   - `compute_tax(income=1500000, use_new=True)`: Should calculate tax correctly as per slabs (no rebate).
3. **Old Regime Check:**
   - `compute_tax(income=650000, use_new=False)`: Should calculate tax correctly as per old regime rules (no change expected from this bug fix).
4. **Failing Scenarios:**
   - **With bug:** Any income under ₹7,00,000 in the new regime will show tax due.
5. **Success Scenarios:**
   - **After fix:** Incomes up to ₹7,00,000 under the new regime correctly show ₹0 tax.
   - **After fix:** Incomes above ₹7,00,000 under the new regime are taxed correctly according to the slabs.

---

### [B08] Stock Advisor Always Recommends "Sell"

**Type:** Medium
**Category:** Logic Error / Prediction Mapping
**File:** `backend/app/modules/new/stock_advisor.py`
**Location:** `get_recommendation` function
**Line Numbers:** ~60-65

**Bug Description:**
On the Advisor page, the system is designed to provide "Buy", "Sell", or "Hold" recommendations for a selected stock based on a RandomForestClassifier's prediction of whether the stock price will go up. The model correctly outputs a probability of the price going up (`prob`). However, due to a logic bug in the `get_recommendation` function, the decision mapping always results in a "SELL ❌" recommendation, regardless of the actual `prob` value or the model's underlying prediction. This renders the stock advisor feature useless, as it provides a fixed, incorrect recommendation.

**Root Cause:**
The `get_recommendation` function calculates `prob`, which is the probability of the price going up. It then uses a series of `if/elif/else` statements to determine the `decision`. The bug lies in the thresholds used for these conditions:
```python
    if prob > 0.6:
        decision = "BUY ✅"
    elif prob < 0.4:
        decision = "SELL ❌"
    else:
        decision = "HOLD ⚖️"
```
The bug description states "always returns 'Sell'". This implies that the `prob` value is consistently less than 0.4, causing the `elif prob < 0.4` condition to always be met. This consistent low probability of price going up is likely due to an issue in the model's training or the data it was trained on, rather than a direct flaw in the `if/elif/else` structure itself. The model is either poorly trained, or the data it's learning from consistently suggests a low probability of upward movement, leading to a biased output that always triggers the "SELL" condition.

**Impact:**
- **Severity:** High
- **User Impact:** Users receive consistently negative "SELL" recommendations, regardless of the stock or market conditions. This makes the stock advisor feature unreliable and potentially leads to missed opportunities or unnecessary selling.
- **System Impact:** The RandomForestClassifier's output is effectively ignored beyond a simple threshold check that always results in one outcome. The system fails to provide diverse or accurate advice.
- **Affected Functionality:** Stock recommendation system on the Advisor page.

**Expected Symptom:**
- For any stock and any input parameters, the recommendation displayed is consistently "SELL ❌".
- The `Predicted Up Probability` might be consistently low (e.g., below 0.4).

**Validation Criteria for Fix:**
A valid solution must:
1. Investigate the `train_models` function and the data (`stock_data_7stocks.csv`) used for training the RandomForestClassifier.
2. Identify why the `prob` (probability of price going up) is consistently low. This could involve:
    - Ensuring the training data is representative and balanced.
    - Adjusting model parameters or features if the model is underperforming.
3. If the model's output is genuinely always low, then the thresholds (0.6 and 0.4) might need adjustment to reflect a more realistic distribution of `prob` values, or the model itself needs improvement.
4. The fix should result in the `get_recommendation` function returning "BUY", "HOLD", or "SELL" based on the actual predicted probability, not always "SELL".

**Technical Details:**
- `prob = model[0].predict_proba(X_last)[0][1]` correctly extracts the probability of the positive class (price going up).
- The `Target` column in the training data is `1` for price up, `0` for price down.
- The issue is likely upstream in the model's ability to predict `prob > 0.4`.

**Related Code Context:**
- `train_models` function trains the RandomForestClassifier.
- `add_indicators` function prepares features for the model.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Run the `stock_advisor.py` script and enter various stock symbols and buy prices.
   - **With bug:** Observe that the recommendation is always "SELL ❌".
   - **After fix:** The recommendation should vary between "BUY ✅", "HOLD ⚖️", and "SELL ❌" based on the stock and its predicted probability.
2. **Model Output Inspection:**
   - (Requires debugging or logging) Inspect the `prob` variable within `get_recommendation`.
   - **With bug:** `prob` will consistently be less than 0.4.
   - **After fix:** `prob` should show a wider range of values.
3. **Data Analysis:**
   - Analyze `stock_data_7stocks.csv` to see if there's an inherent bias towards downward movements or if the features are not predictive of upward movements.
4. **Failing Scenarios:**
   - **With bug:** The advisor provides no useful "BUY" or "HOLD" recommendations.
5. **Success Scenarios:**
   - **After fix:** The advisor provides varied and data-driven recommendations.

---

### [B09] FinBot Does Not Respond to User Input

**Type:** Medium
**Category:** API Contract Violation / Frontend-Backend Mismatch
**File:** `backend/app/routes/finbot.py`
**Location:** `chat` function
**Line Numbers:** ~60-61

**Bug Description:**
On the FinBot page, users can enter queries into a chatbot interface. The chatbot accepts the user's message and displays it in the chat window, but it fails to generate or display any reply from the bot. This happens because there's a mismatch in the API contract: the backend correctly processes the message and generates a reply using `_llm_call`, but it returns the response with a key (`"reply"`) that the frontend is not expecting. The frontend likely expects a different key (e.g., `"message"`) to render the bot's response, leading to the reply not being displayed.

**Root Cause:**
The `chat` endpoint in `backend/app/routes/finbot.py` returns a dictionary `{"reply": reply}`. The comment on line 60 explicitly states: "The frontend expects `{"message": "..."}` but backend returns `{"reply": "..."}`". This confirms that the key used in the backend's response (`"reply"`) does not match the key the frontend is looking for (`"message"`). As a result, the frontend receives the response but cannot find the content it needs to render.

**Impact:**
- **Severity:** High
- **User Impact:** The chatbot is non-functional from a user perspective, as it never provides responses. This makes the FinBot feature unusable and frustrating.
- **System Impact:** The backend logic for generating chatbot responses works correctly, but the communication contract between the frontend and backend is broken, preventing the display of results.
- **Affected Endpoints:** `POST /api/finbot/chat`

**Expected Symptom:**
- User types a message into the FinBot chat interface.
- The user's message appears in the chat history.
- No response from the FinBot appears in the chat history, leaving a one-sided conversation.
- In network developer tools, the `POST /api/finbot/chat` request succeeds (HTTP 200 OK), and the response body contains `{"reply": "..."}`.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `chat` function in `backend/app/routes/finbot.py`.
2. Change the key in the returned dictionary from `"reply"` to `"message"`.
3. The return statement should become `return {"message": reply}`.
4. The frontend should then correctly display the chatbot's response.

**Technical Details:**
- FastAPI automatically serializes Python dictionaries to JSON responses.
- The `_llm_call` function (or its rule-based placeholder) correctly generates the bot's response string.
- The issue is purely a naming mismatch in the JSON payload.

**Related Code Context:**
- The `ChatIn` Pydantic model defines the incoming message structure.
- The `_llm_call` function contains the logic for generating responses.
- The frontend `FinBot.jsx` (not read yet, but inferred) would be consuming this API.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Send a message to the FinBot (e.g., "What about taxes?").
   - **With bug:** The bot's reply does not appear in the UI.
   - **After fix:** The bot's reply (e.g., "For Indian taxes, compare new vs old regime...") appears in the UI.
2. **Different Queries Test:**
   - Test with various queries that trigger different rule-based responses (e.g., "budget", "loan", "stocks").
   - **After fix:** All responses should appear correctly.
3. **LLM API Key Not Set:**
   - If `settings.LLM_API_KEY` is not set, the fallback message "I'm FinBot. Connect an LLM key..." should be displayed.
4. **Failing Scenarios:**
   - **With bug:** The chatbot appears unresponsive.
5. **Success Scenarios:**
   - **After fix:** The chatbot provides appropriate responses to user queries.

---

### [B10] Synthetic Credit Data Lacks Realistic Feature Correlations

**Type:** Hard
**Category:** Data Generation / Model Training Bias
**File:** `backend/app/modules/ml_credit.py`
**Location:** `_synthetic` function
**Line Numbers:** ~60-64 (feature generation)

**Bug Description:**
The `_synthetic` function in `ml_credit.py` is responsible for generating synthetic credit dataset used for training the Logistic Regression and Random Forest models when a real CSV is not available. However, this function creates the features (`income`, `age`, `utilization`, `late_pay`, `dti`) largely independently of each other. This approach ignores crucial real-world correlations that exist between these financial indicators. For example, `dti` (debt-to-income ratio) is generated uniformly (`rng.uniform(0, 1, n)`) without considering its typical inverse relationship with `income`. A model trained on such an unrealistic, uncorrelated synthetic dataset will perform well on the synthetic validation set but is highly likely to fail or perform poorly when exposed to real-world credit data due to the significant mismatch in data distribution and feature relationships.

**Root Cause:**
The `_synthetic` function generates each feature (`income`, `age`, `utilization`, `late_pay`, `dti`) from its own independent distribution (normal, uniform, poisson). While the `default` target `y` is influenced by a latent probability `z` that combines these features, the features themselves are not correlated in a realistic manner. Specifically, `dti` is generated uniformly, implying no direct relationship with `income` during feature generation, which is a simplification that deviates from real-world financial data where higher income often correlates with lower DTI (or at least a different distribution of DTI). This lack of realistic inter-feature correlation in the input `X` creates a synthetic dataset that does not accurately represent the underlying data-generating process of real credit risk.

**Impact:**
- **Severity:** High
- **User Impact:** A credit risk model trained on this synthetic data will provide inaccurate or misleading probability of default scores for real users. This could lead to incorrect credit decisions (e.g., approving high-risk individuals, denying low-risk individuals).
- **System Impact:** The model exhibits poor generalization capabilities from synthetic to real data. This necessitates constant retraining with real data or makes the synthetic data generation process unreliable for development and testing. The model's performance in a production environment would be significantly lower than its reported performance on synthetic test sets.
- **Affected Functionality:** Credit risk prediction model when trained on synthetic data.

**Expected Symptom:**
- The credit models (Logistic Regression, Random Forest) show good performance (high AUC) on the synthetic test set.
- However, when these models are applied to real-world credit data (if available for testing), their performance metrics (e.g., AUC, accuracy, precision, recall) are significantly lower than expected.
- Feature importance analysis might reveal that the model relies on spurious correlations or fails to capture expected relationships between features.
- Visual inspection of the synthetic data (e.g., scatter plots of `income` vs `dti`) would show a uniform or random distribution where a real dataset would show a clear pattern.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `_synthetic` function to introduce realistic correlations between the generated features.
2. Specifically, the generation of `dti` should be made dependent on `income` (and potentially other factors like `age` or `utilization`). For example, `dti` could be drawn from a distribution whose mean or variance is inversely related to `income`.
3. The goal is to make the synthetic dataset's feature distributions and inter-feature correlations more closely resemble those found in real-world credit data.
4. The model trained on the improved synthetic data should demonstrate better generalization to real-world data (if a real dataset is eventually used for evaluation).

**Technical Details:**
- `np.random.default_rng(self.random_state)` is used for random number generation.
- `rng.normal`, `rng.integers`, `rng.uniform`, `rng.poisson` are used for generating features.
- The latent probability `z` does combine features, but this only affects the target `y`, not the inter-correlation of the input features `X`.

**Related Code Context:**
- The `train` method uses this `_synthetic` data if `large_synthetic_credit_dataset.csv` is not found.
- The `score` method uses the trained models for prediction.

**Test Cases:**
1. **Correlation Analysis (Pre-fix):**
   - Generate a synthetic dataset using the current `_synthetic` function.
   - Calculate the correlation matrix (e.g., `df.corr()`) for the generated features.
   - **With bug:** Observe that correlations between `income` and `dti` (and potentially other pairs) are close to zero or not in line with real-world expectations.
2. **Correlation Analysis (Post-fix):**
   - Generate a synthetic dataset using the modified `_synthetic` function.
   - Calculate the correlation matrix.
   - **After fix:** Observe that `income` and `dti` show a more realistic (e.g., negative) correlation.
3. **Model Performance (Conceptual):**
   - If a real credit dataset were available, a model trained on the fixed synthetic data should perform better on the real data compared to a model trained on the buggy synthetic data.
4. **Visual Inspection:**
   - Plot `income` vs `dti` for both buggy and fixed synthetic datasets to visually confirm the introduction of realistic correlations.

---

### [B11] Watchlist Predictions Are Identical for All Stocks

**Type:** Hard
**Category:** Model Design / Feature Input Mismatch
**File:** `backend/app/modules/trial.py` (and `backend/app/modules/ml_investments.py`)
**Location:** `get_stock_snapshot` function in `trial.py` and `predict_next` method in `InvestmentPredictor` (`ml_investments.py`).
**Line Numbers:** `trial.py`: ~100, `ml_investments.py`: ~100-115

**Bug Description:**
On the Watchlist page (simulated by `trial.py`), LSTM and XGBoost models are used to predict stock trends. However, a fundamental design flaw causes the system to return the exact same prediction for all stocks in the watchlist, regardless of their individual historical data or current market conditions. This bug is intentionally unsolvable through a simple code fix; participants must identify the conceptual problem, which lies in the model's design and its interaction with stock-specific data.

**Root Cause:**
The `InvestmentPredictor` class (from `ml_investments.py`) is designed to predict a generic "next period return" based on a single, internal historical series (`self.series`). This `self.series` is either loaded from a single CSV file (`HistoricalData_1761328678783.csv`) or generated as a synthetic sine wave. The `predict_next()` method of `InvestmentPredictor` does not accept any stock-specific input (like the `symbol` or its recent price data).

In `trial.py`, a single instance of `InvestmentPredictor` (`predictor`) is created and trained *once* globally using this generic series. Subsequently, when `get_stock_snapshot(symbol)` is called for each stock in the watchlist, it calls `predictor.predict_next()`. Since `predictor.predict_next()` always operates on the same internal series and does not receive any information about the `symbol` it's supposed to be predicting for, it will always produce the same `pred_return` and `pred_model` for every stock.

**Impact:**
- **Severity:** Critical
- **User Impact:** The watchlist prediction feature is completely misleading. Users receive identical, generic predictions for all stocks, making the feature useless for individual stock analysis and potentially leading to poor investment decisions.
- **System Impact:** The entire stock prediction mechanism is fundamentally flawed. The models, despite being potentially powerful, are applied in a way that ignores the very data they are supposed to analyze (individual stock performance).
- **Affected Functionality:** Stock trend prediction for all stocks in the watchlist.

**Expected Symptom:**
- When `trial.py` is run and multiple stocks are added to the watchlist, the `Pred(Next)` column in the output will show the exact same numerical value for every stock.
- The `Model` column will also show the same model (e.g., "xgboost" or "lstm" or "naive") for all stocks.
- The predictions do not change based on the specific stock's symbol or its fetched real-time data.

**Validation Criteria for Fix (Identification of Conceptual Problem):**
A valid solution must:
1. Identify that the `InvestmentPredictor` is designed for a single, generic time series, not for multiple individual stock time series.
2. Explain that the `predict_next()` method lacks the necessary input parameters (e.g., `symbol`, `historical_data_for_symbol`) to make stock-specific predictions.
3. Conclude that to provide unique predictions per stock, the `InvestmentPredictor` (or a similar model) would need to be:
    - Either instantiated and trained *per stock* with its specific historical data.
    - Or modified to accept stock-specific historical data as input to its `predict_next()` method.
    - Or the `train_baselines` method would need to be adapted to train models for multiple stocks, perhaps by taking a dictionary of series.
4. The core problem is the mismatch between a generic predictor and the requirement for stock-specific predictions.

**Technical Details:**
- The `InvestmentPredictor` in `ml_investments.py` is a single-series predictor.
- `trial.py` uses a single global instance of this predictor.
- The `get_stock_snapshot` function in `trial.py` fetches real-time data for each `symbol` but this `symbol`-specific data is not passed to `predictor.predict_next()`.

**Related Code Context:**
- `ml_investments.py` defines the `InvestmentPredictor` class.
- `trial.py` demonstrates its usage in a watchlist context.

**Test Cases (for identifying the conceptual problem):**
1. **Run `trial.py` with multiple stocks:**
   - Add "AAPL" and "GOOG" to the watchlist.
   - **With bug:** Observe that the `Pred(Next)` values for AAPL and GOOG are identical.
2. **Inspect `predict_next` signature:**
   - Examine the `predict_next` method in `ml_investments.py`.
   - **With bug:** Note that it does not accept any `symbol` or stock-specific data.
3. **Trace Data Flow:**
   - Follow the data flow from `get_stock_data` (which receives `symbol`) to `predictor.predict_next()`.
   - **With bug:** Observe that the `symbol` information is lost before reaching the prediction logic.

---

### [B12] Watchlist Allows Adding Non-Existent Stocks

**Type:** Medium
**Category:** Input Validation / Data Integrity
**File:** `backend/app/modules/trial.py`
**Location:** `main` function (user input loop) and `get_stock_data` function.
**Line Numbers:** `main`: ~200-205, `get_stock_data`: ~150-151 (error handling)

**Bug Description:**
On the Watchlist page (simulated by `trial.py`), users can add stock symbols to their watchlist. However, due to a lack of validation, the system allows any arbitrary string to be added as a stock symbol, even if that symbol does not correspond to an actual, tradable stock in the market API (AlphaVantage) or any internal database. When data is fetched for these non-existent symbols, the system falls back to generating synthetic or mock data. This results in the watchlist displaying invalid stocks with fabricated data, which can cause misleading charts, predictions, and overall inaccurate portfolio information.

**Root Cause:**
1. **Lack of Validation on Add:** In the `main` function's input loop, when a user enters a symbol, it is directly added to the `watchlist` list (`watchlist.append(user_input)`) without any check against a valid list of symbols or a real-time API.
2. **Graceful Fallback to Mock Data:** The `get_stock_snapshot` function (called by `get_stock_data`) is designed with a fallback mechanism. If the AlphaVantage API key is not configured, or if the API call fails (e.g., for an invalid symbol), it gracefully falls back to `get_mock_price(s)` and generates other mock metrics. This behavior, while robust for API failures, masks the issue of invalid input by providing plausible-looking but fake data.
3. **Incomplete Error Handling:** While `get_stock_data` has a `try-except KeyError` block, it only catches errors *after* attempting to parse the JSON response. If AlphaVantage returns an error for an invalid symbol (e.g., "Invalid API call" or "Symbol not found") that doesn't raise a `KeyError` but rather returns an empty or malformed `Global Quote` or `Time Series` object, the system might still fall through to mock data or return a generic "Could not fetch data" without explicitly validating the symbol's existence.

**Impact:**
- **Severity:** Medium
- **User Impact:** Users can inadvertently add non-existent stocks to their watchlist, leading to a false sense of portfolio diversity or performance. The displayed data for these stocks is entirely fabricated, making any analysis based on it unreliable and potentially causing financial misjudgments.
- **System Impact:** The system processes requests for invalid symbols, potentially wasting API calls (if AlphaVantage is configured) and generating mock data unnecessarily. The integrity of the watchlist data is compromised.
- **Affected Functionality:** Stock watchlist management, real-time stock data display, and predictions.

**Expected Symptom:**
- User adds a clearly fake stock symbol (e.g., "XYZ123") to the watchlist.
- The symbol appears in the watchlist output.
- The price, %change, SMA20, RSI14, and prediction for "XYZ123" are displayed, but these values are synthetic and do not reflect any real market data.
- No explicit error message is shown to the user indicating that "XYZ123" is an invalid symbol.

**Validation Criteria for Fix:**
A valid solution must:
1. Implement a validation step when a user attempts to add a stock to the `watchlist`.
2. This validation should check if the `symbol` is a valid, existing stock. This could involve:
    - Making a preliminary API call to AlphaVantage (or a similar service) to verify the symbol's existence.
    - Checking against a predefined list of valid symbols (if available).
3. If the symbol is invalid, the system should inform the user and prevent it from being added to the `watchlist`.
4. The system should only add and display data for valid stock symbols.

**Technical Details:**
- The `get_price` and `get_stock_snapshot` functions are the primary points of interaction with external stock data (AlphaVantage or mock).
- The `normalize_symbol` function ensures consistent symbol formatting.
- The `KeyError` handling in `get_stock_data` is too broad and doesn't distinguish between API errors and invalid symbols.

**Related Code Context:**
- `settings.ALPHAVANTAGE_API_KEY` controls whether live data is fetched.
- The `get_mock_price` function provides the synthetic data.

**Test Cases:**
1. **Add Valid Symbol:**
   - Add a known valid symbol (e.g., "AAPL", "GOOG").
   - **After fix:** The symbol should be added, and real (or mock if API key is missing) data should be displayed.
2. **Add Invalid Symbol:**
   - Add a clearly invalid symbol (e.g., "NONEXISTENTSTOCK", "123XYZ").
   - **With bug:** The symbol is added, and mock data is displayed.
   - **After fix:** The system should reject the symbol, inform the user it's invalid, and not add it to the watchlist.
3. **API Key Missing/Invalid:**
   - Run the script without `ALPHAVANTAGE_API_KEY` or with an invalid one.
   - **After fix:** Valid symbols should still be added and display mock data (as per existing fallback), but invalid symbols should still be rejected.
4. **Error Message Check:**
   - Verify that the error message for an invalid symbol is clear and informative to the user.

---

### [B13] Custom ROI Regressor Fails Due to Flawed Gradient Descent

**Type:** Hard
**Category:** Mathematical Error / Optimization Algorithm
**File:** `backend/app/modules/new2/roi_predict_gd.py`
**Location:** `CustomRegressor.fit` method
**Line Numbers:** ~30-32

**Bug Description:**
The `roi_predict_gd.py` module features a custom regressor (`CustomRegressor`) intended to predict Return on Investment (ROI) using a custom gradient descent implementation. The goal was to experiment with a user-defined mathematical loss function, specifically a Mean Absolute Percentage Error (MAPE)-like loss. However, the implementation of the gradient descent algorithm within the `fit` method contains severe mathematical and logical flaws. The calculated `grad` (`np.sign(preds - y)`) does not correspond to the derivative of the actual loss function being minimized. Furthermore, the weight update rule (`self.weights -= self.lr * grad.mean()`) incorrectly applies the *mean* of this flawed gradient to *all* model weights uniformly, instead of updating each weight by its specific partial derivative. These fundamental errors prevent the model from learning effectively, causing the optimization process to behave unpredictably, leading to either a complete failure to converge or the generation of nonsensical ROI predictions despite valid inputs.

**Root Cause:**
The `CustomRegressor.fit` method suffers from two critical errors in its custom gradient descent implementation:
1. **Incorrect Gradient Calculation:** The loss function is defined as `loss = np.mean(np.abs((y - preds) / (y + 1e-5)))`, which is a variant of Mean Absolute Percentage Error (MAPE). The gradient calculated is `grad = np.sign(preds - y)`. This `grad` is the derivative of Mean Absolute Error (MAE) with respect to `preds`, not the derivative of the MAPE-like loss. The correct gradient for MAPE is significantly more complex and involves `y` in the denominator.
2. **Improper Weight Update:** The weight update rule `self.weights -= self.lr * grad.mean()` is fundamentally incorrect. In gradient descent, each weight (`w_j`) should be updated by its corresponding partial derivative (`∂Loss/∂w_j`). By taking the `mean()` of the `grad` (which is already incorrect) and applying this single scalar value to all elements of `self.weights`, the algorithm fails to learn the individual contribution of each feature to the prediction. This uniform update prevents proper optimization and convergence.

These combined errors mean the `CustomRegressor` is not performing a valid gradient descent optimization for its stated loss function.

**Impact:**
- **Severity:** Critical
- **User Impact:** The ROI prediction model is completely unreliable, providing predictions that are either random, static, or wildly inaccurate. This makes the feature useless for financial decision-making and can lead to significant financial misjudgments.
- **System Impact:** The `CustomRegressor` is effectively broken as an optimization algorithm. It cannot learn from data, rendering the entire ROI prediction pipeline non-functional. Resources are consumed in a training process that yields no meaningful model.
- **Affected Functionality:** ROI prediction, `CustomRegressor` training and prediction.

**Expected Symptom:**
- The printed "Test MAE" and "R² Score" after training will be very poor (high MAE, low or negative R²), indicating that the model has not learned anything useful.
- Interactive predictions will show little to no sensitivity to changes in input features, or will produce values that are clearly outside a reasonable range for ROI.
- The model's weights (`self.weights`) will likely not converge to stable values, or will converge to values that do not minimize the loss function.
- The training process might appear to run, but the model's predictive power will be negligible.

**Validation Criteria for Fix:**
A valid solution must:
1. **Derive and Implement Correct Gradient:** The `grad` calculation must be replaced with the mathematically correct partial derivatives of the chosen MAPE-like loss function with respect to each weight. This will involve applying the chain rule.
2. **Correct Weight Update Rule:** The weight update rule must be modified to update each weight `w_j` using its corresponding gradient component `∂Loss/∂w_j`. This typically involves a matrix multiplication or element-wise operation, not a scalar mean.
3. The `CustomRegressor` should demonstrate significantly improved performance metrics (lower MAE, higher R²) on the test set after the fix.
4. The model should converge to a stable and accurate set of weights that effectively minimize the loss function.

**Technical Details:**
- The loss function is `L = (1/N) * Σ |(y_i - preds_i) / (y_i + ε)|`.
- The derivative `∂L/∂w_j` would involve `∂preds_i/∂w_j = X_ij` (where `X_ij` is the `j`-th feature of the `i`-th sample).
- The `np.hstack([np.ones((X.shape[0], 1)), X])` correctly adds a bias term.

**Related Code Context:**
- The `preprocessor` correctly handles numerical scaling and one-hot encoding.
- The `Pipeline` correctly integrates the preprocessing and regression steps.

**Test Cases:**
1. **Performance Metrics Check:**
   - Run the script.
   - **With bug:** Observe the printed "Test MAE" and "R² Score" values; they will be indicative of a non-learning model.
   - **After fix:** The MAE should significantly decrease, and the R² score should increase, demonstrating effective learning.
2. **Interactive Prediction Sensitivity:**
   - Provide varying inputs for interactive prediction (e.g., high principal, low fees vs. low principal, high fees).
   - **With bug:** Predictions will be largely unresponsive or nonsensical.
   - **After fix:** Predictions should change logically in response to input variations, reflecting learned relationships.
3. **Convergence Observation:**
   - (Requires internal inspection or logging) Monitor `self.weights` over `epochs`.
   - **With bug:** Weights will likely not show a clear convergence pattern.
   - **After fix:** Weights should gradually adjust and stabilize.
4. **Gradient Calculation Verification:**
   - (Requires manual derivation or numerical approximation) Verify that the implemented gradient calculation matches the mathematical derivative of the chosen loss function.

---

### [B14] Login Allows Blank or Null Passwords

**Type:** Medium
**Category:** Security Vulnerability / Input Validation
**File:** `backend/app/routes/auth.py`
**Location:** `login` function
**Line Numbers:** ~34-36

**Bug Description:**
The login functionality in the application allows users to successfully authenticate and gain access even if the password field is left blank or provided as a null string. This critical security vulnerability arises because the authentication logic does not explicitly validate whether a non-empty password has been provided before attempting to verify it against the stored hashed password. As a result, unauthorized logins may occur without proper password verification, compromising user accounts and system security.

**Root Cause:**
The `LoginIn` Pydantic model defines the `password` field as `str`, which by default allows empty strings. The `login` function then proceeds to call `verify_password(data.password, u.hashed_password)`. The `verify_password` function (from `app.core.security`) likely handles an empty string as a valid input for comparison, and if a user was registered with an empty password (which is also a potential bug in `register`), or if the `verify_password` function has a flaw, it could return `True` for an empty password. The primary issue is the lack of explicit validation in `LoginIn` to ensure the password is not empty.

**Impact:**
- **Severity:** Critical
- **User Impact:** User accounts are vulnerable to unauthorized access. An attacker could potentially log in to any account if they know the email address and the password was set to blank or null, or if the `verify_password` function has a flaw with empty strings.
- **System Impact:** Compromises the security and integrity of the entire application. Leads to unauthorized access, data breaches, and loss of user trust.
- **Affected Functionality:** User login and authentication.

**Expected Symptom:**
- A user can successfully log in by providing a valid email address and leaving the password field empty or entering a blank string.
- The system grants an `access_token` for such a login attempt.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `LoginIn` Pydantic model in `backend/app/routes/auth.py`.
2. Add a validation constraint to the `password` field to ensure it is not an empty string (e.g., using `MinLength(1)` or `Field(..., min_length=1)`).
3. This validation should cause FastAPI to return a `422 Unprocessable Entity` error if an empty password is provided.
4. (Optional but recommended) Ensure the `RegisterIn` model also prevents registration with empty passwords.
5. (Optional but recommended) Review `app.core.security.verify_password` to ensure it robustly handles empty or null password inputs.

**Technical Details:**
- Pydantic models are used for request body validation.
- `EmailStr` ensures valid email format.
- `verify_password` compares a plaintext password with a hashed password.
- `HTTPException(401, "Invalid credentials")` is the standard response for failed authentication.

**Related Code Context:**
- `app.core.security.py` contains `hash_password` and `verify_password`.
- `app.models.user.py` defines the `User` model.

**Test Cases:**
1. **Login with Empty Password:**
   - Attempt to log in with a valid email and an empty string for the password.
   - **With bug:** Login succeeds, and a token is returned.
   - **After fix:** Login fails with a `422 Unprocessable Entity` error, indicating that the password field cannot be empty.
2. **Login with Null Password (if API allows):**
   - Attempt to log in with a valid email and a `null` value for the password (if the API allows `null` in the request body).
   - **With bug:** Login might succeed depending on `verify_password` implementation.
   - **After fix:** Login fails with a `422 Unprocessable Entity` error.
3. **Login with Valid Password:**
   - Attempt to log in with a valid email and a correct, non-empty password.
   - **After fix:** Login should still succeed.
4. **Failing Scenarios:**
   - **With bug:** Unauthorized access is possible with empty passwords.
5. **Success Scenarios:**
   - **After fix:** Empty passwords are rejected at the validation layer, preventing unauthorized access.

---

### [B15] New Tax Regime Standard Deduction is Incorrect

**Type:** Medium
**Category:** Business Logic Error / Hardcoded Value
**File:** `backend/app/modules/tax_india.py`
**Location:** `compute_tax` function
**Line Numbers:** ~30

**Bug Description:**
The `compute_tax` function is responsible for calculating income tax based on the user's income and selected tax regime. For the New Tax Regime, a standard deduction is applied to the income before calculating the tax. However, due to a hardcoded error, the function incorrectly uses ₹75,000 as the standard deduction for the new regime. As per the Finance Act 2023, the correct standard deduction for salaried individuals and pensioners under the New Tax Regime is ₹50,000. This factual error in the business logic leads to incorrect (lower) taxable income and consequently incorrect tax calculations for users who choose the new regime.

**Root Cause:**
In the `compute_tax` function, the line `std_ded = 50000.0 if not use_new else 75000.0` assigns the standard deduction. When `use_new` is `True` (indicating the New Tax Regime), `std_ded` is incorrectly set to `75000.0`. This value should be `50000.0` to align with the current tax laws.

**Impact:**
- **Severity:** High
- **User Impact:** Users opting for the New Tax Regime will have their taxable income underestimated by ₹25,000, leading to a lower calculated tax liability than what they actually owe. This can result in underpayment of taxes and potential legal issues for the user.
- **System Impact:** The tax calculation module provides factually incorrect results for the New Tax Regime, violating a critical business rule and legal compliance.
- **Affected Functionality:** Tax calculation for the New Tax Regime.

**Expected Symptom:**
- When calculating tax under the New Tax Regime, the taxable income will be ₹25,000 lower than it should be, and the final tax amount will also be lower than the legally mandated amount.
- For an income of, say, ₹10,00,000 under the New Regime, the system will apply a deduction of ₹75,000 instead of ₹50,000.

**Validation Criteria for Fix:**
A valid solution must:
1. Modify the `compute_tax` function in `backend/app/modules/tax_india.py`.
2. Change the hardcoded standard deduction for the New Tax Regime from `75000.0` to `50000.0`.
3. Ensure that the standard deduction for the Old Tax Regime remains `50000.0` (if applicable, or its correct value).
4. The tax calculation for the New Tax Regime should then correctly reflect the ₹50,000 standard deduction.

**Technical Details:**
- The `std_ded` variable holds the standard deduction amount.
- The conditional assignment `50000.0 if not use_new else 75000.0` is the point of error.
- The `taxable` income is derived by subtracting `std_ded`.

**Related Code Context:**
- The `slab_tax_new` and `slab_tax_old` functions define the tax slab rates for each regime.
- The `compute_tax` function orchestrates the overall tax calculation.

**Test Cases:**
1. **Basic Reproduction Test:**
   - Call `compute_tax(income=1000000, use_new=True)`.
   - **With bug:** The `taxable_income` in the returned `TaxResult` will be `1000000 - 75000 = 925000`.
   - **After fix:** The `taxable_income` should be `1000000 - 50000 = 950000`.
2. **Old Regime Check:**
   - Call `compute_tax(income=1000000, use_new=False)`.
   - **After fix:** The standard deduction for the old regime should remain unchanged (e.g., `50000.0`).
3. **Various Income Levels:**
   - Test with different income levels under the New Tax Regime to ensure the correct standard deduction is consistently applied.
4. **Failing Scenarios:**
   - **With bug:** Tax calculations for the New Tax Regime are consistently lower than they should be.
5. **Success Scenarios:**
   - **After fix:** Tax calculations for the New Tax Regime accurately reflect the ₹50,000 standard deduction.

---
### [B16] SGDRegressor Removed from ROI Pipeline

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

### [B17] get_model Generates Corrupted Pickle File

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

### [B18] Logistic Regression Replaced with Linear Regression

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

### [B19] Train/Test Split Misconfiguration

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

### [B20] Missing Gradient Steps in LSTM Training Loop

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
## Summary

This catalog documents 20 intentionally planted bugs across various difficulty levels in the Fintech project. Each bug entry provides comprehensive detail to facilitate understanding, identification, and validation of fixes.

---

## Validation Notes for Automated Judging

When evaluating contestant solutions:

1. **Code Location:** Verify the fix is in the correct file and function.
2. **Change Scope:** Ensure the fix addresses only the specific bug, not other issues.
3. **Functionality:** Verify the fix doesn't break existing functionality.
4. **Edge Cases:** Check that edge cases are handled appropriately.
5. **Best Practices:** Ensure the solution follows Python/FastAPI/React best practices.
6. **No Over-Fixing:** Solutions should fix the bug, not refactor unrelated code.
7. **HTTP Semantics:** For HTTP-related bugs, verify correct status codes and headers.
8. **Data Integrity:** For database bugs, ensure transactions are handled correctly.
9. **API Contract:** For API bugs, verify the contract is maintained.
10. **Performance:** For performance bugs, verify the improvement is achieved.

---

## Notes

- All bugs are marked with comments like `# BUG [BXX]` in the source code (if applicable).
- Bugs can be activated by uncommenting buggy code variants (if present).
- The working code remains intact for reference.
- Some bugs may have dependencies or interactions with others.
- Contestants should fix bugs without breaking existing functionality.
