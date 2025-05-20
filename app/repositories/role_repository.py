from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import RoleModel, Role
from app.repositories.base_repository import BaseRepository

class RoleRepository:
    """Repository for Role model operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_role(self, role: Role) -> Optional[RoleModel]:
        """Get role by enum value"""
        return self.db.query(RoleModel).filter(RoleModel.role == role).first()
    
    def create_role(self, role: Role) -> RoleModel:
        """Create new role"""
        role_obj = RoleModel(role=role)
        self.db.add(role_obj)
        self.db.commit()
        self.db.refresh(role_obj)
        return role_obj
    
    def get_or_create(self, role: Role) -> RoleModel:
        """Get role or create if it doesn't exist"""
        role_obj = self.get_by_role(role)
        if not role_obj:
            role_obj = self.create_role(role)
        return role_obj