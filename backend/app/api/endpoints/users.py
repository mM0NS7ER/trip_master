from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User
from ...schemas.user import (
    User, UserUpdate, AvatarUploadResponse,
    MessageResponse, PasswordResetRequest
)
from ...services.user_service import UserService
from ...utils.auth import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=User)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新当前用户信息"""
    user = UserService.update_user(db, user_id=current_user.id, user_update=user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.post("/me/avatar", response_model=AvatarUploadResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """上传用户头像"""
    # 在实际应用中，这里应该将文件上传到云存储服务
    # 这里我们模拟上传过程并返回一个模拟的URL

    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )

    # 模拟上传过程
    import uuid
    filename = f"{uuid.uuid4()}.{file.content_type.split('/')[-1]}"
    avatar_url = f"https://example.com/avatars/{filename}"

    # 更新用户头像URL
    user = UserService.update_avatar(db, user_id=current_user.id, avatar_url=avatar_url)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return {"avatar_url": avatar_url}

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """重置密码"""
    # 在实际应用中，这里应该发送密码重置邮件
    # 这里我们仅返回成功消息

    # 检查用户是否存在
    user = UserService.get_user_by_email(db, email=password_reset.email)
    if not user:
        # 为了安全，即使用户不存在也返回成功消息
        return {"message": "密码重置邮件已发送"}

    # 这里应该生成密码重置令牌并发送邮件
    # 为了演示，我们仅返回成功消息
    return {"message": "密码重置邮件已发送"}