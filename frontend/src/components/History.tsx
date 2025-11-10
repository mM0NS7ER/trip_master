
import { useState, useEffect, useRef } from "react"
import { Trash2, MessageSquare } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { useDialogStore } from "@/store/dialogStore"
import { useChatStore } from "@/store/chatStore"
import { apiGet } from "@/utils/api"

interface ChatHistory {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  userId?: string
}

const History = ({ isOpen, onClose, onSelectChat }: { isOpen: boolean, onClose: () => void, onSelectChat: (id: string) => void }) => {
  const [filteredHistory, setFilteredHistory] = useState<ChatHistory[]>([])
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { openDeleteConfirm } = useDialogStore()
  const { chats, setChats } = useChatStore()
  const historyRef = useRef<HTMLDivElement>(null)

  // 加载用户聊天记录
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (!token) {
          // 用户未登录，清空历史记录
          setChats([]);
          return;
        }

        const response = await apiGet('/chats');

        if (!response.ok) {
          throw new Error('获取聊天记录失败');
        }

        const data = await response.json();
        // 确保数据格式符合接口要求
        const formattedHistory = data.chats.map((chat: any) => ({
          id: chat.id,
          title: chat.title || '未命名会话',
          lastMessage: chat.last_message || '',
          timestamp: new Date(chat.updated_at).toLocaleString('zh-CN'),
          userId: chat.user_id
        }));
        
        setChats(formattedHistory);
      } catch (error) {
        console.error('获取聊天记录失败:', error);
        // 出错时设置空数组，避免显示错误数据
        setChats([]);
      }
    };

    fetchChatHistory();
  }, [user?.id, setChats]); // 当用户ID变化时重新获取数据

  // 过滤历史记录，只显示当前用户的记录
  useEffect(() => {
    if (user) {
      const userHistory = chats.filter(chat => 
        chat.userId === user.id || !chat.userId // 兼容没有userId的旧数据
      )
      setFilteredHistory(userHistory)
    } else {
      // 如果用户未登录，显示访客记录或空列表
      const guestHistory = chats.filter(chat => !chat.userId)
      setFilteredHistory(guestHistory)
    }
  }, [chats, user])

  // 点击外部区域关闭History组件
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (historyRef.current && !historyRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    // 只有当History组件打开时才添加事件监听器
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    // 清理事件监听器
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, onClose])

  const handleDeleteChat = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    // 打开全局确认对话框
    openDeleteConfirm(id)
  }

  const handleSelectChat = (id: string) => {
    onSelectChat(id)
    navigate(`/chat/${id}`)
  }

  return (
    <div ref={historyRef} className={`fixed left-20 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-gray-200 shadow-lg transform transition-transform duration-300 z-10 ${isOpen ? "translate-x" : "-translate-x-96"}`}>
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
        {filteredHistory.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            暂无历史会话
          </div>
        ) : (
          <ul>
            {filteredHistory.map((chat) => (
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


    </div>
  )
}

export default History
