from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

# Get categories by user_id
def get_categories(db: Session, user_id: int, type: str = None):
    query = db.query(Category).filter(
        (Category.user_id == user_id) | (Category.is_default == True)
    )
    if type:
        query = query.filter(Category.type == type)
    return query.all()

# Get category by id
def get_category(db: Session, category_id: int, user_id: int):
    return db.query(Category).filter(
        Category.id == category_id,
        (Category.user_id == user_id) | (Category.is_default == True)
    ).first()

# Create category
def create_category(db: Session, category: CategoryCreate, user_id: int):
    db_category = Category(
        **category.model_dump(),
        user_id=user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Update category
def update_category(db: Session, category_id: int, category: CategoryUpdate, user_id: int):
    db_category = get_category(db, category_id, user_id)
    if db_category and not db_category.is_default:  # Only allow update non-default categories
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

# Delete category
def delete_category(db: Session, category_id: int, user_id: int):
    db_category = get_category(db, category_id, user_id)
    if db_category and not db_category.is_default:  # Only allow delete non-default categories
        db.delete(db_category)
        db.commit()
        return True
    return False
