from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, Budget, Expense
from ..schemas import BudgetCreate, BudgetUpdate, BudgetResponse, GlobalBudget

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new budget"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_budget = Budget(
        user_id=user_id,
        name=budget.name,
        category=budget.category,
        limit=budget.amount, # amount from schema maps to limit in model
        period=budget.period,
        is_rollover=budget.is_rollover
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    # Calculate initial spent (it might not be 0 if expenses already exist for this category)
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    spent = db.query(Expense).filter(
        Expense.user_id == user_id,
        func.lower(Expense.category) == budget.category.lower(),
        Expense.date >= start_of_month
    ).with_entities(Expense.amount).all()
    total_spent = sum(item[0] for item in spent)
    
    response = BudgetResponse.model_validate(new_budget)
    response.spent = total_spent
    
    return response

@router.get("/", response_model=list[BudgetResponse])
async def get_budgets(user_id: int, db: Session = Depends(get_db)):
    """Get all budgets for a user with calculated spent amount"""
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start_of_month
    ).all()
    
    response_budgets = []
    for budget in budgets:
        # Match by Enum value or string, normalized to lowercase
        target_cat = str(budget.category).lower()
        spent = sum(e.amount for e in current_expenses if str(e.category.value).lower() == target_cat)
        budget_resp = BudgetResponse.model_validate(budget)
        budget_resp.spent = float(spent)
        response_budgets.append(budget_resp)
        
    return response_budgets

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.category == budget.category,
        Expense.date >= start_of_month
    ).all()
    
    spent = sum(e.amount for e in current_expenses)
    
    response = BudgetResponse.model_validate(budget)
    response.spent = spent
    
    return response

@router.put("/{budget_id}", response_model=BudgetResponse)
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
    if budget.amount is not None:
        db_budget.limit = budget.amount
    elif budget.limit is not None: # Backup for variations in schema
        db_budget.limit = budget.limit
        
    if budget.period is not None:
        db_budget.period = budget.period
    if budget.is_rollover is not None:
        db_budget.is_rollover = budget.is_rollover
    
    db_budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_budget)
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.category == db_budget.category,
        Expense.date >= start_of_month
    ).all()
    
    spent = sum(e.amount for e in current_expenses)
    
    response = BudgetResponse.model_validate(db_budget)
    response.spent = float(spent)
    
    return response

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
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

@router.put("/users/{user_id}/global")
async def update_user_global_budget(user_id: int, budget: GlobalBudget, db: Session = Depends(get_db)):
    """Update user's global monthly budget limit"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.monthly_budget_limit = budget.limit
    db.commit()
    return {"message": "Global budget updated successfully", "limit": user.monthly_budget_limit}
