"""FinPilot - AI-Powered Personal Finance Manager"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
from typing import List, Optional

# Import database and models
from backend.database import get_db, init_db
from backend.models import (
    User, Expense, ExpenseCategory, Budget, BudgetPeriod,
    SavingsGoal, Transaction, TransactionType
)

# ==================== PYDANTIC SCHEMAS ====================

# ---- Auth Schemas ----
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime
    is_active: bool

# ---- Expense Schemas ----
class ExpenseCreate(BaseModel):
    amount: float
    category: ExpenseCategory
    description: str = None
    date: datetime = None

class ExpenseUpdate(BaseModel):
    amount: float = None
    category: ExpenseCategory = None
    description: str = None

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    amount: float
    category: ExpenseCategory
    description: str
    date: datetime
    blockchain_hash: str
    created_at: datetime

# ---- Budget Schemas ----
class BudgetCreate(BaseModel):
    name: str
    category: str
    limit: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY

class BudgetUpdate(BaseModel):
    name: str = None
    limit: float = None
    period: BudgetPeriod = None

class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    category: str
    limit: float
    period: BudgetPeriod
    start_date: datetime
    created_at: datetime

# ---- Savings Schemas ----
class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: datetime = None
    description: str = None

class SavingsGoalUpdate(BaseModel):
    name: str = None
    target_amount: float = None
    current_amount: float = None
    deadline: datetime = None
    description: str = None

class SavingsGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: datetime
    description: str
    progress_percentage: float
    created_at: datetime

# ==================== BLOCKCHAIN UTILITIES ====================

class BlockchainVerifier:
    """Blockchain verification for transactions"""

    @staticmethod
    def generate_hash(transaction_id: int, user_id: int, amount: float, 
                     description: str, timestamp: datetime, previous_hash: Optional[str] = None) -> str:
        """Generate SHA256 hash of transaction"""
        transaction_data = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "description": description,
            "timestamp": timestamp.isoformat(),
            "previous_hash": previous_hash or "genesis"
        }
        json_data = json.dumps(transaction_data, sort_keys=True)
        hash_object = hashlib.sha256(json_data.encode())
        return hash_object.hexdigest()

    @staticmethod
    def verify_transaction(blockchain_hash: str, transaction_id: int, user_id: int,
                          amount: float, description: str, timestamp: datetime,
                          previous_hash: Optional[str] = None) -> bool:
        """Verify transaction integrity"""
        calculated_hash = BlockchainVerifier.generate_hash(
            transaction_id, user_id, amount, description, timestamp, previous_hash
        )
        return calculated_hash == blockchain_hash

# ==================== AI ADVISOR ENGINE ====================

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
        """Generate AI-powered recommendations"""
        recommendations = []

        start_of_month = datetime.utcnow().replace(day=1)
        current_expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_of_month
        ).all()

        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()

        if not budgets:
            recommendations.append("📊 Create monthly budgets to track your spending limits")

        for budget in budgets:
            category_spending = sum(
                e.amount for e in current_expenses if e.category.value == budget.category
            )

            if category_spending > budget.limit:
                overage = category_spending - budget.limit
                recommendations.append(
                    f"⚠️ You've exceeded {budget.category} budget by ${overage:.2f}. "
                    f"Consider reducing expenses in this category."
                )
            elif category_spending > budget.limit * 0.8:
                remaining = budget.limit - category_spending
                recommendations.append(
                    f"💡 You're approaching your {budget.category} budget limit. "
                    f"Only ${remaining:.2f} remaining."
                )

        patterns = self.analyze_spending_patterns(user_id, days=30)
        
        if patterns.get("expense_count", 0) == 0:
            recommendations.append("📝 Start tracking your expenses to get personalized insights")
        else:
            avg_daily = patterns.get("average_daily_spend", 0)
            if avg_daily > 50:
                recommendations.append(
                    f"💰 Your average daily spending is ${avg_daily:.2f}. "
                    f"Look for areas to optimize and reduce costs."
                )

        return recommendations if recommendations else [
            "✅ Great job! Your spending is on track. Keep maintaining your budget."
        ]

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

# ==================== FASTAPI APP ====================

app = FastAPI(
    title="FinPilot",
    description="AI-Powered Personal Finance Manager",
    version="1.0.0"
)

# Mount static files
static_dir = Path(__file__).parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ==================== HELPER FUNCTION ====================

def get_html_content():
    """Load and return HTML content"""
    template_path = Path(__file__).parent / "frontend" / "template" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>FinPilot - Loading...</h1></body></html>"

# ==================== ROUTES: HOME ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    return get_html_content()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "FinPilot"}

# ==================== ROUTES: AUTHENTICATION ====================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=User.hash_password(user.password),
        full_name=user.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(user_id: int, db: Session = Depends(get_db)):
    """Get current user info"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ==================== ROUTES: EXPENSES ====================

