from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .exceptions import TripMasterException

async def trip_master_exception_handler(request: Request, exc: TripMasterException):
    """处理TripMaster自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "code": exc.detail["code"],
                "message": exc.detail["message"]
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """处理标准HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "errors": errors
            }
        }
    )
