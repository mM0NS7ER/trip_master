from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from .message import MessageResponse

# 基础聊天模型
class ChatBase(BaseModel):
    title: Optional[str] = None

# 创建聊天请求模型
class ChatCreate(ChatBase):
    session_id: Optional[UUID] = None
    title: Optional[str] = None

# 聊天响应模型
class ChatResponse(ChatBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 聊天列表响应模型
class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

# 聊天详情响应模型
class ChatDetailResponse(ChatResponse):
    messages: Optional[List[MessageResponse]] = None

# 更新聊天标题请求模型
class ChatUpdateTitle(BaseModel):
    title: str

# 消息请求模型
class MessageRequest(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str

# 聊天完成请求模型
class ChatCompletionRequest(BaseModel):
    messages: List[MessageRequest]
    stream: bool = True
    model: str = "deepseek-chat"
