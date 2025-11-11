from typing import Dict, Any, List
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from supabase import Client

from ..core.database import get_supabase
from ..models.message import Message, SenderType
from ..schemas.message import MessageResponse


class RealtimeService:
    """实时服务类，处理Supabase的实时功能"""
    
    def __init__(self):
        try:
            self.supabase: Client = get_supabase()
        except Exception as e:
            print(f"Supabase客户端不可用，实时功能将被禁用: {str(e)}")
            self.supabase = None
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        """接受WebSocket连接并订阅聊天频道"""
        await websocket.accept()
        
        # 将连接添加到活动连接字典
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)
        
        # 只有在Supabase可用时才订阅实时消息
        if self.supabase is not None:
            try:
                self.supabase.realtime.subscribe(
                    f"public:messages:chat_id=eq.{chat_id}",
                    event="INSERT",
                    callback=lambda payload: self._handle_new_message(chat_id, payload)
                )
            except Exception as e:
                print(f"订阅实时消息失败: {str(e)}")
    
    def disconnect(self, websocket: WebSocket, chat_id: str):
        """断开WebSocket连接"""
        if chat_id in self.active_connections:
            if websocket in self.active_connections[chat_id]:
                self.active_connections[chat_id].remove(websocket)
            
            # 如果没有更多连接，取消订阅
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]
    
    async def _handle_new_message(self, chat_id: str, payload: Dict[str, Any]):
        """处理新消息事件"""
        try:
            # 解析Supabase实时事件载荷
            if "record" in payload:
                message_data = payload["record"]
                
                # 只处理AI消息，用户消息已经由发送方知道
                if message_data.get("sender") == SenderType.AI.value:
                    # 向该聊天室的所有连接发送消息
                    if chat_id in self.active_connections:
                        message_json = json.dumps({
                            "type": "new_message",
                            "data": {
                                "id": message_data.get("id"),
                                "chat_id": message_data.get("chat_id"),
                                "content": message_data.get("content"),
                                "sender": message_data.get("sender"),
                                "timestamp": message_data.get("timestamp")
                            }
                        })
                        
                        # 向所有连接的客户端发送消息
                        for connection in self.active_connections[chat_id]:
                            try:
                                await connection.send_text(message_json)
                            except Exception as e:
                                print(f"发送消息失败: {str(e)}")
        except Exception as e:
            print(f"处理实时消息失败: {str(e)}")
    
    async def broadcast_message(self, chat_id: str, message: MessageResponse):
        """向聊天室广播消息（用于本地消息）"""
        if chat_id in self.active_connections:
            message_json = json.dumps({
                "type": "new_message",
                "data": message.dict()
            })
            
            # 向所有连接的客户端发送消息
            for connection in self.active_connections[chat_id]:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"发送消息失败: {str(e)}")