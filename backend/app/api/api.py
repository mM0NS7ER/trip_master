from fastapi import APIRouter

from .endpoints import auth, users

api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册用户相关路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])
