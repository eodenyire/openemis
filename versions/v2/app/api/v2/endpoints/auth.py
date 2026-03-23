from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserRole
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "student"


class UserOut(BaseModel):
    id: int; username: str; email: Optional[str]; role: str; is_active: bool; is_superuser: bool
    class Config: from_attributes = True


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=data.username).first():
        raise HTTPException(400, "Username already exists")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), token: str = Depends(lambda: None)):
    # handled via deps in real usage
    pass
