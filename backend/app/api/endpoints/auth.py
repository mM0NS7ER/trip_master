from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import traceback

from ...core.database import get_db
from ...core.security import create_access_token
from ...core.config import settings
from ...core.exceptions import (
    EmailAlreadyExistsException, UsernameAlreadyExistsException,
    InvalidCredentialsException, DatabaseException, WeakPasswordException
)
import re
from ...schemas.user import (
    UserCreate, UserLogin, UserWithToken, UserAndToken,
    GuestUserWithToken, MessageResponse, ErrorResponse
)
from ...services.user_service import UserService

router = APIRouter()

@router.post("/signup", response_model=UserAndToken)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册"""
    print(f"收到的注册数据: {user_data.dict()}")
    # 检查邮箱是否已存在
    user = UserService.get_user_by_email(db, email=user_data.email)
    if user:
        print(f"邮箱已被使用: {user_data.email}")
        raise EmailAlreadyExistsException(user_data.email)

    # 检查用户名是否已存在
    user = UserService.get_user_by_username(db, username=user_data.username)
    if user:
        print(f"用户名已被使用: {user_data.username}")
        raise UsernameAlreadyExistsException(user_data.username)

    # 验证密码强度
    if len(user_data.password) < 6:
        raise WeakPasswordException()


    # 创建新用户
    try:
        print(f"准备创建用户，数据: {user_data.dict()}")
        user = UserService.create_user(db, user_data)
        print(f"用户创建成功: {user.id}")
    except Exception as e:
        print(f"创建用户时出错: {str(e)}")
        traceback.print_exc()
        raise DatabaseException(f"创建用户失败: {str(e)}")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "user": user,
        "token": access_token
    }

@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """OAuth2兼容的登录接口"""
    # 验证用户凭据
    user = UserService.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise InvalidCredentialsException()

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signin", response_model=UserAndToken)
def signin(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    # 验证用户凭据
    user = UserService.authenticate_user(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise InvalidCredentialsException()

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "user": user,
        "token": access_token
    }

@router.post("/guest", response_model=UserAndToken)
def guest_signin(db: Session = Depends(get_db)) -> Any:
    """访客登录"""
    # 创建访客用户
    user = UserService.create_guest_user(db)

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "user": user,
        "token": access_token
    }

@router.post("/signout", response_model=MessageResponse)
def signout() -> Any:
    """用户登出"""
    # 在实际应用中，这里可以将令牌加入黑名单
    # 目前仅返回成功消息
    return {"message": "登出成功"}