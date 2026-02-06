from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Expense, Budget
from ..schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from ..services.blockchain import BlockchainVerifier

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
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

    # ---- INTELLIGENT ALERTS ----
    alerts = []
    category_budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == expense.category.value
    ).first()

    if category_budget:
        limit_monthly = category_budget.limit
        limit_daily = limit_monthly / 30.0
        limit_weekly = limit_monthly / 4.0
        
        start_of_day = new_expense.date.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == expense.category,
            Expense.date >= start_of_day
        ).all()
        daily_total = sum(e.amount for e in daily_expenses)
        
        if daily_total > limit_daily:
            alerts.append(f"⚠️ Daily Limit Exceeded: You've spent ₹{daily_total:,.2f} on {expense.category.value} today (Limit: ₹{limit_daily:,.2f}).")

        start_of_week = new_expense.date - timedelta(days=7)
        weekly_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == expense.category,
            Expense.date >= start_of_week
        ).all()
        weekly_total = sum(e.amount for e in weekly_expenses)
        
        if weekly_total > limit_weekly:
             alerts.append(f"⚠️ Weekly Threshold: ₹{weekly_total:,.2f} spent on {expense.category.value} in last 7 days (Target: ₹{limit_weekly:,.2f}).")
    
    response_object = ExpenseResponse.model_validate(new_expense)
    response_object.alerts = alerts
    
    return response_object

@router.get("/", response_model=list[ExpenseResponse])
async def get_expenses(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all expenses for a user"""
    expenses = db.query(Expense).filter(Expense.user_id == user_id).offset(skip).limit(limit).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
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
        db_expense.amount = expense.amount
        should_rehash = True
    if expense.category is not None:
        db_expense.category = expense.category
    if expense.description is not None:
        db_expense.description = expense.description
        should_rehash = True
    if expense.payment_method is not None:
        db_expense.payment_method = expense.payment_method
    if expense.payee is not None:
        db_expense.payee = expense.payee
    if expense.reference_no is not None:
        db_expense.reference_no = expense.reference_no
    if expense.status is not None:
        db_expense.status = expense.status
        
    if should_rehash:
        blockchain_hash = BlockchainVerifier.generate_hash(
            transaction_id=db_expense.id,
            user_id=user_id,
            amount=db_expense.amount,
            description=db_expense.description or "",
            timestamp=db_expense.date,
            previous_hash="modified"
        )
        db_expense.blockchain_hash = blockchain_hash
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
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
