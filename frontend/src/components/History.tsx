
import { useState, useEffect } from "react"
import { Trash2, MessageSquare } from "lucide-react"
import { useNavigate } from "react-router-dom"

interface ChatHistory {
  id: string
  title: string
  lastMessage: string
  timestamp: string
}

const History = ({ isOpen, onClose, onSelectChat }: { isOpen: boolean, onClose: () => void, onSelectChat: (id: string) => void }) => {
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const navigate = useNavigate()

  // 模拟加载历史记录
  useEffect(() => {
    // 从localStorage获取历史记录
    const savedHistory = localStorage.getItem('chatHistory')
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory))
    } else {
      // 模拟数据
      const mockHistory = [
        {
          id: "12345",
          title: "北京三日游",
          lastMessage: "故宫的门票怎么预订？",
          timestamp: "2023-08-15 14:30"
        },
        {
          id: "67890",
          title: "上海美食之旅",
          lastMessage: "推荐一些上海的特色小吃",
          timestamp: "2023-08-14 10:15"
        },
        {
          id: "11111",
          title: "云南大理洱海",
          lastMessage: "洱海附近有什么推荐的民宿？",
          timestamp: "2023-08-12 18:45"
        }
      ]
      setChatHistory(mockHistory)
    }
  }, [])

  const handleDeleteChat = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const updatedHistory = chatHistory.filter(chat => chat.id !== id)
    setChatHistory(updatedHistory)
    localStorage.setItem('chatHistory', JSON.stringify(updatedHistory))
  }

  const handleSelectChat = (id: string) => {
    onSelectChat(id)
    navigate(`/chat/${id}`)
  }

  return (
    <div className={`fixed left-20 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-gray-200 shadow-lg transform transition-transform duration-300 z-10 ${isOpen ? "translate-x" : "-translate-x-96"}`}>
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">历史会话</h2>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-gray-100"
        >
          ×
        </button>
      </div>
      <div className="overflow-y-auto h-[calc(100%-4rem)]">
        {chatHistory.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            暂无历史会话
          </div>
        ) : (
          <ul>
            {chatHistory.map((chat) => (
              <li
                key={chat.id}
                className="p-4 border-b hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                onClick={() => handleSelectChat(chat.id)}
              >
                <div className="flex items-center space-x-3">
                  <MessageSquare className="w-5 h-5 text-gray-400" />
                  <div>
                    <h3 className="font-medium text-sm">{chat.title}</h3>
                    <p className="text-xs text-gray-500 truncate">{chat.lastMessage}</p>
                    <p className="text-xs text-gray-400">{chat.timestamp}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  className="p-1 rounded hover:bg-gray-200"
                >
                  <Trash2 className="w-4 h-4 text-gray-400" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      {/* TODO: Integrate backend API */}
    </div>
  )
}

export default History
