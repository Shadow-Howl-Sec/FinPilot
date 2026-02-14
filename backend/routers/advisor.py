from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Expense
from ..services.advisor_service import FinancialAdvisor
from ..services.audit_service import AuditService

router = APIRouter(prefix="/advisor", tags=["advisor"])

@router.get("/audit")
async def get_financial_audit(user_id: int, db: Session = Depends(get_db)):
    """Perform comprehensive financial audit"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    audit = AuditService(db)
    integrity = audit.perform_integrity_sweep(user_id)
    anomalies = audit.detect_anomalies(user_id)
    compliance = audit.check_compliance(user_id)
    
    return {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "integrity": integrity,
        "anomalies": anomalies,
        "compliance": compliance
    }

@router.get("/recommendations")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get AI-powered financial recommendations"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    recommendations = advisor.get_recommendations(user_id)
    return {"user_id": user_id, "recommendations": recommendations}

@router.get("/analysis")
async def get_spending_analysis(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Analyze spending patterns"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    analysis = advisor.analyze_spending_patterns(user_id, days=days)
    return {"user_id": user_id, "analysis": analysis}

@router.get("/forecast")
async def get_spending_forecast(user_id: int, db: Session = Depends(get_db)):
    """Get predicted monthly spending"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    forecast = advisor.predict_monthly_spending(user_id)
    return {"user_id": user_id, "forecast": forecast}

@router.get("/dashboard")
async def get_dashboard_summary(user_id: int, db: Session = Depends(get_db)):
    """Get complete dashboard summary"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    
    savings_history = []
    current_date = datetime.utcnow()
    global_limit = user.monthly_budget_limit or 0
    
    for i in range(3):
        target_year = current_date.year
        target_month = current_date.month - i
        if target_month <= 0:
            target_month += 12
            target_year -= 1
            
        m_start = datetime(target_year, target_month, 1)
        if target_month == 12:
             m_end = datetime(target_year + 1, 1, 1)
        else:
             m_end = datetime(target_year, target_month + 1, 1)

        m_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= m_start,
            Expense.date < m_end
        ).all()
        
        m_total = sum(e.amount for e in m_expenses)
        m_savings = global_limit - m_total
        
        month_name = m_start.strftime("%b %Y")
        savings_history.append({
            "month": month_name,
            "savings": m_savings,
            "expenses": m_total,
            "status": "Surplus" if m_savings >= 0 else "Deficit"
        })

    return {
        "user_id": user_id,
        "user_name": user.full_name or user.username,
        "analysis": advisor.analyze_spending_patterns(user_id, days=30),
        "forecast": advisor.predict_monthly_spending(user_id),
        "recommendations": advisor.get_recommendations(user_id),
        "financial_summary": {
             "global_budget_limit": global_limit,
             "total_spent_month": advisor.analyze_spending_patterns(user_id, days=30).get("total_spent", 0),
             "net_savings": global_limit - advisor.analyze_spending_patterns(user_id, days=30).get("total_spent", 0),
             "savings_history": savings_history,
             "overall_savings": (global_limit * max(1, int((datetime.utcnow() - user.created_at).days / 30))) - (db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id).scalar() or 0)
        }
    }
