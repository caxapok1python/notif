from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from models import User
from schemas import UserOut
from src.dependencies import get_current_user, get_current_admin_user, get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", response_model=List[UserOut])
def read_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    return db.query(User).all()