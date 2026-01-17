from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.database import get_db
from app.models.user import User
from app.models.group import Group as GroupModel, UserGroup, Permission, GroupPermission
from app.utils.auth import check_admin_role, check_owner_role, can_edit_user, can_change_role
from app.schemas.user import User as UserSchema, UserUpdate, UserCreate, Group, GroupBase, Permission as PermissionSchema
from app.utils.jwt import get_password_hash

# Create router
router = APIRouter()

# Get all users - admin only
@router.get("/admin/users", response_model=list[UserSchema])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Get all users in the system (admin only)"""
    return db.query(User).all()

# Create user - admin only
@router.post("/admin/users/add", response_model=UserSchema)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Create a new user (admin only)"""
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user object without role
    db_user = User(
        username=user.username,
        email=user.email,
        nickname=user.nickname or user.username,
        hashed_password=get_password_hash(user.password)
    )
    
    # Add user to database first to get an ID
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Check if current user can assign requested groups
    current_user_groups = [g.name for g in current_user.groups]
    
    # Get all requested groups from database
    for group_name in user.groups:
        requested_group = db.query(GroupModel).filter(GroupModel.name == group_name).first()
        if not requested_group:
            # Skip invalid groups
            continue
        
        # Check if current user can assign this group
        # Owner can assign any group
        if "owner" not in current_user_groups:
            # Admin can only assign user or admin groups, not owner
            if requested_group.name == "owner":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can assign owner group"
                )
        
        # Assign the group to the user
        user_group = UserGroup(user_id=db_user.id, group_id=requested_group.id)
        db.add(user_group)
    
    db.commit()
    
    # Refresh user to include groups
    db.refresh(db_user)
    return db_user

# Update user - apply new permission rules
@router.post("/admin/users/update/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Update a user - apply new permission rules:
    1. Owner can edit any user including other owners
    2. Admin can only edit regular users, not other admins or owners
    3. Admin can promote regular users to admin, but can't demote or change other roles
    """
    # Get the user to update
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can edit this user
    if not can_edit_user(current_user, user_to_update):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this user"
        )
    
    # Update user data
    update_data = user_update.dict(exclude_unset=True)
    
    # Extract groups from update data if present
    groups = update_data.pop("groups", None)
    
    # Handle password update if provided
    if "password" in update_data:
        # Hash the password before updating
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update user fields
    for field, value in update_data.items():
        if hasattr(user_to_update, field):
            setattr(user_to_update, field, value)
    
    # Update user groups if requested
    if groups:
        # Check if current user can assign requested groups
        current_user_groups = [g.name for g in current_user.groups]
        
        # Remove existing groups
        db.query(UserGroup).filter(UserGroup.user_id == user_id).delete()
        
        # Assign new groups
        for group_name in groups:
            requested_group = db.query(GroupModel).filter(GroupModel.name == group_name).first()
            if not requested_group:
                # Skip invalid groups
                continue
            
            # Check if current user can assign this group
            # Owner can assign any group
            if "owner" not in current_user_groups:
                # Admin can only assign user or admin groups, not owner
                if requested_group.name == "owner":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only owner can assign owner group"
                    )
            
            # Assign the group to the user
            user_group = UserGroup(user_id=user_id, group_id=requested_group.id)
            db.add(user_group)
    
    db.commit()
    db.refresh(user_to_update)
    return user_to_update

# Delete user - apply new permission rules
@router.post("/admin/users/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Delete a user - apply new permission rules:
    1. Owner can delete any user including other owners
    2. Admin can only delete regular users, not other admins or owners
    """
    # Get the user to delete
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can delete this user
    if not can_edit_user(current_user, user_to_delete):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this user"
        )
    
    # Delete user-group relationships first (for better database integrity)
    db.query(UserGroup).filter(UserGroup.user_id == user_id).delete()
    
    # Delete user
    db.delete(user_to_delete)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}

# Group Management Endpoints

