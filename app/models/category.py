from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # income, expense
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True, default="#000000")
    is_default = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable=True for default categories
    
    # Relationships
    user = relationship("User", back_populates="categories")
    records = relationship("Record", back_populates="category")
