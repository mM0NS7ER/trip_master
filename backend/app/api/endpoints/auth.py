from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
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
from ...services.auth_service import AuthService

router = APIRouter()

@router.post("/signup", response_model=UserAndToken)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册（使用Supabase Auth）"""
    print(f"收到的注册数据: {user_data.dict()}")

    # 验证密码强度
    if len(user_data.password) < 6:
        raise WeakPasswordException()

    # 准备用户数据
    user_metadata = {
        "username": user_data.username,
        "name": user_data.name,
        "age": user_data.age,
        "bio": user_data.bio,
        "avatar_url": user_data.avatar_url
    }

    # 使用Supabase Auth创建用户
    try:
        auth_service = AuthService()
        response = auth_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            user_data=user_metadata
        )

        # 将Supabase用户同步到本地数据库
        user = auth_service.sync_supabase_user_to_db(
            db=db,
            supabase_user_id=response["user"].id,
            email=user_data.email,
            user_data=user_metadata
        )

        # 处理Supabase注册后的session
        if response["session"] is not None:
            # 如果有session，直接使用
            access_token = response["session"].access_token
        else:
            # 如果没有session（需要邮箱验证），尝试自动登录
            try:
                login_response = auth_service.sign_in(
                    email=user_data.email,
                    password=user_data.password
                )
                access_token = login_response["session"].access_token
            except Exception as login_error:
                # 如果自动登录也失败，返回提示信息
                print(f"自动登录失败: {str(login_error)}")
                return {
                    "user": user,
                    "token": None,
                    "message": "注册成功，但需要验证邮箱后才能登录。请检查您的邮箱。"
                }

        return {
            "user": user,
            "token": access_token
        }
    except Exception as e:
        print(f"注册失败: {str(e)}")
        traceback.print_exc()
        if "already registered" in str(e).lower():
            raise EmailAlreadyExistsException(user_data.email)
        raise DatabaseException(f"注册失败: {str(e)}")

@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """OAuth2兼容的登录接口（使用Supabase Auth）"""
    try:
        # 使用Supabase进行身份验证
        auth_service = AuthService()
        response = auth_service.sign_in(
            email=form_data.username,
            password=form_data.password
        )

        # 将Supabase用户同步到本地数据库
        user = auth_service.sync_supabase_user_to_db(
            db=db,
            supabase_user_id=response["user"].id,
            email=form_data.username,
            user_data=response["user"].user_metadata or {}
        )

        # 使用Supabase的会话令牌
        access_token = response["session"].access_token

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"登录失败: {str(e)}")
        traceback.print_exc()
        raise InvalidCredentialsException()

@router.post("/signin", response_model=UserAndToken)
def signin(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录（使用Supabase Auth）"""
    print(f"收到登录请求: {user_credentials.email}")
    try:
        # 使用Supabase进行身份验证
        auth_service = AuthService()
        response = auth_service.sign_in(
            email=user_credentials.email,
            password=user_credentials.password
        )

        # 将Supabase用户同步到本地数据库
        user = auth_service.sync_supabase_user_to_db(
            db=db,
            supabase_user_id=response["user"].id,
            email=user_credentials.email,
            user_data=response["user"].user_metadata or {}
        )

        # 使用Supabase的会话令牌
        access_token = response["session"].access_token

        return {
            "user": user,
            "token": access_token
        }
    except Exception as e:
        print(f"登录失败: {str(e)}")
        traceback.print_exc()
        raise InvalidCredentialsException()

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
def signout(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login"))
) -> Any:
    """用户登出（使用Supabase Auth）"""
    try:
        # 使用Supabase进行登出
        auth_service = AuthService()
        auth_service.sign_out(access_token=token)
        return {"message": "登出成功"}
    except Exception as e:
        print(f"登出失败: {str(e)}")
        traceback.print_exc()
        # 即使Supabase登出失败，也返回成功消息，因为客户端可以清除本地令牌
        return {"message": "登出成功"}
