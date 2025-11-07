from typing import Optional

from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """创建新用户"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            name=user.name,
            hashed_password=hashed_password,
            age=user.age,
            bio=user.bio,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_guest=user.is_guest
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def create_guest_user(db: Session) -> User:
        """创建访客用户"""
        # 生成唯一的访客用户名
        import uuid
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"

        db_user = User(
            email="guest@example.com",
            username=guest_username,
            name="访客用户",
            hashed_password=None,  # 访客用户没有密码
            is_active=True,
            is_verified=False,
            is_guest=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not user.hashed_password:  # 访客用户没有密码
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[User]:
        """更新用户头像"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        db_user.avatar_url = avatar_url
        db.commit()
        db.refresh(db_user)
        return db_user
