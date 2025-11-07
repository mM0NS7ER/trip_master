from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class TripMasterException(HTTPException):
    """TripMaster 自定义异常基类"""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail={"code": code, "message": message}, headers=headers)

class AuthException(TripMasterException):
    """认证相关异常"""
    pass

class EmailAlreadyExistsException(AuthException):
    """邮箱已存在异常"""
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="EMAIL_ALREADY_EXISTS",
            message=f"邮箱 {email} 已被注册，请使用其他邮箱或尝试登录"
        )

class UsernameAlreadyExistsException(AuthException):
    """用户名已存在异常"""
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="USERNAME_ALREADY_EXISTS",
            message=f"用户名 {username} 已被使用，请选择其他用户名"
        )

class InvalidCredentialsException(AuthException):
    """无效凭据异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_CREDENTIALS",
            message="用户名或密码错误，请检查您的输入",
            headers={"WWW-Authenticate": "Bearer"}
        )

class UserNotFoundException(AuthException):
    """用户未找到异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message="用户不存在"
        )

class InactiveUserException(AuthException):
    """非活跃用户异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="INACTIVE_USER",
            message="用户账户已被禁用，请联系管理员"
        )

class GuestAccountException(AuthException):
    """访客账户异常"""
    def __init__(self, message: str = "访客账户无法执行此操作"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="GUEST_ACCOUNT_LIMITATION",
            message=message
        )

class ValidationException(TripMasterException):
    """验证相关异常"""
    pass

class InvalidEmailException(ValidationException):
    """无效邮箱异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_EMAIL",
            message="邮箱格式不正确"
        )

class WeakPasswordException(ValidationException):
    """弱密码异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="WEAK_PASSWORD",
            message="密码强度不够，请使用包含大小写字母、数字和特殊字符的密码，长度至少为8位"
        )

class PasswordMismatchException(ValidationException):
    """密码不匹配异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="PASSWORD_MISMATCH",
            message="两次输入的密码不一致"
        )

class InvalidUsernameException(ValidationException):
    """无效用户名异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_USERNAME",
            message="用户名格式不正确，请使用3-20个字符，只能包含字母、数字和下划线"
        )

class ServerException(TripMasterException):
    """服务器相关异常"""
    pass

class DatabaseException(ServerException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message
        )

class FileUploadException(ServerException):
    """文件上传异常"""
    def __init__(self, message: str = "文件上传失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="FILE_UPLOAD_ERROR",
            message=message
        )
