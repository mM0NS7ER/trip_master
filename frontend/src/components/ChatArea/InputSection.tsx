
import { useState } from "react"
import { Mic, Send } from "lucide-react"

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
          className="p-2 rounded-full hover:bg-gray-100" 
          onClick={() => alert("语音输入功能开发中")}
        >
          <Mic className="w-5 h-5 text-gray-500" />
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
      </div>
      {/* TODO: Integrate backend API for AI response */}
    </div>
  )
}

export default InputSection
