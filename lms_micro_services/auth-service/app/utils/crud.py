from app.models.user import User, RefreshToken, PasswordResetToken
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserRole
from app.core.security import get_password_hash, verify_password
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100, role: Optional[UserRole] = None, is_active: Optional[bool] = None) -> List[User]:
        """Get list of users with filtering"""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()

    def get_users_created_by(self, creator_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users created by specific teacher/admin"""
        return self.db.query(User).filter(User.created_by == creator_id).offset(skip).limit(limit).all()

    def count_users(self, role: Optional[UserRole] = None, is_active: Optional[bool] = None) -> int:
        """Count users with filtering"""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
            
        return query.count()

    def create_user(self, user: UserCreate, created_by_user_id: Optional[int] = None) -> User:
        """Create new user"""
        hashed_password = get_password_hash(user.password)
        
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_by=created_by_user_id
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        update_data = user.dict(exclude_unset=True)
        
        # Hash password if provided
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = get_password_hash(update_data['password'])
            del update_data['password']  # Remove plain password from update_data
        
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False

        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False

        db_user.last_login = datetime.utcnow()
        self.db.commit()
        return True

    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False

        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password"""
        # Try username first, then email
        user = self.get_user_by_username(username)
        if not user:
            user = self.get_user_by_email(username)
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user

    def is_username_taken(self, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if username is already taken"""
        query = self.db.query(User).filter(User.username == username)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    def is_email_taken(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is already taken"""
        query = self.db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

class RefreshTokenCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Create new refresh token"""
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_active == True,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).first()

    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke refresh token"""
        db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not db_token:
            return False

        db_token.is_active = False
        self.db.commit()
        return True

    def revoke_user_tokens(self, user_id: int) -> bool:
        """Revoke all refresh tokens for a user"""
        self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_active == True
            )
        ).update({"is_active": False})
        
        self.db.commit()
        return True

    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        deleted_count = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return deleted_count

class PasswordResetTokenCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_reset_token(self, user_id: int, token: str, expires_at: datetime) -> PasswordResetToken:
        """Create new password reset token"""
        # Invalidate any existing unused tokens for this user
        self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used == False
            )
        ).update({"is_used": True})

        db_token = PasswordResetToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get valid password reset token"""
        return self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        ).first()

    def use_reset_token(self, token: str) -> bool:
        """Mark reset token as used"""
        db_token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not db_token:
            return False

        db_token.is_used = True
        self.db.commit()
        return True

    def cleanup_expired_tokens(self) -> int:
        """Remove expired reset tokens"""
        deleted_count = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return deleted_count

# Convenience functions
def get_user_crud(db: Session = None) -> UserCRUD:
    """Get UserCRUD instance"""
    if db is None:
        db = next(get_db())
    return UserCRUD(db)

def get_refresh_token_crud(db: Session = None) -> RefreshTokenCRUD:
    """Get RefreshTokenCRUD instance"""
    if db is None:
        db = next(get_db())
    return RefreshTokenCRUD(db)

def get_password_reset_crud(db: Session = None) -> PasswordResetTokenCRUD:
    """Get PasswordResetTokenCRUD instance"""
    if db is None:
        db = next(get_db())
    return PasswordResetTokenCRUD(db)
