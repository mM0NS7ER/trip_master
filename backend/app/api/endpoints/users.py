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
    """重置密码（使用Supabase Auth）"""
    try:
        # 使用Supabase发送密码重置邮件
        auth_service = AuthService()
        auth_service.reset_password(email=password_reset.email)
        return {"message": "密码重置邮件已发送"}
    except Exception as e:
        print(f"发送密码重置邮件失败: {str(e)}")
        # 为了安全，即使发送失败也返回成功消息
        return {"message": "密码重置邮件已发送"}