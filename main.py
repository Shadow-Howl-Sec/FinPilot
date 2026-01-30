from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    Transaction, TransactionType, PaymentMethod, ExpenseStatus
)

# ==================== PYDANTIC SCHEMAS ====================

# ---- Auth Schemas ----
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

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
    description: Optional[str] = None
    date: Optional[datetime] = None
    # Professional Fields
    payment_method: PaymentMethod = PaymentMethod.CASH
    payee: Optional[str] = None
    reference_no: Optional[str] = None
    status: ExpenseStatus = ExpenseStatus.CLEARED

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    payee: Optional[str] = None
    reference_no: Optional[str] = None
    status: Optional[ExpenseStatus] = None

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    amount: float
    category: ExpenseCategory
    description: Optional[str] = None
    date: datetime
    # Professional Fields
    payment_method: PaymentMethod
    payee: Optional[str] = None
    reference_no: Optional[str] = None
    status: ExpenseStatus
    blockchain_hash: Optional[str] = None
    created_at: datetime
    alerts: Optional[List[str]] = [] # Intelligent warnings (Daily/Weekly breaches)

# ---- Budget Schemas ----
class BudgetCreate(BaseModel):
    name: str
    category: str
    amount: float # Frontend maps 'amount' to 'limit' via internal logic or alias
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    is_rollover: bool = False

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    limit: Optional[float] = None
    amount: Optional[float] = None # Frontend alias for limit
    period: Optional[BudgetPeriod] = None
    is_rollover: Optional[bool] = None

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
    # Calculated/Alias fields
    spent: float = 0.0
    amount: float = 0.0 # Returns 'limit' as 'amount' for frontend
    is_rollover: bool = False

class GlobalBudget(BaseModel):
    limit: float

# ---- Savings Schemas ----
# Savings Schemas Removed

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
        
        # Indian Fiscal Year Logic
        fy_start, fy_end = get_indian_fiscal_year_dates()
        
        # Fetch Fiscal Year Data
        fy_expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= fy_start,
            Expense.date <= fy_end
        ).all()

        current_month_expenses = [e for e in fy_expenses if e.date.month == datetime.utcnow().month]

        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()

        # 1. Budget Variance Analysis (Monthly)
        if not budgets:
            recommendations.append("💼 **Compliance Alert**: No budgets found. As your Financial Advisor, I strongly recommend setting up monthly operative budgets immediately to maintain fiscal discipline.")
        
        total_budgeted_monthly = 0
        total_actual_monthly = 0

        for budget in budgets:
            # Monthly variance
            category_spending = sum(
                e.amount for e in current_month_expenses if e.category.value == budget.category
            )
            total_budgeted_monthly += budget.limit
            total_actual_monthly += category_spending

            variance = category_spending - budget.limit
            
            if variance > 0:
                recommendations.append(
                    f"⚠️ **Variance Detected**: Your '{budget.category}' spending (₹{category_spending:,.2f}) has exceeded the monthly limit (₹{budget.limit:,.2f}) by ₹{variance:,.2f}. "
                    f"Immediate audit of expenses in this category is required."
                )
            elif category_spending > budget.limit * 0.9:
                recommendations.append(
                    f"🔔 **High Utilization**: You have utilized 90% of your '{budget.category}' budget. "
                    f"Exercise caution to avoid overage."
                )

        # 2. Daily Run Rate Analysis
        # Calculate daily avg based on days passed in current month
        days_passed = datetime.utcnow().day
        monthly_total = sum(e.amount for e in current_month_expenses)
        avg_daily = monthly_total / days_passed if days_passed > 0 else 0
        
        if avg_daily > 2000:
             recommendations.append(
                f"📉 **Cost Control**: Your daily average burn rate is high (₹{avg_daily:,.2f}). "
                f"We need to review discretionary spending to optimize cash flow."
            )

        # 3. Allocations & Ratio Analysis
        # Simplistic Tax Advice without SavingsGoal dependency
        months_to_year_end = 12 - datetime.utcnow().month + 1 + (0 if datetime.utcnow().month > 3 else 12)
        if datetime.utcnow().month in [1, 2, 3]:
             recommendations.append("� **Tax Planning**: We are approaching fiscal year-end (Mar 31). Ensure 80C and 80D investments are maximized.")

        # Default clean chit
        if not recommendations:
            recommendations.append("✅ **Audit Clean**: Books are in order. Spending aligns with projections. Continue maintaining this fiscal discipline.")
            
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
    
    if user is None or not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:  # type: ignore
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

