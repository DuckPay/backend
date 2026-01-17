from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.database import get_db
from app.utils.auth import get_current_user
from app.crud.category import get_categories, get_category, create_category, update_category, delete_category
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.models.user import User

# Create router
router = APIRouter()

# Get all categories
@router.get("/", response_model=List[Category])
def read_categories(
    type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_categories(db=db, user_id=current_user.id, type=type)

# Get category by ID
@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_category = get_category(db=db, category_id=category_id, user_id=current_user.id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return db_category

# Create category
@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_category(db=db, category=category, user_id=current_user.id)

# Update category
@router.post("/update/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_category = update_category(db=db, category_id=category_id, category=category, user_id=current_user.id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or cannot be updated"
        )
    return db_category

# Delete category
@router.post("/delete/{category_id}", status_code=status.HTTP_200_OK)
def delete_existing_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_category(db=db, category_id=category_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or cannot be deleted"
        )
    return {"status": "success", "message": "Category deleted successfully"}
