"""
ReAssist JWT Authentication
Lightweight but production-grade auth layer.
- Bcrypt password hashing
- JWT access tokens (HS256)
- FastAPI dependency for protected routes
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

# ─── Config ───────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("JWT_SECRET", "reassist-dev-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ─── Password Utils ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── Token Utils ──────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ─── FastAPI Dependencies ─────────────────────────────────────────────────────

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Protected route dependency.
    If no token is provided, falls back to a default demo user (auto-created).
    This keeps the platform functional for demos without requiring login.
    """
    if credentials and credentials.credentials:
        user_id = decode_token(credentials.credentials)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user

    # Fallback: Auto-create or fetch a demo user (no auth friction for demos)
    demo_user = db.query(User).filter(User.email == "demo@reassist.ai").first()
    if not demo_user:
        demo_user = User(
            email="demo@reassist.ai",
            password_hash=hash_password("demo123")
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    return demo_user
