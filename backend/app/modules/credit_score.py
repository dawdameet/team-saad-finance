"""
Simple Credit Score Calculator module.

Expose a reusable function `calculate_credit_score(...)` returning an integer score
in the 300-850 range. A small CLI is provided for manual runs.

-- BUGGY VERSION: calculate_credit_score ignores inputs and returns a constant score.
"""

from typing import Optional


def calculate_credit_score(
    payment_history: float,
    credit_utilization: float,
    credit_age_years: float,
    credit_types_count: float,
    recent_inquiries_count: float,
) -> int:
    """Compute a simple credit score (300-850).

    NOTE: This buggy version intentionally ignores the input parameters and
    returns a fixed score every time.
    """
    # ⚠️ BUG: ignore the provided inputs entirely
    # The function always returns this fixed score regardless of arguments.
    STATIC_SCORE = 650

    # Ensure returned value respects 300-850 bounds (redundant here, but kept)
    return int(max(300, min(850, STATIC_SCORE)))


def _prompt_float(prompt: str, min_val: float, max_val: float) -> float:
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Enter a number.")


if __name__ == "__main__":
    print("=== Simple Credit Score Calculator (BUGGY) ===")
    ph = _prompt_float("Payment History (0-100%) : ", 0, 100)
    util = _prompt_float("Credit Utilization (0-100%) : ", 0, 100)
    age = _prompt_float("Average Age of Credit Accounts (in years) : ", 0, 30)
    types_ = _prompt_float("Number of Different Credit Types (1-10) : ", 1, 10)
    inq = _prompt_float("Number of Recent Credit Inquiries (0-10) : ", 0, 10)

    score = calculate_credit_score(
        payment_history=ph,
        credit_utilization=util,
        credit_age_years=age,
        credit_types_count=types_,
        recent_inquiries_count=inq,
    )
    print(f"\nEstimated Credit Score: {int(score)} / 850")
