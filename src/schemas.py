from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str  # 'service', 'sms', 'email'

class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str

    class Config:
        orm_mode = True