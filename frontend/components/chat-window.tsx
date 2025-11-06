"use client"

import { useRef, useState, useEffect } from "react"
import { Plus, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useChatSessions } from "@/lib/hooks/useChatSessions"
import { addMessageToChat } from "@/lib/utils/chatUtils"
import type { Message } from "@/lib/utils/chatUtils"

interface ChatWindowProps {
  chatId: string | null
}

export function ChatWindow({ chatId }: ChatWindowProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [inputValue, setInputValue] = useState("")
  const { currentChat, addMessage, refreshSessions } = useChatSessions()
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  // Cleanup timeout if chatId changes
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }
  }, [chatId])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Handle file upload here
      console.log("File selected:", file.name)
      // You can add your file handling logic here
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleSend = () => {
    if (!inputValue.trim() || !chatId) return

    // Capture the chatId at the time of sending to prevent stale closure issues
    const sendingChatId = chatId
    const userMessageContent = inputValue.trim()

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Add user message using the hook (which updates state)
    addMessage({
      role: "user",
      content: userMessageContent,
    })

    // Clear input
    setInputValue("")

    // TODO: Add assistant response logic here
    // For now, we'll just add a placeholder response
    // Use the captured chatId to ensure message is added to the correct chat
    timeoutRef.current = setTimeout(() => {
      // Verify the chatId is still the same before adding the response
      if (chatId === sendingChatId && sendingChatId) {
        // Use the utility function directly with the captured chatId
        // This ensures the message is added to the correct chat even if user navigated away
        const assistantMessage: Message = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
          role: "assistant",
          content: "This is a placeholder response. Backend integration needed.",
          timestamp: Date.now(),
        }
        
        addMessageToChat(sendingChatId, assistantMessage)
        
        // Refresh the sessions to update the UI
        // This ensures the UI reflects the new message even if user navigated away
        refreshSessions()
      }
      timeoutRef.current = null
    }, 500)
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const messages = currentChat?.messages || []

  return (
    <div className="flex-1 flex flex-col bg-gray-50 rounded-r-2xl overflow-hidden">
      {/* Message List Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <p className="text-lg">No messages yet. Start a conversation!</p>
            </div>
          ) : (
            <div className="space-y-4 py-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={message.role === "user" ? "flex justify-end" : "flex justify-start"}
                >
                  <div
                    className={message.role === "user"
                      ? "bg-blue-500 text-white rounded-lg px-4 py-2 max-w-[80%]"
                      : "bg-white text-gray-800 rounded-lg px-4 py-2 max-w-[80%] border border-gray-200"}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chat Input Area at Bottom */}
      <div className="px-8 pb-8">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-3 shadow-sm">
            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileUpload}
              accept=".pdf,.txt,.doc,.docx"
            />
            
            {/* Upload Button */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                type="button"
                onClick={handleUploadClick}
                className="w-8 h-8 rounded-full bg-white hover:bg-gray-200"
              >
                <Plus className="h-4 w-4 text-gray-700" />
              </Button>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                Upload Files
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
              </div>
            </div>

            {/* Input Field */}
            <Input
              ref={inputRef}
              type="text"
              placeholder="Ask anything from here"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-700 placeholder:text-gray-400"
              disabled={!chatId}
            />

            {/* Send Button */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSend}
                disabled={!inputValue.trim() || !chatId}
                className="w-8 h-8 rounded-full bg-white hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-4 w-4 text-gray-700" />
              </Button>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                Submit
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

