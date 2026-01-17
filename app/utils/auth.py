from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.jwt import decode_access_token
from app.crud.user import get_user_by_username
from app.schemas.user import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# Get current user dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
    
	payload = decode_access_token(token)
	if payload is None:
		raise credentials_exception
    
	username: str = payload.get("sub")
	user_id: int = payload.get("user_id")
	groups: list = payload.get("groups", [])
    
	if username is None:
		raise credentials_exception
    
	token_data = TokenData(username=username, user_id=user_id, groups=groups)
	user = get_user_by_username(db, username=token_data.username)
    
	if user is None:
		raise credentials_exception
    
	return user

# Role check dependency
def get_current_active_user(current_user = Depends(get_current_user)):
	return current_user

# Check if user has admin or owner group
def check_admin_role(current_user = Depends(get_current_user)):	# Check if user has owner group, admin group, or any group with is_admin=True
	# Check if any group has is_admin=True (owner and admin groups should have is_admin=True)
	has_admin_group = any(group.is_admin for group in current_user.groups)
	if not has_admin_group:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin access required",
		)
	return current_user

# Check if user has owner group
def check_owner_role(current_user = Depends(get_current_user)):
	# Check if user has any group with special owner permissions (by checking if any group is the owner group)
	user_groups = [group.name for group in current_user.groups]
	if "owner" not in user_groups:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Owner access required",
		)
	return current_user

# Check if user can edit a specific user
def can_edit_user(current_user, user_to_edit):	# Get user groups
	current_user_groups = [group.name for group in current_user.groups]
	user_to_edit_groups = [group.name for group in user_to_edit.groups]
	
	# Owner can edit any user
	if "owner" in current_user_groups:
		return True
	
	# Calculate user levels - find the highest level (smallest number) for each user
	current_user_level = min(group.level for group in current_user.groups)
	user_to_edit_level = min(group.level for group in user_to_edit.groups)
	
	# Check if current user has admin group or any group with is_admin=True
	is_admin = any(group.is_admin for group in current_user.groups)
	
	# User can only edit users with lower or equal level than themselves
	# Low level group (smaller number) can edit higher level groups (larger numbers)
	# Higher level groups (larger numbers) cannot edit lower level groups (smaller numbers)
	if is_admin:
		# Check if current user's level is lower than or equal to user to edit's level
		# (current user has higher or equal privilege)
		return current_user_level <= user_to_edit_level
	
	# Regular users can't edit anyone
	return False

# Check if user can change a user's role
def can_change_role(current_user, user_to_change, new_group):	# Get current user groups
	current_groups = [group.name for group in current_user.groups]
	user_to_change_groups = [group.name for group in user_to_change.groups]
	
	# Owner can change any role
	if "owner" in current_groups:
		return True
	
	# Calculate user levels - find the highest level (smallest number) for each user
	current_user_level = min(group.level for group in current_user.groups)
	user_to_change_level = min(group.level for group in user_to_change.groups)
	
	# Check if current user has admin group or any group with is_admin=True
	is_admin = any(group.is_admin for group in current_user.groups)
	
	# User can only change roles of users with lower or equal level than themselves
	# Low level group (smaller number) can change roles of higher level groups (larger numbers)
	# Higher level groups (larger numbers) cannot change roles of lower level groups (smaller numbers)
	if is_admin and current_user_level <= user_to_change_level:
		# Check if user to change is a regular user (no is_admin groups) or has higher level
		is_user_to_change_admin = any(group.is_admin for group in user_to_change.groups)
		return not is_user_to_change_admin and new_group == "admin"
	
	# Regular users or users with higher level can't change roles
	return False

# Check if user has a specific permission
def has_permission(current_user, permission_name):	# Check if user has any group that is owner (special case)
	is_owner = any(group.name == "owner" for group in current_user.groups)
	if is_owner:
		return True
	
	# Check if user has the permission through any of their groups
	for group in current_user.groups:
		for permission in group.permissions:
			if permission.name == permission_name:
				return True
	
	# User doesn't have the permission
	return False

# Check if user has any of the specified permissions
def has_any_permission(current_user, permission_names):	# Check if user has any group that is owner (special case)
	is_owner = any(group.name == "owner" for group in current_user.groups)
	if is_owner:
		return True
	
	# Check if user has any of the permissions through any of their groups
	for group in current_user.groups:
		for permission in group.permissions:
			if permission.name in permission_names:
				return True
	
	# User doesn't have any of the permissions
	return False

# Permission check dependencies
def check_permission(permission_name):
	def dependency(current_user = Depends(get_current_user)):
		if not has_permission(current_user, permission_name):
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Permission denied",
			)
		return current_user
	return dependency

# Check if user is owner (owner group is special and cannot be modified)
def check_owner(current_user = Depends(get_current_user)):
	user_groups = [group.name for group in current_user.groups]
	if "owner" not in user_groups:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Owner access required",
		)
	return current_user
