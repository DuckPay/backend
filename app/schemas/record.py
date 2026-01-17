from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Record base schema
class RecordBase(BaseModel):
    amount: float
    type: str  # income, expense
    description: Optional[str] = None
    category_id: int
    date: Optional[datetime] = None

# Record create schema
class RecordCreate(RecordBase):
    pass

# Record update schema
class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None

# Record response schema
class Record(RecordBase):
    id: int
    user_id: int
    date: datetime
    
    class Config:
        from_attributes = True

# Record with category details
class RecordWithCategory(Record):
    category: dict  # Will include category details
