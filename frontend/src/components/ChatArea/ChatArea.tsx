
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
}

const ChatArea = ({ sessionId }: ChatAreaProps) => {
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

  // 从localStorage加载历史消息
  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat_${sessionId}`)
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages))
    }
  }, [sessionId])

  // 保存消息到localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages))
    }
  }, [messages, sessionId])

  // 处理发送消息
  const handleSendMessage = (message: Message) => {
    // 添加用户消息
    setMessages(prevMessages => [...prevMessages, message])

    // 模拟AI回复
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "这是一个模拟回复。实际将使用DeepSeek API处理。",
        sender: "ai",
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prevMessages => [...prevMessages, aiResponse])
      // TODO: Integrate backend API for AI response
    }, 1000)
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
