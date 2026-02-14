"""FinPilot Models - Database models and business logic"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import hashlib
import secrets
import enum

# ==================== ENUMS ====================

class ExpenseCategory(str, enum.Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SHOPPING = "shopping"
    EDUCATION = "education"
    OTHER = "other"

class BudgetPeriod(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class TransactionType(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"

class PaymentMethod(str, enum.Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"
    NET_BANKING = "Net Banking"
    CHECK = "Check"
    OTHER = "Other"

class ExpenseStatus(str, enum.Enum):
    CLEARED = "Cleared"
    PENDING = "Pending"
    RECONCILED = "Reconciled"

# ==================== USER MODEL ====================

class User(Base):
    """User model for FinPilot"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String, unique=True, index=True, nullable=True) # For WhatsApp Bot Integration
    monthly_budget_limit = Column(Float, default=0.0) # Global Monthly Budget Cap

    # Relationships
    expenses = relationship("Expense", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        salt, password_hash = self.password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return new_hash == password_hash

# ==================== EXPENSE MODEL ====================

class Expense(Base):
    """Expense model"""
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Enum(ExpenseCategory), default=ExpenseCategory.OTHER)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Professional Fields
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    payee = Column(String, nullable=True) # Vendor/Person
    reference_no = Column(String, nullable=True) # Invoice/Bill #
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.CLEARED)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    blockchain_hash = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="expenses")
    transaction = relationship("Transaction", uselist=False, back_populates="expense")

# ==================== BUDGET MODEL ====================

class Budget(Base):
    """Budget model"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    limit = Column(Float, nullable=False)
    period = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_rollover = Column(Boolean, default=False) # Access unused budget in next period
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")

    @property
    def amount(self) -> float:
        """Alias for limit"""
        return self.limit

# SavingsGoal Logic Removed

# ==================== TRANSACTION MODEL ====================

# ==================== TRANSACTION MODEL ====================

class Transaction(Base):
    """Transaction model - represents verifiable financial records"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    type = Column(Enum(TransactionType), default=TransactionType.EXPENSE)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    blockchain_hash = Column(String, unique=True, index=True)
    previous_hash = Column(String, nullable=True)
    verified = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    expense = relationship("Expense", back_populates="transaction")
