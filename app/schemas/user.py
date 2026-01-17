from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Group base schema
class GroupBase(BaseModel):
    name: str
    is_admin: Optional[bool] = False
    description: Optional[str] = None
    is_system: Optional[bool] = False
    level: Optional[int] = 5

# Permission schema
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str

class Permission(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Group response schema
class Group(GroupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True

# User base schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    nickname: Optional[str] = None

# User create schema
class UserCreate(UserBase):
    password: str
    groups: List[str] = ["user"]

# User update schema
class UserUpdate(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    groups: Optional[List[str]] = None

# User response schema
class User(UserBase):
    id: int
    groups: List[Group] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# User login schema
class UserLogin(BaseModel):
    username: str
    password: str

# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data schema
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    groups: Optional[List[str]] = None
