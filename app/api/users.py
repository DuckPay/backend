from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.jwt import verify_password, create_access_token
from app.crud.user import get_user_by_username, get_user_by_email, create_user, get_user_by_id, update_user
from app.schemas.user import UserCreate, User, Token, UserUpdate
from app.utils.auth import get_current_user

# Create router
router = APIRouter()

# User registration
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    return create_user(db=db, user=user)

# User login
@router.post("/login", response_model=Token)
def login_user(user_credentials: dict, db: Session = Depends(get_db)):
    # Get username and password from request body
    username = user_credentials.get("username")
    password = user_credentials.get("password")
    
    # Validate input
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    
    # Get user by username
    user = get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user groups
    user_groups = [group.name for group in user.groups]
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "groups": user_groups}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user
@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Update current user
@router.post("/me/update", response_model=User)
def update_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user(db=db, user_id=current_user.id, user=user_update)
