from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, get_supabase
from ..models.user import User
from ..services.auth_service import AuthService

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    # bcrypt密码长度限制为72字节，截断过长的密码
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌并返回载荷"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_token_with_exp(token: str) -> Optional[dict]:
    """验证令牌并返回载荷，包括过期时间"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # 令牌已过期，但仍然返回载荷，以便检查过期时间
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
            payload["expired"] = True
            return payload
        except JWTError:
            return None
    except JWTError:
        return None

def should_refresh_token(payload: dict) -> bool:
    """检查令牌是否需要续期"""
    if not payload:
        return False

    # 如果令牌已过期，需要续期
    if payload.get("expired", False):
        return True

    # 获取令牌过期时间
    exp = payload.get("exp")
    if not exp:
        return False

    # 计算剩余时间（秒）
    from datetime import datetime
    now = datetime.utcnow()
    exp_datetime = datetime.fromtimestamp(exp)
    remaining_seconds = (exp_datetime - now).total_seconds()

    # 如果剩余时间少于阈值，需要续期
    threshold_seconds = settings.TOKEN_REFRESH_THRESHOLD_MINUTES * 60
    return remaining_seconds < threshold_seconds

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（使用Supabase Auth）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 使用Supabase验证令牌
        auth_service = AuthService()
        # 尝试从请求头中获取refresh_token
        # 这里暂时使用空字符串，因为从请求中获取refresh_token需要额外的实现
        supabase_user = auth_service.get_current_user(access_token=token, refresh_token="")
        
        if supabase_user is None:
            raise credentials_exception
        
        # 从数据库获取用户
        user_id = UUID(supabase_user["id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None:
            # 如果用户不在本地数据库中，尝试同步
            user = auth_service.sync_supabase_user_to_db(
                db=db,
                supabase_user_id=supabase_user["id"],
                email=supabase_user["email"],
                user_data=supabase_user["user_metadata"] or {}
            )
        
        return user
    except Exception as e:
        print(f"验证用户失败: {str(e)}")
        raise credentials_exception