@app.put("/api/users/{user_id}/budget")
async def update_user_budget(user_id: int, budget: GlobalBudget, db: Session = Depends(get_db)):
    """Update user's global monthly budget limit"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.monthly_budget_limit = budget.limit
    db.commit()
    return {"message": "Global budget updated successfully", "limit": user.monthly_budget_limit}

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
        date=expense.date or datetime.utcnow(),
        payment_method=expense.payment_method,
        payee=expense.payee,
        reference_no=expense.reference_no,
        status=expense.status
    )
    
    db.add(new_expense)
    db.flush()
    
    blockchain_hash = BlockchainVerifier.generate_hash(
        transaction_id=new_expense.id,  # type: ignore
        user_id=user_id,
        amount=expense.amount,
        description=expense.description or "",
        timestamp=new_expense.date,  # type: ignore
        previous_hash=previous_hash  # type: ignore
    )
    
    new_expense.blockchain_hash = blockchain_hash  # type: ignore
    db.commit()
    db.refresh(new_expense)

    # ---- INTELLIGENT ALERTS ----
    alerts = []
    
    # 1. Fetch Category Budget
    category_budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == expense.category.value
    ).first()

    if category_budget:
        limit_monthly = category_budget.limit
        limit_daily = limit_monthly / 30.0
        limit_weekly = limit_monthly / 4.0
        
        # 2. Daily Check
        start_of_day = new_expense.date.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == expense.category,
            Expense.date >= start_of_day
        ).all()
        daily_total = sum(e.amount for e in daily_expenses)
        
        if daily_total > limit_daily:
            alerts.append(f"⚠️ Daily Limit Exceeded: You've spent ₹{daily_total:,.2f} on {expense.category.value} today (Limit: ₹{limit_daily:,.2f}).")

        # 3. Weekly Check (Rolling 7 days for simplicity or Start of Week)
        # Let's use simple rolling 7 days to catch recent intensity
        start_of_week = new_expense.date - timedelta(days=7)
        weekly_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == expense.category,
            Expense.date >= start_of_week
        ).all()
        weekly_total = sum(e.amount for e in weekly_expenses)
        
        if weekly_total > limit_weekly:
             alerts.append(f"⚠️ Weekly Threshold: ₹{weekly_total:,.2f} spent on {expense.category.value} in last 7 days (Target: ₹{limit_weekly:,.2f}).")
    
    # Attach alerts to response (simulated field, not in DB)
    response_object = ExpenseResponse.model_validate(new_expense)
    response_object.alerts = alerts
    
    return response_object

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
    
    should_rehash = False
    
    if expense.amount is not None:
        db_expense.amount = expense.amount  # type: ignore
        should_rehash = True
    if expense.category is not None:
        db_expense.category = expense.category  # type: ignore
    if expense.description is not None:
        db_expense.description = expense.description  # type: ignore
        should_rehash = True
    if expense.payment_method is not None:
        db_expense.payment_method = expense.payment_method # type: ignore
    if expense.payee is not None:
        db_expense.payee = expense.payee # type: ignore
    if expense.reference_no is not None:
        db_expense.reference_no = expense.reference_no # type: ignore
    if expense.status is not None:
        db_expense.status = expense.status # type: ignore
        
    if should_rehash:
        blockchain_hash = BlockchainVerifier.generate_hash(
            transaction_id=db_expense.id, # type: ignore
            user_id=user_id,
            amount=db_expense.amount, # type: ignore
            description=db_expense.description or "", # type: ignore
            timestamp=db_expense.date, # type: ignore
            previous_hash="modified" # Mark as modified so it doesn't fail basic checks but indicates change
        )
        db_expense.blockchain_hash = blockchain_hash # type: ignore
    
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
        limit=budget.amount, # Map frontend 'amount' to DB 'limit'
        period=budget.period,
        is_rollover=budget.is_rollover
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    # Construct response with aliases
    response = BudgetResponse.model_validate(new_budget)
    response.amount = new_budget.limit
    response.spent = 0.0 # Initial spent
    
    return response

@app.get("/api/budgets/", response_model=list[BudgetResponse])
async def get_budgets(user_id: int, db: Session = Depends(get_db)):
    """Get all budgets for a user with calculated spent amount"""
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    
    # Calculate spent for each budget in current month
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start_of_month
    ).all()
    
    response_budgets = []
    for budget in budgets:
        # Sum expenses for this budget category
        spent = sum(e.amount for e in current_expenses if e.category.value == budget.category)
        
        # Prepare response object
        budget_resp = BudgetResponse.model_validate(budget)
        budget_resp.spent = spent
        budget_resp.amount = budget.limit
        response_budgets.append(budget_resp)
        
    return response_budgets

@app.get("/api/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Calculate spent
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.category == budget.category, # Filter directly by category
        Expense.date >= start_of_month
    ).all()
    
    spent = sum(e.amount for e in current_expenses)
    
    response = BudgetResponse.model_validate(budget)
    response.spent = spent
    # response.amount is handled by property alias in model
    
    return response

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
        db_budget.name = budget.name  # type: ignore
    if budget.limit is not None:
        db_budget.limit = budget.limit  # type: ignore
    if budget.amount is not None:
        db_budget.limit = budget.amount # Alias handling
    if budget.period is not None:
        db_budget.period = budget.period  # type: ignore
    if budget.is_rollover is not None:
        db_budget.is_rollover = budget.is_rollover # type: ignore
    
    db_budget.updated_at = datetime.utcnow()  # type: ignore
    db.commit()
    db.refresh(db_budget)
    
    # Calculate spent (re-fetch logic for updated budget)
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.category == db_budget.category,
        Expense.date >= start_of_month
    ).all()
    
    spent = sum(e.amount for e in current_expenses)
    
    response = BudgetResponse.model_validate(db_budget)
    response.spent = spent
    
    return response

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

# Savings Endpoints Removed

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
    
    # Savings History Analysis (Last 3 Months)
    savings_history = []
    current_date = datetime.utcnow()
    global_limit = user.monthly_budget_limit or 0
    
    for i in range(3): # Current month (0) + 2 previous
        # Calculate month date
        month_date = current_date - timedelta(days=30 * i) 
        # Approximate month start/end
        m_start = month_date.replace(day=1, hour=0, minute=0, second=0)
        # Handle December rollover for next month calculation (hacky but works for rough history)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1)
        else:
             m_end = m_start.replace(month=m_start.month + 1)
        
        # Determine strict previous months (simplify: just strict months)
        # Actually better to use specific year/month logic
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
             "total_spent_month": advisor.analyze_spending_patterns(user_id, days=30).get("total_spent", 0), # reusing analysis
             "net_savings": global_limit - advisor.analyze_spending_patterns(user_id, days=30).get("total_spent", 0),
             "savings_history": savings_history,
             "overall_savings": (global_limit * max(1, int((datetime.utcnow() - user.created_at).days / 30))) - (db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id).scalar() or 0)
        }
    }

# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=5500, reload=True)
