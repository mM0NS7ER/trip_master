
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { useEffect, useState } from "react"
import ChatLayout from "./components/ChatLayout"
import { AuthProvider } from "./store/authStore.tsx"

function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  // 检查当前活跃会话
  useEffect(() => {
    const savedSessionId = localStorage.getItem('currentSessionId')
    if (savedSessionId) {
      setCurrentSessionId(savedSessionId)
    } else {
      // 如果没有活跃会话，创建一个新的
      const newSessionId = `${Date.now()}_${Math.floor(Math.random() * 10000)}`
      localStorage.setItem('currentSessionId', newSessionId)
      setCurrentSessionId(newSessionId)
    }
  }, [])

  // 创建新会话
  const createNewSession = () => {
    const newSessionId = `${Date.now()}_${Math.floor(Math.random() * 10000)}`
    localStorage.setItem('currentSessionId', newSessionId)
    return newSessionId
  }

  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Navigate to={`/chat/${currentSessionId || createNewSession()}`} replace />} />
            <Route path="/chat/:sessionId" element={<ChatLayout />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
