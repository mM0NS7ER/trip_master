from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from ..models.user import User

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
    """获取当前用户，如果令牌即将过期则自动续期"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "TOKEN_EXPIRED"},
    )

    # 使用带过期检查的令牌验证
    payload = verify_token_with_exp(token)
    if payload is None:
        raise credentials_exception

    # 检查令牌是否已过期
    if payload.get("expired", False):
        raise token_expired_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # 将字符串转换为UUID
    user_id = UUID(user_id_str)

    # 从数据库获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # 检查令牌是否需要续期
    if should_refresh_token(payload):
        # 创建新的访问令牌
        new_token = create_access_token(data={"sub": str(user.id)})

        # 在响应头中添加新令牌，前端需要处理这个响应头
        # 由于FastAPI依赖注入机制的限制，我们需要使用全局上下文来传递新令牌
        # 这里我们使用请求上下文来存储新令牌
        from starlette.requests import Request
        from starlette.contextvars import ContextVar
        from contextvars import ContextVar

        # 使用全局上下文变量来存储新令牌
        try:
            from .token_refresh_middleware import new_token_context
            new_token_context.set(new_token)
        except Exception as e:
            # 如果设置上下文变量失败，至少记录日志
            import logging
            logging.error(f"Failed to set new token in context: {str(e)}")

    return user