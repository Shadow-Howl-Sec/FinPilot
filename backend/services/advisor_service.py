from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from ..models import Expense, Budget

def get_indian_fiscal_year_dates():
    """Get Indian Fiscal Year start and end dates"""
    curr = datetime.utcnow()
    year = curr.year
    if curr.month >= 4:
        start = datetime(year, 4, 1)
        end = datetime(year + 1, 3, 31, 23, 59, 59)
    else:
        start = datetime(year - 1, 4, 1)
        end = datetime(year, 3, 31, 23, 59, 59)
    return start, end

class FinancialAdvisor:
    """AI-powered financial advisor"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_spending_patterns(self, user_id: int, days: int = 30) -> dict:
        """Analyze spending patterns"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date
        ).all()

        if not expenses:
            return {
                "status": "no_data",
                "message": "No expenses found in the specified period"
            }

        category_analysis = {}
        total_spent = 0

        for expense in expenses:
            category = expense.category.value
            if category not in category_analysis:
                category_analysis[category] = {"count": 0, "total": 0}
            
            category_analysis[category]["count"] += 1
            category_analysis[category]["total"] += expense.amount
            total_spent += expense.amount

        return {
            "period_days": days,
            "total_spent": total_spent,
            "average_daily_spend": total_spent / days if days > 0 else 0,
            "category_breakdown": category_analysis,
            "expense_count": len(expenses)
        }

    def get_recommendations(self, user_id: int) -> List[str]:
        """Generate CA-style financial analysis and recommendations"""
        recommendations = []
        
        fy_start, fy_end = get_indian_fiscal_year_dates()
        
        fy_expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= fy_start,
            Expense.date <= fy_end
        ).all()

        current_month_expenses = [e for e in fy_expenses if e.date.month == datetime.utcnow().month]
        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()

        if not budgets:
            recommendations.append("💼 **Compliance Alert**: No budgets found. As your Financial Advisor, I strongly recommend setting up monthly operative budgets immediately.")
        
        total_budgeted_monthly = 0
        total_actual_monthly = 0

        for budget in budgets:
            target_cat = str(budget.category).lower()
            category_spending = sum(
                e.amount for e in current_month_expenses if str(e.category.value).lower() == target_cat
            )
            total_budgeted_monthly += budget.limit
            total_actual_monthly += category_spending

            variance = category_spending - budget.limit
            
            if variance > 0:
                recommendations.append(
                    f"⚠️ **Variance Detected**: Your '{budget.category}' spending (₹{category_spending:,.2f}) has exceeded the monthly limit (₹{budget.limit:,.2f}) by ₹{variance:,.2f}."
                )
            elif category_spending > budget.limit * 0.9:
                recommendations.append(
                    f"🔔 **High Utilization**: You have utilized 90% of your '{budget.category}' budget."
                )

        days_passed = datetime.utcnow().day
        monthly_total = sum(e.amount for e in current_month_expenses)
        avg_daily = monthly_total / days_passed if days_passed > 0 else 0
        
        if avg_daily > 2000:
             recommendations.append(
                f"📉 **Cost Control**: Your daily average burn rate is high (₹{avg_daily:,.2f})."
            )

        if datetime.utcnow().month in [1, 2, 3]:
             recommendations.append(" **Tax Planning**: We are approaching fiscal year-end (Mar 31). Ensure 80C and 80D investments are maximized.")

        if not recommendations:
            recommendations.append("✅ **Audit Clean**: Books are in order. Spending aligns with projections.")
            
        return recommendations

    def predict_monthly_spending(self, user_id: int) -> dict:
        """Predict end-of-month spending"""
        today = datetime.utcnow()
        start_of_month = today.replace(day=1)
        days_elapsed = (today - start_of_month).days + 1
        days_in_month = 30

        current_spending = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_of_month
        ).all()

        current_total = sum(e.amount for e in current_spending)
        
        if days_elapsed == 0:
            return {"predicted_monthly": 0, "days_elapsed": 0}

        predicted_monthly = (current_total / days_elapsed) * days_in_month

        return {
            "current_month_spending": current_total,
            "predicted_monthly_spending": predicted_monthly,
            "days_elapsed": days_elapsed,
            "days_remaining": days_in_month - days_elapsed
        }
