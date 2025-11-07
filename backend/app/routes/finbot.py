from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.core.config import settings

router = APIRouter()

class ChatIn(BaseModel):
    message: str

def _llm_call(prompt: str) -> str:
    """
    Simple rule-based FinTech chatbot responses.
    If LLM_API_KEY is set, you can replace this with actual LLM call.
    """
    lower_prompt = prompt.lower()

    # -------- Taxes --------
    if "tax" in lower_prompt:
        return "For Indian taxes, compare new vs old regime. Provide income and deductions; I can estimate your liability."
    
    # -------- Budgeting --------
    if "budget" in lower_prompt or "saving" in lower_prompt:
        return "A simple 50/30/20 split works well: 50% essentials, 30% wants, 20% savings/investments."

    # -------- Loans --------
    if "loan" in lower_prompt or "emi" in lower_prompt:
        return "Check interest rates, tenure, and EMIs. Personal loans usually have higher rates than home or auto loans."

    # -------- Investments --------
    if "mutual fund" in lower_prompt:
        return "Mutual funds pool money from investors to buy a diversified portfolio of stocks and bonds. Check expense ratio before investing."
    
    if "stock" in lower_prompt or "equity" in lower_prompt:
        return "Stocks represent ownership in a company. Diversify your portfolio to reduce risk."

    if "crypto" in lower_prompt or "bitcoin" in lower_prompt:
        return "Cryptocurrencies are volatile digital assets. Only invest what you can afford to lose."

    if "fd" in lower_prompt or "fixed deposit" in lower_prompt:
        return "Fixed deposits are low-risk, interest-bearing deposits with banks. Longer tenure usually gives higher interest."

    if "budget" in lower_prompt or "expense" in lower_prompt:
        return "Track your income and expenses. Categorize as essentials, wants, and savings."

    # -------- Credit Card / Banking --------
    if "credit card" in lower_prompt or "debt" in lower_prompt:
        return "Pay your credit card dues on time to avoid interest. Keep utilization below 30% for good credit score."

    if "bank" in lower_prompt or "account" in lower_prompt:
        return "Ensure KYC is updated and use secure channels for banking transactions."

    # -------- Retirement / Long-term planning --------
    if "retirement" in lower_prompt or "pension" in lower_prompt:
        return "Start investing early in retirement plans like PPF, EPF, or NPS to benefit from compounding."

    # -------- Default fallback --------
    if not settings.LLM_API_KEY:
        return "I'm FinBot. Connect an LLM key in backend .env for richer answers."
    
    # Placeholder for real LLM integration
    return "LLM response placeholder (connect provider to enable)."

@router.post("/chat")
def chat(inp: ChatIn, user = Depends(auth_user)):
    # ❌ BUG: using incorrect response key or missing rendering logic
    # The frontend expects {"message": "..."} but backend returns {"reply": "..."}
    reply = _llm_call(inp.message)
    return {"reply": reply}
