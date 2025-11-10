
import { MessageCircle, Search, Heart, Bell, User, Plus } from "lucide-react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore.tsx"
import UserProfile from "./UserProfile.tsx"
import { toast } from "react-hot-toast"

interface SidebarProps {
  onNewChat: () => void
  onToggleHistory: () => void
  showHistory: boolean
}

const Sidebar = ({ onNewChat, onToggleHistory, showHistory }: SidebarProps) => {
  const navigate = useNavigate()
  const { openAuthModal, user } = useAuthStore()
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  
  const handleUserClick = () => {
    if (user) {
      setIsProfileOpen(true)
    } else {
      openAuthModal()
    }
  }

  // 检查用户是否已登录，如果未登录则提示并打开登录框
  const checkAuthAndExecute = (callback: () => void, message: string) => {
    if (user) {
      callback();
    } else {
      toast.error(message);
      openAuthModal();
    }
  };
  


  return (
    <aside className="w-20 h-full bg-white border-r flex flex-col items-center relative">
      <div className="flex-1 flex flex-col items-center py-4 space-y-4">
        <button
          onClick={onNewChat}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
          title="新聊天"
        >
          <Plus className="w-6 h-6" />
        </button>
        <button
          onClick={onToggleHistory}
          className={`p-2 rounded-md hover:bg-gray-100 ${showHistory ? 'text-blue-500' : 'text-gray-500 hover:text-blue-500'}`}
          title="聊天"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
        <button
          onClick={() => checkAuthAndExecute(() => alert("搜索功能开发中"), "请先登录后再使用搜索功能")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
          title="搜索"
        >
          <Search className="w-6 h-6" />
        </button>
        <button
          onClick={() => checkAuthAndExecute(() => alert("收藏功能开发中"), "请先登录后再使用收藏功能")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
          title="收藏"
        >
          <Heart className="w-6 h-6" />
        </button>
        <button
          onClick={() => checkAuthAndExecute(() => alert("通知功能开发中"), "请先登录后再查看通知")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
          title="通知"
        >
          <Bell className="w-6 h-6" />
        </button>

      </div>
      <div className="absolute bottom-4">
        <button
          onClick={handleUserClick}
          className={`p-2 rounded-md hover:bg-gray-100 ${user ? "text-blue-500" : "text-gray-500 hover:text-blue-500"}`}
          title="用户中心"
        >
          <User className="w-6 h-6" />
        </button>
      </div>
      {/* TODO: Integrate backend API */}
      
      {/* 用户个人信息弹窗 */}
      <UserProfile isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
    </aside>
  )
}

export default Sidebar
