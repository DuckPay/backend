from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.utils.database import Base

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Owner, Admin, User, etc.
    is_admin = Column(Boolean, default=False)  # Whether this is an admin group
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False)  # System groups cannot be deleted/edited
    level = Column(Integer, default=5)  # Group level, 0-N, smaller number means higher level
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary="user_groups", back_populates="groups")
    permissions = relationship("Permission", secondary="group_permissions", back_populates="groups")

class UserGroup(Base):
    __tablename__ = "user_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "create_user", "delete_record"
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)  # e.g., "user_management", "record_management"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    groups = relationship("Group", secondary="group_permissions", back_populates="permissions")

class GroupPermission(Base):
    __tablename__ = "group_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TablePermission(Base):
    __tablename__ = "table_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)  # e.g., "records", "categories"
    group_id = Column(Integer, index=True, nullable=False)
    can_access = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_add = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_manage = Column(Boolean, default=False)
    can_modify_table_info = Column(Boolean, default=False)
    can_add_category = Column(Boolean, default=False)
    can_delete_category = Column(Boolean, default=False)
    can_delete_table = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
