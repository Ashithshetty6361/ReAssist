"""
Auth routes — Register + Login
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.auth import get_current_user, create_access_token, hash_password, verify_password
from src.models.orm import User
from src.api.schemas import AuthRegister, AuthLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(req: AuthRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(user.id), "user_id": user.id}


@router.post("/login")
def login(req: AuthLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_access_token(user.id), "user_id": user.id}
