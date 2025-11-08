from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .api import api_router
from .core.config import settings
from .core.exceptions import TripMasterException
from .core.exception_handlers import (
    trip_master_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from .core.token_refresh_middleware import TokenRefreshMiddleware

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Trip Master API - 旅行规划师后端服务",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册全局异常处理器
app.add_exception_handler(TripMasterException, trip_master_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加令牌刷新中间件
app.add_middleware(TokenRefreshMiddleware)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 根路径
@app.get("/")
async def root():
    return {"message": "欢迎使用 Trip Master API"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
