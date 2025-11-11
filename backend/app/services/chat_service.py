import json
import httpx
from typing import List, Optional, AsyncGenerator, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.chat import Chat
from ..models.message import Message, SenderType
from ..schemas.chat import ChatCreate, ChatCompletionRequest
from ..schemas.message import MessageCreate, MessageResponse
from ..core.config import settings
from ..services.analytics_service import RealtimeService


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.realtime_service = RealtimeService()

    # 获取用户的所有聊天
    def get_user_chats(self, user_id: UUID) -> List[Chat]:
        return self.db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()

    # 创建新聊天
    def create_chat(self, user_id: UUID, chat_data: ChatCreate) -> Chat:
        # 如果没有提供标题，使用默认标题
        title = chat_data.title or "新的对话"

        # 创建新的聊天会话
        db_chat = Chat(
            title=title,
            user_id=user_id
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat

    # 获取特定聊天
    def get_chat(self, chat_id: UUID, user_id: UUID) -> Optional[Chat]:
        return self.db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()

    # 更新聊天标题
    def update_chat_title(self, chat_id: UUID, user_id: UUID, title: str) -> Optional[Chat]:
        db_chat = self.get_chat(chat_id, user_id)
        if not db_chat:
            return None

        db_chat.title = title
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat

    # 删除聊天
    def delete_chat(self, chat_id: UUID, user_id: UUID) -> bool:
        db_chat = self.get_chat(chat_id, user_id)
        if not db_chat:
            return False

        self.db.delete(db_chat)
        self.db.commit()
        return True

    # 获取聊天历史消息
    def get_chat_messages(self, chat_id: UUID, user_id: UUID) -> List[Message]:
        # 首先验证用户是否有权访问此聊天
        db_chat = self.get_chat(chat_id, user_id)
        if not db_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="聊天不存在"
            )

        return self.db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp.asc()).all()

    # 保存消息到数据库
    def save_message(self, chat_id: UUID, content: str, sender: SenderType) -> Message:
        db_message = Message(
            chat_id=chat_id,
            content=content,
            sender=sender
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        # 广播消息到连接的客户端
        import asyncio
        from ..schemas.message import MessageResponse
        
        message_response = MessageResponse(
            id=db_message.id,
            chat_id=db_message.chat_id,
            content=db_message.content,
            sender=db_message.sender.value,
            timestamp=db_message.timestamp,
            created_at=db_message.created_at
        )
        
        # 异步广播消息
        asyncio.create_task(
            self.realtime_service.broadcast_message(str(chat_id), message_response)
        )
        
        return db_message

    # 调用AI API (GLM)
    async def call_ai_api(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not settings.AI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI API密钥未配置"
            )

        model = model or settings.AI_MODEL

        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json"
        }

        # 添加系统提示
        if settings.SYSTEM_PROMPT and messages and isinstance(messages, list) and messages[0].get("role") != "system":
            messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}] + messages

        payload = {
            "model": model,
            "messages": messages,
            "stream": False  # 非流式请求
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )

            if response.status_code != 200:
                error_detail = f"调用AI API失败 (状态码: {response.status_code}): {response.text}"
                print(f"API调用错误: {error_detail}")  # 添加日志记录
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_detail
                )

            return response.json()

    # 调用DeepSeek API
    async def call_deepseek_api(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not settings.DEEPSEEK_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DeepSeek API密钥未配置"
            )

        model = model or settings.DEEPSEEK_MODEL

        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": False  # 非流式请求
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            )

            if response.status_code != 200:
                error_detail = f"调用DeepSeek API失败 (状态码: {response.status_code}): {response.text}"
                print(f"API调用错误: {error_detail}")  # 添加日志记录
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_detail
                )

            return response.json()

    # 流式调用AI API (GLM)
    async def stream_ai_api(self, messages: List[Dict[str, str]], model: str = None) -> AsyncGenerator[str, None]:
        if not settings.AI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI API密钥未配置"
            )

        model = model or settings.AI_MODEL

        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json"
        }

        # 添加系统提示
        if settings.SYSTEM_PROMPT and messages and isinstance(messages, list) and messages[0].get("role") != "system":
            messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}] + messages

        payload = {
            "model": model,
            "messages": messages,
            "stream": True  # 流式请求
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_detail = f"调用AI API失败 (状态码: {response.status_code}): {error_text}"
                    print(f"流式API调用错误: {error_detail}")  # 添加日志记录
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=error_detail
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        if data == "[DONE]":
                            break
                        try:
                            # 解析JSON并检查内容
                            parsed_data = json.loads(data)
                            # GLM API可能返回不同的结构，确保我们提取正确的内容
                            if "choices" in parsed_data and parsed_data["choices"]:
                                choice = parsed_data["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    # 构造与前端期望的格式一致的响应
                                    formatted_data = {
                                        "choices": [{
                                            "delta": {
                                                "content": choice["delta"]["content"]
                                            }
                                        }]
                                    }
                                    yield json.dumps(formatted_data)
                        except (json.JSONDecodeError, KeyError):
                            continue

    # 流式调用DeepSeek API
    async def stream_deepseek_api(self, messages: List[Dict[str, str]], model: str = None) -> AsyncGenerator[str, None]:
        if not settings.DEEPSEEK_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DeepSeek API密钥未配置"
            )

        model = model or settings.DEEPSEEK_MODEL

        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": True  # 流式请求
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                settings.DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_detail = f"调用DeepSeek API失败 (状态码: {response.status_code}): {error_text}"
                    print(f"流式API调用错误: {error_detail}")  # 添加日志记录
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=error_detail
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        if data == "[DONE]":
                            break
                        try:
                            yield data
                        except json.JSONDecodeError:
                            continue

    # 处理聊天完成请求
    async def complete_chat(self, chat_id: UUID, user_id: UUID, request: ChatCompletionRequest):
        # 验证用户是否有权访问此聊天
        db_chat = self.get_chat(chat_id, user_id)
        if not db_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="聊天不存在"
            )

        # 保存用户消息
        if request.messages and request.messages[-1].role == "user":
            user_message = request.messages[-1].content
            self.save_message(chat_id, user_message, SenderType.USER)

            # 如果是第一条消息且标题为默认的"新的对话"，则更新标题
            if db_chat.title == "新的对话":
                # 截取消息的前30个字符作为标题
                title = user_message[:30] + "..." if len(user_message) > 30 else user_message
                self.update_chat_title(chat_id, user_id, title)

        # 准备发送给DeepSeek API的消息
        api_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        if request.stream:
            # 流式响应
            # 收集所有响应内容以便保存
            ai_content = ""
            
            async def generator():
                nonlocal ai_content
                async for chunk in self.stream_ai_api(api_messages, request.model):
                    # 解析chunk并提取内容
                    try:
                        parsed_chunk = json.loads(chunk)
                        if "choices" in parsed_chunk and parsed_chunk["choices"]:
                            choice = parsed_chunk["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                ai_content += choice["delta"]["content"]
                    except json.JSONDecodeError:
                        pass
                    
                    yield chunk
                
                # 流式响应完成后，保存完整的AI回复
                if ai_content:
                    self.save_message(chat_id, ai_content, SenderType.AI)
            
            return generator()
        else:
            # 非流式响应
            response = await self.call_ai_api(api_messages, request.model)

            # 保存AI回复
            if "choices" in response and response["choices"]:
                ai_content = response["choices"][0]["message"]["content"]
                self.save_message(chat_id, ai_content, SenderType.AI)

            return response

    # 重新生成最后一条AI回复
    async def regenerate_last_ai_response(self, chat_id: UUID, user_id: UUID):
        # 验证用户是否有权访问此聊天
        db_chat = self.get_chat(chat_id, user_id)
        if not db_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="聊天不存在"
            )

        # 获取聊天历史
        messages = self.get_chat_messages(chat_id, user_id)

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="聊天记录为空，无法重新生成"
            )

        # 删除最后一条AI回复
        if messages[-1].sender == SenderType.AI:
            self.db.delete(messages[-1])
            self.db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="最后一条消息不是AI回复，无法重新生成"
            )

        # 准备发送给DeepSeek API的消息
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": "user" if msg.sender == SenderType.USER else "assistant",
                "content": msg.content
            })

        # 调用AI API (GLM)
        response = await self.call_ai_api(api_messages)

        # 保存新的AI回复
        if "choices" in response and response["choices"]:
            ai_content = response["choices"][0]["message"]["content"]
            self.save_message(chat_id, ai_content, SenderType.AI)

        return response
