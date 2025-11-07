#!/bin/bash
# This script creates all issues and labels for the finance project.
# Make sure you are logged in to the GitHub CLI: `gh auth login`

set -e

# --- CONFIGURATION ---
REPO="dawdameet/team-saad-finance"
# ---------------------

echo "Targeting repository: $REPO"
echo "This script will create 23 labels and 20 issues."
echo "Press Enter to continue, or Ctrl+C to cancel."
read

# === PART 1: CREATE LABELS ===
# We use --force to make this script idempotent.
# If the label already exists, it will just be updated.

echo "Creating labels..."

# Difficulty Labels
gh label create "difficulty-easy" -R $REPO --color "0E8A16" --description "Easy Difficulty (10 pts)" --force
gh label create "difficulty-medium" -R $REPO --color "D9B41E" --description "Medium Difficulty (20 pts)" --force
gh label create "difficulty-hard" -R $REPO --color "B60205" --description "Hard Difficulty (30 pts)" --force

# Bug ID Labels
gh label create "bug-1" -R $REPO --color "d73a4a" --description "Bug ID 1" --force
gh label create "bug-2" -R $REPO --color "d73a4a" --description "Bug ID 2" --force
gh label create "bug-3" -R $REPO --color "d73a4a" --description "Bug ID 3" --force
gh label create "bug-4" -R $REPO --color "d73a4a" --description "Bug ID 4" --force
gh label create "bug-5" -R $REPO --color "d73a4a" --description "Bug ID 5" --force
gh label create "bug-6" -R $REPO --color "d73a4a" --description "Bug ID 6" --force
gh label create "bug-7" -R $REPO --color "d73a4a" --description "Bug ID 7" --force
gh label create "bug-8" -R $REPO --color "d73a4a" --description "Bug ID 8" --force
gh label create "bug-9" -R $REPO --color "d73a4a" --description "Bug ID 9" --force
gh label create "bug-10" -R $REPO --color "d73a4a" --description "Bug ID 10" --force
gh label create "bug-11" -R $REPO --color "d73a4a" --description "Bug ID 11" --force
gh label create "bug-12" -R $REPO --color "d73a4a" --description "Bug ID 12" --force
gh label create "bug-13" -R $REPO --color "d73a4a" --description "Bug ID 13" --force
gh label create "bug-14" -R $REPO --color "d73a4a" --description "Bug ID 14" --force
gh label create "bug-15" -R $REPO --color "d73a4a" --description "Bug ID 15" --force
gh label create "bug-16" -R $REPO --color "d73a4a" --description "Bug ID 16" --force
gh label create "bug-17" -R $REPO --color "d73a4a" --description "Bug ID 17" --force
gh label create "bug-18" -R $REPO --color "d73a4a" --description "Bug ID 18" --force
gh label create "bug-19" -R $REPO --color "d73a4a" --description "Bug ID 19" --force
gh label create "bug-20" -R $REPO --color "d73a4a" --description "Bug ID 20" --force

echo "Label creation complete."

# === PART 2: CREATE ISSUES ===
# We use --body-file - and a heredoc (<<EOF) to safely pass the
# multi-line markdown body with quotes and code blocks.

echo "Creating issues..."

echo "Creating issue 1..."
gh issue create -R $REPO \
  -t "Bug 1: Portfolio Trend Graph Always Shows 1 Month of Data" \
  --label "bug-1,difficulty-easy" \
  --body-file - <<EOF
