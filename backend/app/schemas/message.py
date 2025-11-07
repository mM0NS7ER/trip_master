from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

# 基础消息模型
class MessageBase(BaseModel):
    content: str
    sender: str = Field(..., pattern="^(user|ai)$")  # 限制只能是"user"或"ai"

# 创建消息请求模型
class MessageCreate(MessageBase):
    chat_id: UUID

# 消息响应模型
class MessageResponse(MessageBase):
    id: UUID
    chat_id: UUID
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# 消息列表响应模型
class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
