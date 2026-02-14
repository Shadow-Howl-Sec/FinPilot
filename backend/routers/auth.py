from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserRegister, UserLogin, UserResponse, GlobalBudget, UserUpdate
from ..services.bot_service import WhatsAppBotService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.put("/profile", response_model=UserResponse)
async def update_profile(profile_data: UserUpdate, user_id: int, db: Session = Depends(get_db)):
    """Update user profile info"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    if profile_data.phone_number is not None:
        user.phone_number = profile_data.phone_number
        
    db.commit()
    db.refresh(user)
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
        full_name=user.full_name,
        phone_number=user.phone_number # Persist phone number from registration
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Trigger welcome message if phone number is provided
    if new_user.phone_number:
        from ..services.bot_service import WhatsAppBotService
        await WhatsAppBotService.send_welcome_message(db, new_user.phone_number, new_user.full_name)
    
    return new_user

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user via username or phone number"""
    # Try finding by username first
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # If not found by username, try finding by phone number
    if not user:
        user = db.query(User).filter(User.phone_number == credentials.username).first()
    
    if user is None or not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int, db: Session = Depends(get_db)):
    """Get current user info"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
