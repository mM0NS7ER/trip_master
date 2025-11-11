from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...services.analytics_service import RealtimeService

router = APIRouter()

# 创建实时服务实例
realtime_service = RealtimeService()

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    chat_id: str,
    token: str = None,
    db: Session = Depends(get_db)
):
    """WebSocket端点，用于实时聊天"""
    # 验证用户身份
    if not token:
        await websocket.close(code=4001, reason="未提供认证令牌")
        return

    try:
        # 使用Supabase验证令牌
        from ...services.auth_service import AuthService
        auth_service = AuthService()
        # 添加refresh_token参数，暂时使用空字符串
        supabase_user = auth_service.get_current_user(access_token=token, refresh_token="")

        if not supabase_user:
            await websocket.close(code=4001, reason="无效的认证令牌")
            return

        # 从数据库获取用户
        user_id = UUID(supabase_user["id"])
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            await websocket.close(code=4001, reason="用户不存在")
            return

        # 连接到实时服务
        await realtime_service.connect(websocket, chat_id)

        try:
            # 保持连接活跃
            while True:
                # 等待客户端消息
                data = await websocket.receive_text()
                # 这里可以处理客户端发送的消息，如心跳包等
        except WebSocketDisconnect:
            # 客户端断开连接
            realtime_service.disconnect(websocket, chat_id)
    except Exception as e:
        print(f"WebSocket连接错误: {str(e)}")
        await websocket.close(code=4000, reason="连接错误")
