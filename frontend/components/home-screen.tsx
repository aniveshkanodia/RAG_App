"use client"

import { useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { Plus, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useChatSessions } from "@/lib/hooks/useChatSessions"
import { checkServerHealth, uploadFile } from "@/lib/api/client"

export function HomeScreen() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({ type: null, message: '' })
  const [isUploading, setIsUploading] = useState(false)
  const router = useRouter()
  const { createNewChat } = useChatSessions()

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Clear previous status
    setUploadStatus({ type: null, message: '' })
    setServerError(null)
    setIsUploading(true)

    try {
      // Upload the file
      const response = await uploadFile(file)
      
      // Show success message
      setUploadStatus({
        type: 'success',
        message: `Successfully uploaded file ${file.name}.`
      })
      
      // Clear status after 5 seconds
      setTimeout(() => {
        setUploadStatus({ type: null, message: '' })
      }, 5000)
    } catch (error) {
      // Show error message
      const errorMessage = error instanceof Error ? error.message : "Failed to upload file. Please try again."
      setUploadStatus({
        type: 'error',
        message: errorMessage
      })
      
      // Clear status after 5 seconds
      setTimeout(() => {
        setUploadStatus({ type: null, message: '' })
      }, 5000)
    } finally {
      setIsUploading(false)
      // Reset file input so the same file can be uploaded again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const messageContent = inputValue.trim()
    
    // Clear any previous error
    setServerError(null)
    setIsLoading(true)
    
    try {
      // Check if server is available before creating a new chat
      const isServerAvailable = await checkServerHealth()
      
      if (!isServerAvailable) {
        setServerError("Server is not available. Please make sure the backend server is running.")
        setIsLoading(false)
        return
      }
      
      // Create a new chat session only if server is available
      const newChat = createNewChat()
      
      // Navigate to chat page with message in URL params
      // The chat page will detect the message param and send it automatically
      router.push(`/chat?chatId=${newChat.id}&message=${encodeURIComponent(messageContent)}`)
    } catch (error) {
      setServerError("Unable to connect to the server. Please try again later.")
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50 rounded-r-2xl overflow-hidden">
      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 pb-24">
        {/* Greeting Section */}
        <div className="w-full max-w-4xl mb-12">
          <h1 className="text-6xl font-bold text-blue-500 mb-2">Hello</h1>
          <p className="text-xl text-gray-600">I'm here to help you find answers and insights from your documents.</p>
        </div>
      </div>

      {/* Chat Input Area at Bottom */}
      <div className="px-8 pb-4">
        <div className="max-w-4xl mx-auto">
          {/* Server Error Message */}
          {serverError && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{serverError}</p>
            </div>
          )}
          {/* Upload Status Message */}
          {uploadStatus.type && (
            <div className={`mb-3 p-3 rounded-lg ${
              uploadStatus.type === 'success' 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <p className="text-sm">{uploadStatus.message}</p>
            </div>
          )}
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
                disabled={isUploading}
                className="w-8 h-8 rounded-full bg-white hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? (
                  <div className="w-4 h-4 border-2 border-gray-700 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Plus className="h-4 w-4 text-gray-700" />
                )}
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
              disabled={isLoading}
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-700 placeholder:text-gray-400"
            />

            {/* Send Button */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-white hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-gray-700 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="h-4 w-4 text-gray-700" />
                )}
              </Button>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                Submit
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Copyright Notice */}
      <div className="px-8 pb-4">
        <div className="max-w-4xl mx-auto">
          <p className="text-xs text-gray-500 text-center">
            © 2025 Anivesh Kanodia. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}

