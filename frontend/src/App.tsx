
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { useEffect, useState } from "react"
import ChatLayout from "./components/ChatLayout"
import { AuthProvider } from "./store/authStore.tsx"
import { Toaster } from "react-hot-toast"
import GlobalConfirmDialog from "./components/GlobalConfirmDialog"

function App() {
  // 不再在应用启动时创建会话ID，而是延迟到用户发送第一条消息时

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
            <Route path="/" element={<Navigate to="/chat/new" replace />} />
            <Route path="/chat/:sessionId" element={<ChatLayout />} />
          </Routes>
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: "#363636",
                color: "#fff",
              },
            }}
          />
          <GlobalConfirmDialog />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
