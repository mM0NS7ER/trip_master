from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
import logging

# 创建上下文变量来存储新令牌
new_token_context: ContextVar = ContextVar('new_token')

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """令牌刷新中间件，用于在响应中添加新的访问令牌"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 处理请求
        response = await call_next(request)

        # 检查是否有新令牌需要添加到响应头中
        try:
            new_token = new_token_context.get(None)
            if new_token:
                response.headers["X-New-Token"] = new_token
                logging.info(f"Added new token to response headers")
        except LookupError:
            # 没有新令牌，不需要处理
            pass
        except Exception as e:
            logging.error(f"Error adding new token to response: {str(e)}")

        return response
