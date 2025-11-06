
import { MessageCircle, Search, Heart, Bell, User, Plus } from "lucide-react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"

interface SidebarProps {
  onNewChat: () => void
  onToggleHistory: () => void
  showHistory: boolean
}

const Sidebar = ({ onNewChat, onToggleHistory, showHistory }: SidebarProps) => {
  const navigate = useNavigate()

  return (
    <aside className="w-20 h-full bg-white border-r flex flex-col items-center relative">
      <div className="flex-1 flex flex-col items-center py-4 space-y-4">
        <button
          onClick={onNewChat}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
        >
          <Plus className="w-6 h-6" />
        </button>
        <button
          onClick={onToggleHistory}
          className={`p-2 rounded-md hover:bg-gray-100 ${showHistory ? 'text-blue-500' : 'text-gray-500 hover:text-blue-500'}`}
        >
          <MessageCircle className="w-6 h-6" />
        </button>
        <button
          onClick={() => alert("搜索功能开发中")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
        >
          <Search className="w-6 h-6" />
        </button>
        <button
          onClick={() => alert("收藏功能开发中")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
        >
          <Heart className="w-6 h-6" />
        </button>
        <button
          onClick={() => alert("通知功能开发中")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
        >
          <Bell className="w-6 h-6" />
        </button>
      </div>
      <div className="absolute bottom-4">
        <button
          onClick={() => alert("用户中心功能开发中")}
          className="p-2 rounded-md hover:bg-gray-100 text-gray-500 hover:text-blue-500"
        >
          <User className="w-6 h-6" />
        </button>
      </div>
      {/* TODO: Integrate backend API */}
    </aside>
  )
}

export default Sidebar
