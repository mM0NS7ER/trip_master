from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

# 基础用户模型
class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: str
    age: Optional[int] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_guest: bool = False

# 用户注册请求模型
class UserCreate(UserBase):
    password: str

# 用户登录请求模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 用户更新请求模型
class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None

# 用户响应模型
class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 用户令牌响应模型
class UserWithToken(User):
    token: str

# 用户和令牌分离的响应模型
class UserAndToken(BaseModel):
    user: User
    token: str

# 访客用户模型
class GuestUser(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# 访客用户令牌响应模型
class GuestUserWithToken(GuestUser):
    token: str

# 密码重置请求模型
class PasswordResetRequest(BaseModel):
    email: EmailStr

# 头像上传响应模型
class AvatarUploadResponse(BaseModel):
    avatar_url: str

# 通用响应模型
class MessageResponse(BaseModel):
    message: str

# 错误响应模型
class ErrorResponse(BaseModel):
    code: str
    message: str
