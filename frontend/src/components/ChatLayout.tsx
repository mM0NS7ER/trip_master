
import { useState } from "react"
import { useParams } from "react-router-dom"
import Header from "./Header"
import Sidebar from "./Sidebar"
import History from "./History"
import ChatArea from "./ChatArea/ChatArea"
import MapArea from "./MapArea"

const ChatLayout = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [showHistory, setShowHistory] = useState(false)

  const handleNewChat = () => {
    // 生成新的sessionId并导航
    const newSessionId = `${Date.now()}_${Math.floor(Math.random() * 10000)}`
    window.location.href = `/chat/${newSessionId}`
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
    </div>
  )
}

export default ChatLayout
