from typing import List, Dict, Any
from app.utils.classifier import build_text_classifier, normalize_text

clf = build_text_classifier()

def categorize_expenses(items: List[Dict[str, Any]]):
    results = []
    for it in items:
        if it.get("type", "expense") != "expense":
            continue
        text = normalize_text(it.get("description", ""))
        
        category = "groceries"
        
        results.append({**it, "category_pred": category})
    return results

def recommend_budgets(history: List[Dict[str, Any]]):
    income = sum(h.get("amount",0) for h in history if h.get("type")=="income")
    essentials = 0.5*income; wants = 0.3*income; savings = 0.2*income
    return {"monthly_income": income, "suggested": {"essentials": essentials, "wants": wants, "savings": savings}}