# Get all groups - admin only
@router.get("/admin/groups", response_model=list[Group])
def get_all_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Get all groups in the system (admin only)"""
    return db.query(GroupModel).all()

# Create group - owner only
@router.post("/admin/groups/add", response_model=Group)
def add_group(
    group: GroupBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_owner_role)
):
    """Create a new group (owner only)"""
    # Check if group name already exists
    db_group = db.query(GroupModel).filter(GroupModel.name == group.name).first()
    if db_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    
    # Create group object
    db_group = GroupModel(
        name=group.name,
        description=group.description,
        is_admin=group.is_admin,
        is_system=group.is_system,
        level=group.level
    )
    
    # Add group to database
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# Update group - owner only
@router.post("/admin/groups/update/{group_id}", response_model=Group)
def update_group(
    group_id: int,
    group_update: GroupBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_owner_role)
):
    """Update a group (owner only)"""
    # Get the group to update
    group_to_update = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if not group_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Cannot modify owner group
    if group_to_update.name == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner group cannot be modified"
        )
    
    # Check if group name already exists (excluding current group)
    db_group = db.query(GroupModel).filter(GroupModel.name == group_update.name, GroupModel.id != group_id).first()
    if db_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    
    # Update group fields
    update_data = group_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(group_to_update, field):
            setattr(group_to_update, field, value)
    
    db.commit()
    db.refresh(group_to_update)
    return group_to_update

# Delete group - owner only, cannot delete system groups
@router.post("/admin/groups/delete/{group_id}", status_code=status.HTTP_200_OK)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_owner_role)
):
    """Delete a group (owner only, cannot delete system groups)"""
    # Get the group to delete
    group_to_delete = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if not group_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Cannot delete owner group
    if group_to_delete.name == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner group cannot be deleted"
        )
    
    # Cannot delete system groups
    if group_to_delete.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system groups"
        )
    
    # Delete all user-group relationships for this group
    db.query(UserGroup).filter(UserGroup.group_id == group_id).delete()
    
    # Delete all group-permission relationships for this group
    db.query(GroupPermission).filter(GroupPermission.group_id == group_id).delete()
    
    # Delete the group
    db.delete(group_to_delete)
    db.commit()
    return {"status": "success", "message": "Group deleted successfully"}

# Get all permissions - admin only
@router.get("/admin/permissions", response_model=list[PermissionSchema])
def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Get all permissions in the system (admin only)"""
    return db.query(Permission).all()

# Get all permission nodes - public admin endpoint (no auth required)
@router.get("/admin/permission-nodes", response_model=list[dict])
def get_all_permission_nodes(
    db: Session = Depends(get_db)
):
    """Get all permissions organized by category (public endpoint, no authentication required)"""
    permissions = db.query(Permission).all()
    
    # Organize permissions by category
    category_map = {}
    for permission in permissions:
        if permission.category not in category_map:
            category_map[permission.category] = {
                "category": permission.category,
                "children": []
            }
        category_map[permission.category]["children"].append({
            "id": permission.id,
            "name": permission.name,
            "description": permission.description
        })
    
    # Convert to list
    return list(category_map.values())

# Get group permissions - admin only
@router.get("/admin/groups/{group_id}/permissions", response_model=dict)
def get_group_permissions(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    """Get permissions for a specific group (admin only)"""
    # Get the group
    group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Get all permissions
    all_permissions = db.query(Permission).all()
    
    # Get group's permissions
    group_permission_ids = {permission.id for permission in group.permissions}
    
    return {
        "group": group.name,
        "permissions": [
            {
                "id": permission.id,
                "name": permission.name,
                "description": permission.description,
                "category": permission.category,
                "assigned": permission.id in group_permission_ids
            }
            for permission in all_permissions
        ]
    }

# Update group permissions - owner only
@router.post("/admin/groups/{group_id}/permissions", status_code=status.HTTP_200_OK)
def update_group_permissions(
    group_id: int,
    permission_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(check_owner_role)
):
    """Update permissions for a specific group (owner only)"""
    # Get the group
    group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Cannot modify owner group permissions
    if group.name == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner group permissions cannot be modified"
        )
    
    # Delete existing permissions
    db.query(GroupPermission).filter(GroupPermission.group_id == group_id).delete()
    
    # Add new permissions
    for permission_id in permission_ids:
        # Check if permission exists
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            group_permission = GroupPermission(group_id=group_id, permission_id=permission_id)
            db.add(group_permission)
    
    db.commit()
    return {"status": "success", "message": "Group permissions updated successfully"}
