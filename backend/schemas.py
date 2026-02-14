from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List, Optional
from .models import (
    ExpenseCategory, BudgetPeriod, PaymentMethod, ExpenseStatus
)

# ---- Auth Schemas ----
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None # Added for WhatsApp onboarding

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    created_at: datetime
    is_active: bool

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

# ---- Expense Schemas ----
class ExpenseCreate(BaseModel):
    amount: float
    category: ExpenseCategory
    description: Optional[str] = None
    date: Optional[datetime] = None
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
    payment_method: PaymentMethod = PaymentMethod.CASH
    payee: Optional[str] = None
    reference_no: Optional[str] = None
    status: ExpenseStatus = ExpenseStatus.CLEARED
    blockchain_hash: Optional[str] = None
    created_at: datetime
    alerts: Optional[List[str]] = []

# ---- Budget Schemas ----
class BudgetCreate(BaseModel):
    name: str
    category: str
    amount: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    is_rollover: bool = False

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    limit: Optional[float] = None
    amount: Optional[float] = None
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
    spent: float = 0.0
    amount: float = 0.0
    is_rollover: bool = False

class GlobalBudget(BaseModel):
    limit: float
