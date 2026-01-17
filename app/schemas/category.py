from pydantic import BaseModel
from typing import Optional

# Category base schema
class CategoryBase(BaseModel):
    name: str
    type: str  # income, expense
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: Optional[bool] = False

# Category create schema
class CategoryCreate(CategoryBase):
    pass

# Category update schema
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

# Category response schema
class Category(CategoryBase):
    id: int
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True
