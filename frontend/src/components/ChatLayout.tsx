
import { useState } from "react"
import { useParams } from "react-router-dom"
import { v4 as uuidv4 } from "uuid"
import Header from "./Header"
import Sidebar from "./Sidebar"
import History from "./History"
import ChatArea from "./ChatArea/ChatArea"
import MapArea from "./MapArea"
import AuthModal from "./AuthModal"

const ChatLayout = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [showHistory, setShowHistory] = useState(false)

  const handleNewChat = async () => {
    try {
      // 从localStorage获取token
      const token = localStorage.getItem('token');
      
      // 调用后端API创建新会话
      const response = await fetch('http://localhost:8000/api/chats/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        throw new Error('创建新会话失败');
      }

      const data = await response.json();
      const newSessionId = data.id;
      
      // 导航到新会话
      window.location.href = `/chat/${newSessionId}`;
    } catch (error) {
      console.error("创建新会话出错:", error);
      alert('创建新会话失败，请稍后再试');
    }
  }

  const handleToggleHistory = () => {
    setShowHistory(!showHistory)
  }

  const handleSelectChat = (id: string) => {
    setShowHistory(false)
  }

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <History 
          isOpen={showHistory} 
          onClose={() => setShowHistory(false)}
          onSelectChat={handleSelectChat}
        />
        <Sidebar 
          onNewChat={handleNewChat} 
          onToggleHistory={handleToggleHistory} 
          showHistory={showHistory}
        />
        <div className="flex-1 mr-4">
          {sessionId && <ChatArea sessionId={sessionId} />}
        </div>
        <div className="flex-1">
          <MapArea />
        </div>
      </div>
      <AuthModal />
    </div>
  )
}

export default ChatLayout
