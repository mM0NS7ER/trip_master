
import { useState, useEffect, useRef } from "react"
import WelcomeSection from "./WelcomeSection"
import InputSection from "./InputSection"

interface Message {
  id: string
  text: string
  sender: "user" | "ai"
  timestamp: string
}

interface ChatAreaProps {
  sessionId: string
  onCreateSession?: () => Promise<string | null>
  onMessageSent?: () => void  // 添加回调函数，用于通知父组件消息已发送
}

const ChatArea = ({ sessionId, onCreateSession, onMessageSent }: ChatAreaProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // 每当消息更新时，滚动到底部
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 从后端加载历史消息
  useEffect(() => {
    // 如果是新会话，不检查会话是否存在，等待用户发送第一条消息时再创建
    if (sessionId === "new") {
      return;
    }

    // 检查会话是否存在并获取历史消息
    const checkSessionAndLoadMessages = async () => {
      try {
        const token = localStorage.getItem('token');

        // 检查会话是否存在
        const response = await fetch(`http://localhost:8000/api/chats/${sessionId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          // 会话不存在，创建新会话
          const createResponse = await fetch('http://localhost:8000/api/chats/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({})
          });

          if (createResponse.ok) {
            const data = await createResponse.json();
            // 重定向到新创建的会话
            window.location.href = `/chat/${data.id}`;
            return;
          }
        }

        // 会话存在，从后端获取历史消息
        try {
          const messagesResponse = await fetch(`http://localhost:8000/api/chats/${sessionId}/messages`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          });

          if (messagesResponse.ok) {
            const messagesData = await messagesResponse.json();
            console.log("从后端获取的消息数据:", messagesData); // 调试日志

            // 转换后端消息格式为前端需要的格式
            // 修复：使用msg.sender而不是msg.role
            const formattedMessages = messagesData.messages.map((msg: any) => {
              // 确保sender字段正确设置
              const sender = msg.sender === "user" ? "user" : "ai";
              console.log(`消息ID: ${msg.id}, 发送者: ${msg.sender}, 转换后: ${sender}`); // 调试日志

              return {
                id: msg.id,
                text: msg.content,
                sender: sender,
                timestamp: new Date(msg.created_at).toLocaleTimeString()
              };
            });

            console.log("格式化后的消息:", formattedMessages); // 调试日志
            setMessages(formattedMessages);
            // 同时保存到localStorage作为缓存
            localStorage.setItem(`chat_${sessionId}`, JSON.stringify(formattedMessages));
          } else {
            // 如果获取消息失败，尝试从localStorage加载
            const savedMessages = localStorage.getItem(`chat_${sessionId}`);
            if (savedMessages) {
              setMessages(JSON.parse(savedMessages));
            }
          }
        } catch (error) {
          console.error("获取历史消息出错:", error);
          // 出错时尝试从localStorage加载
          const savedMessages = localStorage.getItem(`chat_${sessionId}`);
          if (savedMessages) {
            setMessages(JSON.parse(savedMessages));
          }
        }
      } catch (error) {
        console.error("检查会话出错:", error);
        // 出错时尝试从localStorage加载
        const savedMessages = localStorage.getItem(`chat_${sessionId}`);
        if (savedMessages) {
          setMessages(JSON.parse(savedMessages));
        }
      }
    };

    checkSessionAndLoadMessages();
  }, [sessionId])

  // 保存消息到localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages))
    }
  }, [messages, sessionId])

  // 处理发送消息
  const handleSendMessage = async (message: Message) => {
    // 如果是新会话且还没有创建实际会话ID，先创建会话
    let actualSessionId: string | null = sessionId;
    if (sessionId === "new" && onCreateSession) {
      actualSessionId = await onCreateSession();
      if (!actualSessionId) {
        return;
      }
    }


    // 添加用户消息
    setMessages(prevMessages => [...prevMessages, message])

    try {
      // 从localStorage获取token
      const token = localStorage.getItem('token');

      // 准备API请求
      const response = await fetch(`http://localhost:8000/api/chats/${actualSessionId}/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          messages: [
            { role: "user", content: message.text }
          ],
          stream: true,
          model: "glm-4"
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取AI回复失败');
      }

      // 处理流式响应
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let aiResponseText = "";

      // 创建一个空的AI消息，稍后更新

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "",
        sender: "ai",
        timestamp: new Date().toLocaleTimeString()
      };

      // 添加空的AI消息
      setMessages(prevMessages => [...prevMessages, aiResponse]);

      if (reader) {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                try {
                  const data = JSON.parse(line.substring(6));
                  if (data.choices && data.choices[0] && data.choices[0].delta && data.choices[0].delta.content) {
                    aiResponseText += data.choices[0].delta.content;

                    // 更新AI消息
                    setMessages(prevMessages =>
                      prevMessages.map(msg =>
                        msg.id === aiResponse.id
                          ? { ...msg, text: aiResponseText }
                          : msg
                      )
                    );
                  }
                } catch (e) {
                  console.error("解析流式数据错误:", e);
                }
              }
            }
          }

          // 消息发送完成后，调用回调函数通知父组件更新聊天历史
          if (onMessageSent) {
            onMessageSent();
          }
        } catch (error) {
          console.error("读取流式响应错误:", error);
          throw error;
        }
      }
    } catch (error) {
      console.error("获取AI回复出错:", error);

      // 错误时添加一个包含详细错误信息的回复
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: (() => {
          const errorMsg = error instanceof Error ? error.message : "未知错误";
          if (errorMsg.includes("Insufficient Balance")) {
            return "抱歉，API服务暂时不可用，可能是账户余额不足。请联系管理员充值。";
          }
          return `抱歉，我现在无法回复。错误信息：${errorMsg}`;
        })(),
        sender: "ai",
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prevMessages => [...prevMessages, errorResponse]);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <WelcomeSection />
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    message.sender === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  <p>{message.text}</p>
                  <p className={`text-xs mt-1 ${message.sender === "user" ? "text-blue-100" : "text-gray-500"}`}>
                    {message.timestamp}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      <InputSection onSendMessage={handleSendMessage} />
    </div>
  )
}

export default ChatArea
