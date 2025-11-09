from fastapi import APIRouter

from .endpoints import auth, users, chat, speech

api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册用户相关路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])

# 注册聊天相关路由
api_router.include_router(chat.router, prefix="/chats", tags=["聊天"])

# 注册语音识别相关路由
api_router.include_router(speech.router, prefix="/speech", tags=["语音识别"])
