from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.group import Group, UserGroup
from app.schemas.user import UserCreate, UserUpdate
from app.utils.jwt import get_password_hash

# Get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).options(
        joinedload(User.groups).joinedload(Group.permissions)
    ).first()

# Get user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).options(
        joinedload(User.groups).joinedload(Group.permissions)
    ).first()

# Get user by id
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).options(
        joinedload(User.groups).joinedload(Group.permissions)
    ).first()

# Create user
def create_user(db: Session, user: UserCreate):
    # If nickname is not provided or empty, use username as default
    nickname = user.nickname or user.username
    
    # Create user object without role
    db_user = User(
        username=user.username,
        email=user.email,
        nickname=nickname,
        hashed_password=get_password_hash(user.password)
    )
    
    # Add user to database first to get an ID
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Get existing groups
    existing_users = db.query(User).count()
    
    # Determine which group(s) to assign
    if existing_users == 1:
        # First user gets owner group
        owner_group = db.query(Group).filter(Group.name == "owner").first()
        if owner_group:
            # Create user-group relationship
            user_group = UserGroup(user_id=db_user.id, group_id=owner_group.id)
            db.add(user_group)
    else:
        # All other users get user group
        user_group_obj = db.query(Group).filter(Group.name == "user").first()
        if user_group_obj:
            # Create user-group relationship
            user_group = UserGroup(user_id=db_user.id, group_id=user_group_obj.id)
            db.add(user_group)
    
    # Commit changes
    db.commit()
    
    # Refresh user to include groups
    db.refresh(db_user)
    return db_user

# Update user
def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user
