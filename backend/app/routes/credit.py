from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.modules.ml_credit import CreditModel
from app.modules.credit_score import calculate_credits_score

router = APIRouter()
_model = CreditModel(); metrics = _model.train()

class Features(BaseModel):
    income: float
    age: int
    utilization: float
    late_pay: int
    dti: float

@router.get("/metrics")
def model_metrics(user = Depends(auth_user)):
    return metrics

@router.post("/score")
def score(f: Features, user = Depends(auth_user)):
    return _model.score(f.model_dump())

class SimpleFeatures(BaseModel):
    payment_history: float  # 0-100
    credit_utilization: float  # 0-100
    credit_age_years: float  # 0-30
    credit_types_count: float  # 1-10
    recent_inquiries_count: float  # 0-10

@router.post("/simple_score")
def simple_score(feat: SimpleFeatures, user = Depends(auth_user)):
    score = calculate_credits_score(
        payment_history=feat.payment_history,
        credit_utilization=feat.credit_utilization,
        credit_age_years=feat.credit_age_years,
        credit_types_count=feat.credit_types_count,
        recent_inquiries_count=feat.recent_inquiries_count,
    )
    return {"score": scores}
