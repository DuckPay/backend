from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models here to avoid circular imports
from app.models.user import User
from app.models.group import Group, UserGroup, Permission, GroupPermission, TablePermission

# Initialize default groups and permissions
def init_db():
    """Initialize the database with default groups and permissions"""
    db = SessionLocal()
    try:
        # Check if groups already exist
        existing_groups = db.query(Group).count()
        
        # Create default groups if they don't exist
        if existing_groups == 0:
            # Create default groups
            owner_group = Group(
                name="owner",
                is_admin=True,
                description="System owner with all permissions",
                is_system=True,
                level=0
            )
            
            admin_group = Group(
                name="admin",
                is_admin=True,
                description="System administrator with limited permissions",
                is_system=True,
                level=1
            )
            
            user_group = Group(
                name="user",
                is_admin=False,
                description="Regular user with basic permissions",
                is_system=True,
                level=3
            )
            
            # Add groups to database
            db.add_all([owner_group, admin_group, user_group])
            db.commit()
        else:
            # Get existing groups
            owner_group = db.query(Group).filter(Group.name == "owner").first()
            admin_group = db.query(Group).filter(Group.name == "admin").first()
            user_group = db.query(Group).filter(Group.name == "user").first()
            
            # If any default group is missing, create it
            if not owner_group:
                owner_group = Group(
                    name="owner",
                    is_admin=True,
                    description="System owner with all permissions",
                    is_system=True,
                    level=0
                )
                db.add(owner_group)
            else:
                # Update existing owner group with level
                owner_group.level = 0
                db.add(owner_group)
            
            if not admin_group:
                admin_group = Group(
                    name="admin",
                    is_admin=True,
                    description="System administrator with limited permissions",
                    is_system=True,
                    level=1
                )
                db.add(admin_group)
            else:
                # Update existing admin group with level
                admin_group.level = 1
                db.add(admin_group)
            
            if not user_group:
                user_group = Group(
                    name="user",
                    is_admin=False,
                    description="Regular user with basic permissions",
                    is_system=True,
                    level=3
                )
                db.add(user_group)
            else:
                # Update existing user group with level
                user_group.level = 3
                db.add(user_group)
            
            db.commit()
        
        # Check if permissions already exist
        existing_permissions = db.query(Permission).count()
        
        # Create permissions if they don't exist
        if existing_permissions == 0:
            # Create permissions
            permissions = [
                # User management permissions
                Permission(name="create_user", description="Create new users", category="user_management"),
                Permission(name="delete_user", description="Delete users", category="user_management"),
                Permission(name="edit_user", description="Edit user information", category="user_management"),
                Permission(name="change_user_password", description="Change user passwords", category="user_management"),
                Permission(name="change_user_info", description="Change user info (nickname, email, groups, enabled)", category="user_management"),
                Permission(name="change_username", description="Change username", category="user_management"),
                
                # Group management permissions
                Permission(name="manage_groups", description="Manage groups (edit name, delete, change permissions)", category="group_management"),
            ]
            
            # Add permissions to database
            db.add_all(permissions)
            db.commit()
        else:
            # Get all permissions
            permissions = db.query(Permission).all()
        
        # Check if group permissions already exist for owner and admin groups
        existing_owner_permissions = db.query(GroupPermission).filter(GroupPermission.group_id == owner_group.id).count()
        existing_admin_permissions = db.query(GroupPermission).filter(GroupPermission.group_id == admin_group.id).count()
        
        # Assign all permissions to owner group if not already assigned
        if existing_owner_permissions == 0:
            for permission in permissions:
                group_permission = GroupPermission(group_id=owner_group.id, permission_id=permission.id)
                db.add(group_permission)
        
        # Assign all permissions to admin group if not already assigned (as default)
        if existing_admin_permissions == 0:
            for permission in permissions:
                group_permission = GroupPermission(group_id=admin_group.id, permission_id=permission.id)
                db.add(group_permission)
        
        db.commit()
        
        print("Default groups and permissions created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