## Bug Description
The portfolio trend graph has buttons for 1M, 3M, 6M, and 1Y time ranges, but it always displays only 1 month of data regardless of the selection. This is because the backend function accepts a \`days\` parameter but immediately overwrites it with a hardcoded value of 30, making the time range selection non-functional and providing users with an incomplete view of their financial history.

## Current Behavior
Regardless of the \`days\` parameter sent to the API (e.g., 90, 180, 365), the response always contains approximately 30 days of data. The frontend graph does not change when different time ranges are selected.

## Expected Behavior
The API should return a number of data points corresponding to the \`days\` parameter provided in the request. The frontend time range buttons should correctly update the graph to show data for 1M, 3M, 6M, or 1Y.

## Files Affected
\`backend/app/routes/dashboard.py\`

## Difficulty: EASY **Points: 10**

## Reproduction Steps
1. Make an API call to \`/api/dashboard/portfolio_series?days=90\`. 2. Observe that the response contains only about 30 items. 3. Locate the \`portfolio_series\` function in the specified file. 4. Find the line where the \`days\` variable is hardcoded to 30. 5. Remove or comment out this line to allow the function to use the \`days\` parameter passed in the request.

## Solution
Remove the line \`days = 30\` inside the \`portfolio_series\` function.

## Hints
Look for a variable being reassigned to a hardcoded value right after the function starts.

---
*Bug ID: 1 **Status**: UNRESOLVED*
EOF

echo "Creating issue 2..."
gh issue create -R $REPO \
  -t "Bug 2: All Outgoing Transactions Categorized as 'Groceries'" \
  --label "bug-2,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The system is designed to use a machine learning model to automatically categorize user expenses. However, a logic error causes all outgoing transactions to be classified as 'groceries', regardless of their description. This makes the expense breakdown on the Budgets page inaccurate and useless for tracking spending, as the ML classifier is built but never actually used to predict the category.

## Current Behavior
All outgoing transactions, like 'Uber ride' or 'Electricity bill', are assigned the category 'groceries'. The Budgets page shows 100% of expenses under a single category.

## Expected Behavior
Transactions should be classified into different, appropriate categories (e.g., 'Food', 'Bills', 'Travel') based on their description by using the ML classifier. The budget UI should display a correct breakdown of expenses.

## Files Affected
\`backend/app/modules/ml_budget.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Call the \`categorize_expenses\` function with a list of diverse transaction descriptions. 2. Observe that every transaction's predicted category is 'groceries'. 3. Examine the \`categorize_expenses\` function. 4. Notice that the \`category\` variable is hardcoded. 5. Replace the hardcoded assignment with a call to the classifier's predict method, like \`category = clf.predict([text])[0]\`.

## Solution
Replace the hardcoded assignment \`category = "groceries"\` with a call to \`clf.predict()\` using the transaction text.

## Hints
The machine learning classifier \`clf\` is initialized but never used within the loop.

---
*Bug ID: 2 **Status**: UNRESOLVED*
EOF

echo "Creating issue 3..."
gh issue create -R $REPO \
  -t "Bug 3: Credit Score Calculator Returns Static Score" \
  --label "bug-3,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The credit score calculator on the Credits page is supposed to compute a score based on user inputs like payment history and credit utilization. However, it always returns a static score of 650, completely ignoring all user-provided data. This makes the calculator non-functional and misleading for users trying to estimate their credit score.

## Current Behavior
No matter what values are entered into the credit score calculator, the displayed score is always 650.

## Expected Behavior
The credit score should be calculated dynamically based on the user's inputs. Different inputs should result in different credit scores within the 300-850 range.

## Files Affected
\`backend/app/modules/credit_score.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Call the \`calculate_credit_score\` function with different sets of valid inputs. 2. Observe that the function always returns 650. 3. Examine the function's implementation. 4. Find the hardcoded \`STATIC_SCORE = 650\` variable. 5. Remove the static variable and the line returning it. 6. Implement a new calculation logic that uses the input parameters to compute a dynamic score.

## Solution
Remove the hardcoded \`STATIC_SCORE\` and implement a formula that uses the function's input parameters to calculate a dynamic score.

## Hints
The function ignores its inputs and returns a hardcoded variable named \`STATIC_SCORE\`.

---
*Bug ID: 3 **Status**: UNRESOLVED*
EOF

echo "Creating issue 4..."
gh issue create -R $REPO \
  -t "Bug 4: RSI Calculation Instability in Stock Advisor" \
  --label "bug-4,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The function to compute the Relative Strength Index (RSI) is mathematically unstable. During strong, sustained uptrends, the average loss can become zero. The current implementation's attempt to prevent division by zero is not robust and can lead to the RSI value becoming 'NaN' (Not a Number) or being inaccurately pinned at 100. This provides corrupted or misleading feature data to the stock advisor model.

## Current Behavior
During strong uptrends, the RSI calculation may produce 'NaN' values or be stuck at 100, which can cause the stock advisor model to fail or make incorrect predictions.

## Expected Behavior
The RSI calculation should robustly handle cases where the average loss is zero, correctly returning an RSI of 100 without generating 'NaN' values.

## Files Affected
\`backend/app/modules/new/stock_advisor.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Create a pandas Series of prices that only increase, ensuring the average loss will be zero. 2. Call the \`compute_rsi\` function with this series. 3. Observe if the result is 'NaN' or unstable. 4. Examine the line where \`rs\` is calculated with \`rs = gain / (loss + 1e-9)\`. 5. Implement a more robust check, such as an if-else block, to handle the case where \`loss\` is exactly zero before performing the division.

## Solution
Modify the \`compute_rsi\` function to explicitly check if \`loss\` is zero and handle that case before performing the division to calculate \`rs\`.

## Hints
A small epsilon is used to prevent division by zero, but a direct conditional check for zero loss is more robust.

---
*Bug ID: 4 **Status**: UNRESOLVED*
EOF

echo "Creating issue 5..."
gh issue create -R $REPO \
  -t "Bug 5: XGBoost Model Trained on Naive Time Index Feature" \
  --label "bug-5,difficulty-easy" \
  --body-file - <<EOF
## Bug Description
The XGBoost model for investment prediction is being trained with a single, uninformative feature: a simple time index (0, 1, 2, 3...). It completely ignores the actual historical price or returns data, meaning it's only learning a simple trend over time. This leads to naive and unreliable predictions that fail to capture any real market patterns.

## Current Behavior
The XGBoost model's predictions are a very smooth trend and do not react to actual market fluctuations because its only input feature is \`[0, 1, 2, ..., N-1]\`.

## Expected Behavior
The model should be trained on meaningful features derived from the historical returns data, such as lagged returns, moving averages, or other technical indicators, to learn actual time-series patterns.

## Files Affected
\`backend/app/modules/ml_investments.py\`

## Difficulty: EASY **Points: 10**

## Reproduction Steps
1. Run the \`train_baselines\` function. 2. Examine the feature matrix \`X_feat\` created for the XGBoost model. 3. Notice it's created using \`np.arange(len(returns))\`. 4. Understand that this is not a useful feature for time-series forecasting. 5. Replace this line with code that creates meaningful features, such as lagged values of the \`returns\` series (e.g., using \`returns.shift(1)\`).

## Solution
Replace the \`X_feat\` creation from \`np.arange(len(returns))\` to a set of features derived from the \`returns\` data, like lagged values.

## Hints
The input features \`X_feat\` for the model are generated with \`np.arange\`, which doesn't contain any information about the actual returns.

---
*Bug ID: 5 **Status**: UNRESOLVED*
EOF

echo "Creating issue 6..."
gh issue create -R $REPO \
  -t "Bug 6: Credit Model AUC Scores Swapped on Return" \
  --label "bug-6,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The credit model training function correctly calculates the AUC performance metric for a Logistic Regression model (\`auc_lr\`) and a Random Forest model (\`auc_rf\`). However, when returning these scores in a dictionary, the values are swapped. This results in misleading reports where the Logistic Regression score is reported for the Random Forest model and vice versa.

## Current Behavior
The training function returns a dictionary where the value for the \`auc_lr\` key is actually the Random Forest's AUC, and the value for \`auc_rf\` is the Logistic Regression's AUC.

## Expected Behavior
The returned dictionary should accurately report the AUC score for each model, with the \`auc_lr\` key corresponding to the Logistic Regression's AUC and the \`auc_rf\` key corresponding to the Random Forest's AUC.

## Files Affected
\`backend/app/modules/ml_credit.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Call the \`CreditModel.train()\` method. 2. Observe the returned dictionary of AUC scores. 3. Notice that the values are swapped relative to their keys (e.g., \`auc_lr\` might have a higher value typical of Random Forest). 4. Examine the \`return\` statement of the \`train\` method. 5. Identify that the variables \`auc_lr\` and \`auc_rf\` are assigned to the wrong keys in the dictionary. 6. Correct the assignments in the return statement.

## Solution
Correct the return statement to \`return {"auc_lr": float(auc_lr), "auc_rf": float(auc_rf)}\`.

## Hints
Check the dictionary construction in the \`return\` statement. The values are assigned to the wrong keys.

---
*Bug ID: 6 **Status**: UNRESOLVED*
EOF

echo "Creating issue 7..."
gh issue create -R $REPO \
  -t "Bug 7: New Tax Regime Incorrectly Calculates Tax Below Threshold" \
  --label "bug-7,difficulty-easy" \
  --body-file - <<EOF
## Bug Description
Under India's New Tax Regime, income up to ₹7,00,000 should be effectively tax-free due to a rebate. However, the system incorrectly calculates and applies tax for incomes below this threshold (but above ₹3,00,000). This is because the calculation logic fails to incorporate the rebate rule, leading to incorrect tax liability for users.

## Current Behavior
The system calculates a non-zero tax amount for incomes between ₹3,00,000 and ₹7,00,000 under the New Tax Regime.

## Expected Behavior
For any taxable income up to ₹7,00,000 under the New Tax Regime, the calculated tax liability should be ₹0.

## Files Affected
\`backend/app/modules/tax_india.py\`

## Difficulty: EASY **Points: 10**

## Reproduction Steps
1. Call \`compute_tax(income=650000, use_new=True)\`. 2. Observe that it returns a non-zero tax amount. 3. Examine the \`slab_tax_new\` function. 4. Notice that it directly applies tax slabs without checking for the rebate. 5. Add a condition at the beginning of the function to check if the income is below or equal to ₹7,00,000 and return 0 if it is.

## Solution
In the \`slab_tax_new\` function, add an initial check: if income is <= 700000, return 0 tax.

## Hints
The logic is missing a check for the tax rebate available for incomes up to ₹7,00,000 under the new regime.

---
*Bug ID: 7 **Status**: UNRESOLVED*
EOF

echo "Creating issue 8..."
gh issue create -R $REPO \
  -t "Bug 8: Stock Advisor Always Recommends 'Sell'" \
  --label "bug-8,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The stock advisor is designed to provide 'Buy', 'Sell', or 'Hold' recommendations based on a model's predicted probability of the stock price going up. However, it consistently recommends 'SELL ❌' for every stock. This is because the underlying model is poorly trained or the data is biased, causing the predicted probability to always be very low (below the 0.4 threshold for a 'Sell' recommendation).

## Current Behavior
The recommendation for any stock is always 'SELL ❌' because the model's predicted probability of the price going up is consistently below 0.4.

## Expected Behavior
The stock advisor should provide varied recommendations ('BUY', 'HOLD', 'SELL') based on the model's output, which should reflect the stock's actual potential.

## Files Affected
\`backend/app/modules/new/stock_advisor.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Run the stock advisor for any stock. 2. Observe the recommendation is always 'SELL ❌'. 3. Add a print statement to check the value of the \`prob\` variable inside the \`get_recommendation\` function. 4. Notice it is always less than 0.4. 5. Conclude the issue is upstream in the model training (\`train_models\`) or the features/data used, which needs to be fixed to produce more reasonable probabilities.

## Solution
The model needs to be retrained or the feature engineering in \`add_indicators\` needs to be improved to produce more accurate and varied probabilities.

## Hints
The issue isn't in the if/elif/else logic itself, but in the \`prob\` value being fed into it. The model is consistently predicting a low probability.

---
*Bug ID: 8 **Status**: UNRESOLVED*
EOF

echo "Creating issue 9..."
gh issue create -R $REPO \
  -t "Bug 9: FinBot Does Not Respond to User Input" \
  --label "bug-9,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The FinBot chatbot UI correctly sends the user's message to the backend, and the backend correctly generates a reply. However, the reply never appears in the chat window. This is due to a simple API contract mismatch: the backend returns the reply in a JSON object with the key 'reply', but the frontend is expecting the key to be 'message'.

## Current Behavior
The user's message appears in the chat, but the FinBot never responds. A successful network request can be seen, but the UI doesn't display the result.

## Expected Behavior
When a user sends a message, the FinBot's generated reply should appear in the chat interface.

## Files Affected
\`backend/app/routes/finbot.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Type a message in the FinBot UI. 2. Observe no response is displayed. 3. Check the browser's network tools for the API call to \`/api/finbot/chat\`. 4. Examine the JSON response body and see \`{"reply": "..."}\`. 5. Look at the \`chat\` function in the backend code. 6. Find the \`return\` statement and change the key in the returned dictionary from \`"reply"\` to \`"message"\`.

## Solution
In the \`chat\` function's return statement, change the dictionary key from \`"reply"\` to \`"message"\`.

## Hints
There is a mismatch between the JSON key the backend sends (\`reply\`) and the key the frontend expects (\`message\`).

---
*Bug ID: 9 **Status**: UNRESOLVED*
EOF

echo "Creating issue 10..."
gh issue create -R $REPO \
  -t "Bug 10: Synthetic Credit Data Lacks Realistic Feature Correlations" \
  --label "bug-10,difficulty-hard" \
  --body-file - <<EOF
## Bug Description
The function that generates synthetic data for training the credit risk model creates features independently of each other. This ignores real-world correlations, such as the relationship between income and debt-to-income ratio (DTI). A model trained on this unrealistic data will likely perform poorly on real-world data because it hasn't learned these crucial inter-feature relationships.

## Current Behavior
The synthetic features are uncorrelated. A scatter plot of \`income\` vs. \`dti\` would show a random cloud, whereas in reality, a pattern is expected.

## Expected Behavior
The synthetic data generation should introduce realistic correlations between features. For example, DTI should be generated in a way that is inversely related to income.

## Files Affected
\`backend/app/modules/ml_credit.py\`

## Difficulty: HARD **Points: 30**

## Reproduction Steps
1. Generate a synthetic dataset using the \`_synthetic\` function. 2. Calculate a correlation matrix for the features. 3. Observe that the correlation between \`income\` and \`dti\` is near zero. 4. Modify the \`_synthetic\` function. 5. Change the line that generates \`dti\` to make it dependent on the already-generated \`income\` values, creating a negative correlation.

## Solution
Modify the \`_synthetic\` function to make the generation of the \`dti\` feature dependent on the \`income\` feature to create a realistic correlation.

## Hints
Each feature is generated from an independent random distribution. \`dti\` should be calculated based on \`income\`.

---
*Bug ID: 10 **Status**: UNRESOLVED*
EOF

echo "Creating issue 11..."
gh issue create -R $REPO \
  -t "Bug 11: Watchlist Predictions Are Identical for All Stocks" \
  --label "bug-11,difficulty-hard" \
  --body-file - <<EOF
## Bug Description
The stock prediction feature on the Watchlist page shows the exact same predicted return for every single stock, regardless of which company it is. This is a fundamental design flaw: a single, generic prediction model is trained once and then asked to make predictions without ever receiving any stock-specific data. The predictor always uses its same internal data, so its output never changes.

## Current Behavior
All stocks in the watchlist show the exact same value in the 'Pred(Next)' column because the prediction function is not given any information about which stock to predict for.

## Expected Behavior
Each stock in the watchlist should have its own unique prediction based on its individual historical data.

## Files Affected
\`backend/app/modules/trial.py\` (and \`ml_investments.py\`)

## Difficulty: HARD **Points: 30**

## Reproduction Steps
1. Add multiple different stocks (e.g., 'AAPL', 'GOOG') to the watchlist. 2. Observe that their predicted returns are identical. 3. Examine the \`get_stock_snapshot\` function in \`trial.py\` and see that it calls \`predictor.predict_next()\`. 4. Examine the \`predict_next\` method in \`ml_investments.py\`. 5. Notice it takes no arguments and uses an internal \`self.series\`. 6. Conclude the design must be changed to pass stock-specific data to the predictor.

## Solution
This is a conceptual bug. The fix requires refactoring the \`InvestmentPredictor\` class to be trained on or predict with stock-specific data for each call.

## Hints
The \`predictor.predict_next()\` function doesn't accept a stock symbol or its data as an argument. It always predicts on the same internal data it was trained on.

---
*Bug ID: 11 **Status**: UNRESOLVED*
EOF

echo "Creating issue 12..."
gh issue create -R $REPO \
  -t "Bug 12: Watchlist Allows Adding Non-Existent Stocks" \
  --label "bug-12,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The watchlist allows a user to add any string as a stock symbol, even if it's a fake one like 'XYZ123'. Instead of rejecting the invalid symbol, the system falls back to generating mock data for it and displays it in the watchlist as if it were a real stock. This compromises data integrity and can mislead the user.

## Current Behavior
Any string can be added to the watchlist. If the symbol is invalid, fake data is generated and displayed for it without any warning to the user.

## Expected Behavior
The system should validate a stock symbol when the user tries to add it. If the symbol is invalid, it should be rejected with an error message and not added to the watchlist.

## Files Affected
\`backend/app/modules/trial.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Run the script and try to add a fake stock symbol like 'XYZ123'. 2. Observe that the fake symbol is added to the list and displayed with mock data. 3. Examine the user input loop in the \`main\` function. 4. Notice that user input is appended directly to the \`watchlist\` without validation. 5. Add a validation step before appending, which could involve an API call or checking against a predefined list of valid symbols.

## Solution
Implement a validation check on the user-provided stock symbol before adding it to the watchlist. If invalid, reject it and inform the user.

## Hints
User input is added to the watchlist without being checked for validity first. The mock data fallback hides the error.

---
*Bug ID: 12 **Status**: UNRESOLVED*
EOF

echo "Creating issue 13..."
gh issue create -R $REPO \
  -t "Bug 13: Custom ROI Regressor Fails Due to Flawed Gradient Descent" \
  --label "bug-13,difficulty-hard" \
  --body-file - <<EOF
## Bug Description
A custom regression model designed to predict ROI using gradient descent is mathematically broken. The calculated gradient does not match the derivative of the model's loss function, and the weight update rule incorrectly applies a single average gradient value to all weights. This prevents the model from learning, resulting in nonsensical predictions and extremely poor performance metrics.

## Current Behavior
The model's R² score is very low or negative, and its predictions are inaccurate because the gradient descent algorithm is implemented with fundamental mathematical errors.

## Expected Behavior
The gradient descent implementation should use the correct mathematical derivative of the loss function and update each model weight individually based on its partial derivative, allowing the model to learn from the data and make accurate predictions.

## Files Affected
\`backend/app/modules/new2/roi_predict_gd.py\`

## Difficulty: HARD **Points: 30**

## Reproduction Steps
1. Run the script and observe the very poor 'Test MAE' and 'R² Score'. 2. Examine the \`fit\` method of the \`CustomRegressor\` class. 3. Compare the calculated \`grad\` with the mathematical derivative of the \`loss\` function and find they don't match. 4. Analyze the weight update rule \`self.weights -= self.lr * grad.mean()\` and realize it's incorrect. 5. Correct both the gradient calculation and the weight update rule to follow the proper gradient descent algorithm.

## Solution
Correct the gradient calculation in the \`fit\` method to match the loss function's derivative and change the weight update rule to update each weight individually.

## Hints
The gradient \`grad\` is wrong, and the weight update uses \`grad.mean()\`, which applies the same update to all weights.

---
*Bug ID: 13 **Status**: UNRESOLVED*
EOF

echo "Creating issue 14..."
gh issue create -R $REPO \
  -t "Bug 14: Login Allows Blank or Null Passwords" \
  --label "bug-14,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
A critical security vulnerability exists where a user can log in successfully by providing a valid email but leaving the password field completely blank. The backend authentication logic fails to validate that a non-empty password was provided, potentially allowing unauthorized access to user accounts.

## Current Behavior
A user can log in with a valid email and an empty string for the password, and the system grants an access token.

## Expected Behavior
The login endpoint should reject any authentication attempt where the password field is empty, returning a validation error (e.g., 422 Unprocessable Entity).

## Files Affected
\`backend/app/routes/auth.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Attempt to make a login API call with a valid user's email and an empty string (\`""\`) as the password. 2. Observe that the login succeeds and a token is returned. 3. Examine the \`LoginIn\` Pydantic model in the specified file. 4. Notice the \`password\` field lacks validation for minimum length. 5. Add a validation constraint, such as \`Field(..., min_length=1)\`, to the password field.

## Solution
Add a validation constraint to the \`password\` field in the \`LoginIn\` Pydantic model, such as \`min_length=1\`.

## Hints
The \`LoginIn\` Pydantic model for the request body does not have a validator to prevent empty strings for the password.

---
*Bug ID: 14 **Status**: UNRESOLVED*
EOF

echo "Creating issue 15..."
gh issue create -R $REPO \
  -t "Bug 15: New Tax Regime Standard Deduction is Incorrect" \
  --label "bug-15,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The tax calculator incorrectly applies a standard deduction of ₹75,000 for the New Tax Regime. According to the Finance Act 2023, the correct standard deduction for salaried individuals under the new regime is ₹50,000. This error causes the system to under-calculate the user's tax liability.

## Current Behavior
The \`compute_tax\` function uses a hardcoded value of ₹75,000 for the standard deduction under the new regime, resulting in an incorrect tax calculation.

## Expected Behavior
The system should apply the correct standard deduction of ₹50,000 when calculating tax for a user under the New Tax Regime.

## Files Affected
\`backend/app/modules/tax_india.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Call \`compute_tax(income=1000000, use_new=True)\`. 2. Observe the resulting \`taxable_income\` is 925,000 (1M - 75k). 3. Examine the \`compute_tax\` function. 4. Find the line that assigns the standard deduction: \`std_ded = 50000.0 if not use_new else 75000.0\`. 5. Change the incorrect \`75000.0\` value to the correct \`50000.0\`.

## Solution
In the \`compute_tax\` function, change the hardcoded standard deduction for the new regime from \`75000.0\` to \`50000.0\`.

## Hints
A ternary operator in the \`compute_tax\` function has a wrong hardcoded value for the new tax regime's standard deduction.

---
*Bug ID: 15 **Status**: UNRESOLVED*
EOF

echo "Creating issue 16..."
gh issue create -R $REPO \
  -t "Bug 16: SGDRegressor Removed from ROI Pipeline" \
  --label "bug-16,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The ROI prediction feature is broken because the machine learning pipeline is incomplete. The final step, which should be an estimator like \`SGDRegressor\`, has been removed. A scikit-learn pipeline must end with an estimator, and its absence causes the program to crash with a \`ValueError\` during training or prediction.

## Current Behavior
Attempting to train the ROI model raises a \`ValueError: Last step of Pipeline should implement fit...\` because the pipeline lacks a final estimator.

## Expected Behavior
The pipeline should be a complete sequence of steps ending with a regression model (estimator), allowing it to be trained and used for predictions successfully.

## Files Affected
\`backend/app/routes/roi.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Attempt to train the ROI model. 2. Observe that a \`ValueError\` is raised. 3. Examine the definition of the scikit-learn \`Pipeline\` object in the specified file. 4. Notice that it contains preprocessing steps but no final model/estimator. 5. Add a final step to the pipeline, such as \`('regressor', SGDRegressor())\`.

## Solution
Add \`SGDRegressor\` or another suitable regressor as the final step in the scikit-learn \`Pipeline\` definition.

## Hints
A scikit-learn Pipeline object is missing its final step, which must be an estimator (a model).

---
*Bug ID: 16 **Status**: UNRESOLVED*
EOF

echo "Creating issue 17..."
gh issue create -R $REPO \
  -t "Bug 17: get_model Generates Corrupted Pickle File" \
  --label "bug-17,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The function responsible for saving the trained ROI model to a file creates a corrupted pickle file. This is because the file is not opened in binary write mode ('wb'). When another part of the system tries to load this corrupted file, it fails with an unpickling error, breaking the model persistence functionality.

## Current Behavior
Loading the saved model file fails with an error like \`UnpicklingError\` or \`EOFError\` because it was not written in binary mode.

## Expected Behavior
The model should be saved to a valid pickle file that can be successfully loaded later for inference.

## Files Affected
\`backend/app/routes/roi.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Train and save the model using the \`get_model\` function. 2. Attempt to load the generated pickle file using \`pickle.load()\`. 3. Observe that loading fails with an error. 4. Examine the \`get_model\` function. 5. Find the \`open()\` call used for writing the file. 6. Identify that it's missing the binary mode specifier 'b'. 7. Change the file mode from \`'w'\` to \`'wb'\`.

## Solution
Change the file open mode from \`'w'\` to \`'wb'\` in the \`get_model\` function when saving the pickle file.

## Hints
When writing pickle files, the file must be opened in binary write mode.

---
*Bug ID: 17 **Status**: UNRESOLVED*
EOF

echo "Creating issue 18..."
gh issue create -R $REPO \
  -t "Bug 18: Logistic Regression Replaced with Linear Regression" \
  --label "bug-18,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The credit scoring module is intended to solve a binary classification problem (default vs. no default) and should use a model like \`LogisticRegression\`. However, it was mistakenly replaced with \`LinearRegression\`, which is a regression model. This is incorrect for the task, leading to poor predictions and outputs that are not probabilities.

## Current Behavior
A \`LinearRegression\` model is being used for a classification task, resulting in poor performance and model outputs that can be outside the [0,1] range.

## Expected Behavior
The credit risk model should be a \`LogisticRegression\` classifier, which outputs probabilities between 0 and 1 and is suitable for binary classification.

## Files Affected
\`backend/app/modules/ml_credit.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Train and evaluate the credit risk model. 2. Observe poor classification metrics (e.g., AUC) and that predicted values are not probabilities. 3. Examine the model instantiation line in the specified file. 4. Identify that \`LinearRegression\` is being used. 5. Replace \`LinearRegression()\` with \`LogisticRegression()\`.

## Solution
Replace the \`LinearRegression\` model instance with \`LogisticRegression\`.

## Hints
A regression model (\`LinearRegression\`) is being used for a classification problem.

---
*Bug ID: 18 **Status**: UNRESOLVED*
EOF

echo "Creating issue 19..."
gh issue create -R $REPO \
  -t "Bug 19: Train/Test Split Misconfiguration" \
  --label "bug-19,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
When splitting data for training and testing the credit model, the \`train_size\` parameter was used instead of \`test_size\`. This misconfiguration causes the data to be split incorrectly, allocating a very small portion for training and a large portion for testing. This leads to model underfitting and poor, unstable performance.

## Current Behavior
The model performs poorly because it is trained on a very small fraction of the data due to a parameter mix-up in the \`train_test_split\` function call.

## Expected Behavior
The data should be split correctly, with a larger portion (e.g., 80%) used for training the model and a smaller portion (e.g., 20%) for testing.

## Files Affected
\`backend/app/modules/ml_credit.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Check the size of the training and testing datasets after the split. 2. Notice that the training set is much smaller than the testing set. 3. Examine the \`train_test_split\` function call. 4. Identify that the \`train_size\` parameter is used where \`test_size\` was intended. 5. Correct the parameter name from \`train_size\` to \`test_size\`.

## Solution
In the \`train_test_split\` call, change the parameter \`train_size\` to \`test_size\`.

## Hints
Look at the parameters passed to \`train_test_split\`. The wrong parameter name is being used to specify the split ratio.

---
*Bug ID: 19 **Status**: UNRESOLVED*
EOF

echo "Creating issue 20..."
gh issue create -R $REPO \
  -t "Bug 20: Missing Gradient Steps in LSTM Training Loop" \
  --label "bug-20,difficulty-medium" \
  --body-file - <<EOF
## Bug Description
The training loop for the LSTM investment model is broken because the essential PyTorch steps for learning have been removed. The calls to \`zero_grad()\`, \`loss.backward()\`, and \`optim.step()\` are missing. Without these, the model's weights are never updated, and it does not learn from the data, causing the training loss to remain constant.

## Current Behavior
The LSTM model does not learn, and its training loss does not decrease. The model's predictions are no better than a random guess.

## Expected Behavior
The training loop should include all necessary steps to update model weights: zeroing gradients, performing backpropagation, and taking an optimizer step. The training loss should decrease over epochs.

## Files Affected
\`backend/app/modules/ml_investments.py\`

## Difficulty: MEDIUM **Points: 20**

## Reproduction Steps
1. Run the LSTM training process. 2. Observe that the printed loss value does not decrease with each epoch. 3. Examine the LSTM training loop within the \`train_baselines\` function. 4. Notice that the lines for updating the model's gradients are missing. 5. Add \`optim.zero_grad()\`, \`loss.backward()\`, and \`optim.step()\` in the correct places within the loop.

## Solution
Restore the \`optim.zero_grad()\`, \`loss.backward()\`, and \`optim.step()\` calls inside the LSTM training loop.

## Hints
The core PyTorch training steps (\`zero_grad\`, \`backward\`, \`step\`) are missing from the training loop.

---
*Bug ID: 20 **Status**: UNRESOLVED*
EOF

echo "All issues created successfully."