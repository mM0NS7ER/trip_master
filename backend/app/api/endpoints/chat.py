import json
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.chat import (
    ChatCreate, 
    ChatResponse, 
    ChatListResponse,
    ChatDetailResponse,
    ChatUpdateTitle,
    ChatCompletionRequest
)
from ...schemas.message import MessageListResponse
from ...services.chat_service import ChatService

router = APIRouter()


# 获取用户聊天列表
@router.get("/", response_model=ChatListResponse)
async def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有聊天会话"""
    chat_service = ChatService(db)
    chats = chat_service.get_user_chats(current_user.id)
    return {"chats": chats}


# 创建新聊天会话
@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    chat_service = ChatService(db)
    new_chat = chat_service.create_chat(current_user.id, chat_data)
    return new_chat


# 获取特定聊天详情
@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取特定聊天的详细信息"""
    chat_service = ChatService(db)
    chat = chat_service.get_chat(chat_id, current_user.id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天不存在"
        )

    return chat


# 发送消息并获取AI回复
@router.post("/{chat_id}/completions")
async def complete_chat(
    chat_id: UUID,
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息并获取AI回复，支持流式和非流式响应"""
    chat_service = ChatService(db)

    # 验证聊天是否存在
    chat = chat_service.get_chat(chat_id, current_user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天不存在"
        )

    if request.stream:
        # 流式响应
        # 等待异步生成器
        chat_generator = await chat_service.complete_chat(chat_id, current_user.id, request)
        
        async def generate():
            try:
                async for chunk in chat_generator:
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
            }
        )
    else:
        # 非流式响应
        response = await chat_service.complete_chat(chat_id, current_user.id, request)
        return {"success": True, "data": response}


# 获取聊天历史
@router.get("/{chat_id}/messages", response_model=MessageListResponse)
async def get_chat_messages(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取特定聊天的所有消息历史"""
    chat_service = ChatService(db)
    messages = chat_service.get_chat_messages(chat_id, current_user.id)
    return {"messages": messages}


# 更新聊天标题
@router.put("/{chat_id}/title", response_model=ChatResponse)
async def update_chat_title(
    chat_id: UUID,
    title_data: ChatUpdateTitle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新聊天标题"""
    chat_service = ChatService(db)
    updated_chat = chat_service.update_chat_title(chat_id, current_user.id, title_data.title)

    if not updated_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天不存在"
        )

    return updated_chat


# 删除聊天会话
@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    chat_service = ChatService(db)
    success = chat_service.delete_chat(chat_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天不存在"
        )

    return {"success": True, "message": "会话已删除"}


# 重新生成最后一条AI回复
@router.post("/{chat_id}/regenerate")
async def regenerate_last_ai_response(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新生成最后一条AI回复"""
    chat_service = ChatService(db)

    try:
        response = await chat_service.regenerate_last_ai_response(chat_id, current_user.id)
        return {"success": True, "data": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新生成失败: {str(e)}"
        )
