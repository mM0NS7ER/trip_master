
import { useState, useRef } from "react"
import { Mic, MicOff, Send } from "lucide-react"
import { apiRequest } from "@/utils/api"

interface Message {
  id: string
  text: string
  sender: "user" | "ai"
  timestamp: string
}

interface InputSectionProps {
  onSendMessage: (message: Message) => void
}

const InputSection = ({ onSendMessage }: InputSectionProps) => {
  const [inputText, setInputText] = useState("")
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const handleSend = () => {
    if (inputText.trim() === "") return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: "user",
      timestamp: new Date().toLocaleTimeString()
    }

    onSendMessage(userMessage)
    setInputText("")
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const startRecording = async () => {
    try {
      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // 设置MediaRecorder选项
      const options = {
        mimeType: 'audio/webm;codecs=opus', // 使用更兼容的格式
        audioBitsPerSecond: 16000 // 设置音频比特率为16kHz，与科大讯飞API匹配
      }

      const mediaRecorder = new MediaRecorder(stream, options)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        setIsProcessing(true)

        try {
          // 创建音频blob
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" })

          // 检查音频大小
          if (audioBlob.size === 0) {
            throw new Error("录音数据为空")
          }

          console.log("音频大小:", audioBlob.size, "bytes")

          // 准备发送到后端
          const formData = new FormData()
          formData.append("audio_file", audioBlob, "recording.webm")

          // 获取当前token
          const token = localStorage.getItem("token")

          if (!token) {
            throw new Error("未找到认证令牌，请先登录")
          }

          console.log("发送语音识别请求...")

          const response = await apiRequest("/api/speech/speech-to-text", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
            },
            body: formData
          })

          console.log("响应状态:", response.status)

          if (!response.ok) {
            const errorText = await response.text()
            console.error("错误响应:", errorText)
            throw new Error(`语音识别失败 (${response.status}): ${errorText}`)
          }

          const data = await response.json()
          console.log("识别结果:", data)

          if (data.success) {
            setInputText(data.text)
          } else {
            alert(`语音识别失败: ${data.error || "未知错误"}`)
          }
        } catch (error) {
          console.error("语音识别错误:", error)
          alert(`语音识别失败: ${error instanceof Error ? error.message : "未知错误"}`)
        } finally {
          setIsProcessing(false)
          // 关闭所有音轨
          stream.getTracks().forEach(track => track.stop())
        }
      }

      // 开始录音
      mediaRecorder.start(100) // 每100ms收集一次数据
      setIsRecording(true)
    } catch (error) {
      console.error("无法访问麦克风:", error)
      alert(`无法访问麦克风: ${error instanceof Error ? error.message : "未知错误"}`)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  return (
    <div className="p-4 border-t">
      <div className="flex items-center space-x-2">
        <input
          type="text"
          placeholder="ask anything..."
          className="border rounded-lg p-2 flex-1"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button
          className={`p-2 rounded-full hover:bg-gray-100 ${isRecording ? "bg-red-100" : ""} ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
        >
          {isRecording ? (
            <MicOff className="w-5 h-5 text-red-500" />
          ) : (
            <Mic className="w-5 h-5 text-gray-500" />
          )}
        </button>
        <button
          className="p-2 rounded-full hover:bg-gray-100"
          onClick={handleSend}
        >
          <Send className="w-5 h-5 text-blue-500" />
        </button>
      </div>
      <div className="mt-2 flex justify-end">
        <span className="text-xs text-gray-500">Mindtrip</span>
        {isProcessing && <span className="ml-2 text-xs text-blue-500">正在处理语音...</span>}
      </div>
      {/* TODO: Integrate backend API for AI response */}
    </div>
  )
}

export default InputSection
