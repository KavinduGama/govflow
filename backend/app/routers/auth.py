from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth_utils import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


def user_payload(user: User) -> dict:
    """Public user fields sent to the frontend."""
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/auth/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        email=request.email,
        name=request.name,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id)})
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_payload(new_user)
    )

@router.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and return JWT token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    token = create_access_token({"sub": str(user.id)})
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_payload(user)
    )

@router.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user profile."""
    return user_payload(current_user)