@app.post("/api/expenses/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(expense: ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new expense"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    last_transaction = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.id.desc()).first()
    previous_hash = last_transaction.blockchain_hash if last_transaction else None
    
    new_expense = Expense(
        user_id=user_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date or datetime.utcnow()
    )
    
    db.add(new_expense)
    db.flush()
    
    blockchain_hash = BlockchainVerifier.generate_hash(
        transaction_id=new_expense.id,
        user_id=user_id,
        amount=expense.amount,
        description=expense.description or "",
        timestamp=new_expense.date,
        previous_hash=previous_hash
    )
    
    new_expense.blockchain_hash = blockchain_hash
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

@app.get("/api/expenses/", response_model=list[ExpenseResponse])
async def get_expenses(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all expenses for a user"""
    expenses = db.query(Expense).filter(Expense.user_id == user_id).offset(skip).limit(limit).all()
    return expenses

@app.get("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense

@app.put("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: int, expense: ExpenseUpdate, user_id: int, db: Session = Depends(get_db)):
    """Update an expense"""
    db_expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()
    
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.amount is not None:
        db_expense.amount = expense.amount
    if expense.category is not None:
        db_expense.category = expense.category
    if expense.description is not None:
        db_expense.description = expense.description
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@app.delete("/api/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return None

# ==================== ROUTES: BUDGETS ====================

@app.post("/api/budgets/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new budget"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_budget = Budget(
        user_id=user_id,
        name=budget.name,
        category=budget.category,
        limit=budget.limit,
        period=budget.period
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    return new_budget

@app.get("/api/budgets/", response_model=list[BudgetResponse])
async def get_budgets(user_id: int, db: Session = Depends(get_db)):
    """Get all budgets for a user"""
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    return budgets

@app.get("/api/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return budget

@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: int, budget: BudgetUpdate, user_id: int, db: Session = Depends(get_db)):
    """Update a budget"""
    db_budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.name is not None:
        db_budget.name = budget.name
    if budget.limit is not None:
        db_budget.limit = budget.limit
    if budget.period is not None:
        db_budget.period = budget.period
    
    db_budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_budget)
    
    return db_budget

@app.delete("/api/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    return None

# ==================== ROUTES: SAVINGS ====================

@app.post("/api/savings/", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_goal(goal: SavingsGoalCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new savings goal"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_goal = SavingsGoal(
        user_id=user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        deadline=goal.deadline,
        description=goal.description
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    return new_goal

@app.get("/api/savings/", response_model=list[SavingsGoalResponse])
async def get_savings_goals(user_id: int, db: Session = Depends(get_db)):
    """Get all savings goals for a user"""
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
    return goals

@app.get("/api/savings/{goal_id}", response_model=SavingsGoalResponse)
async def get_savings_goal(goal_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == user_id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    return goal

@app.put("/api/savings/{goal_id}", response_model=SavingsGoalResponse)
async def update_savings_goal(goal_id: int, goal: SavingsGoalUpdate, user_id: int, db: Session = Depends(get_db)):
    """Update a savings goal"""
    db_goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == user_id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    if goal.name is not None:
        db_goal.name = goal.name
    if goal.target_amount is not None:
        db_goal.target_amount = goal.target_amount
    if goal.current_amount is not None:
        db_goal.current_amount = goal.current_amount
    if goal.deadline is not None:
        db_goal.deadline = goal.deadline
    if goal.description is not None:
        db_goal.description = goal.description
    
    db_goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_goal)
    
    return db_goal

@app.delete("/api/savings/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_savings_goal(goal_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete a savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == user_id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    db.delete(goal)
    db.commit()
    return None

# ==================== ROUTES: AI ADVISOR ====================

@app.get("/api/advisor/recommendations")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get AI-powered financial recommendations"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    recommendations = advisor.get_recommendations(user_id)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@app.get("/api/advisor/analysis")
async def get_spending_analysis(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Analyze spending patterns"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    analysis = advisor.analyze_spending_patterns(user_id, days=days)
    
    return {
        "user_id": user_id,
        "analysis": analysis
    }

@app.get("/api/advisor/forecast")
async def get_spending_forecast(user_id: int, db: Session = Depends(get_db)):
    """Get predicted monthly spending"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    forecast = advisor.predict_monthly_spending(user_id)
    
    return {
        "user_id": user_id,
        "forecast": forecast
    }

@app.get("/api/advisor/dashboard")
async def get_dashboard_summary(user_id: int, db: Session = Depends(get_db)):
    """Get complete dashboard summary"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    advisor = FinancialAdvisor(db)
    
    return {
        "user_id": user_id,
        "user_name": user.full_name or user.username,
        "analysis": advisor.analyze_spending_patterns(user_id, days=30),
        "forecast": advisor.predict_monthly_spending(user_id),
        "recommendations": advisor.get_recommendations(user_id)
    }

# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
