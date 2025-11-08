from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_token, verify_token_with_exp, should_refresh_token, create_access_token
from ..models.user import User
from ..services.user_service import UserService

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/signin")

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

    user_id: UUID = UUID(payload.get("sub"))
    if user_id is None:
        raise credentials_exception

    user = UserService.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    # 检查令牌是否需要续期
    if should_refresh_token(payload):
        # 创建新的访问令牌
        new_token = create_access_token(data={"sub": str(user_id)})

        # 使用全局上下文变量来存储新令牌
        try:
            from ..core.token_refresh_middleware import new_token_context
            new_token_context.set(new_token)
        except Exception as e:
            # 如果设置上下文变量失败，至少记录日志
            import logging
            logging.error(f"Failed to set new token in context: {str(e)}")

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前已验证用户"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户邮箱未验证"
        )
    return current_user
