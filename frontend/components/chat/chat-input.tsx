"use client"

import { useState, KeyboardEvent } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Send, Upload } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  onFileUpload?: () => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  onFileUpload,
  disabled = false,
  placeholder = "Ask a question...",
}: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex items-end gap-2 p-4 border-t">
      {onFileUpload && (
        <Button
          variant="ghost"
          size="icon"
          onClick={onFileUpload}
          disabled={disabled}
        >
          <Upload className="h-5 w-5" />
        </Button>
      )}
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="min-h-[60px] max-h-[200px] resize-none"
        rows={1}
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !message.trim()}
        size="icon"
      >
        <Send className="h-5 w-5" />
      </Button>
    </div>
  )
}

