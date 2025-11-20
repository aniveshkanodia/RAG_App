"use client"

import { useRef, useState, useEffect, useLayoutEffect } from "react"
import { Plus, Send, RotateCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useChatSessions } from "@/lib/hooks/useChatSessions"
import type { Message, UploadedFile } from "@/lib/utils/chatUtils"
import { getChatSessions, saveChatSessions } from "@/lib/utils/chatUtils"
import { chat, uploadFile } from "@/lib/api/client"
import { FileSidebar } from "./file-sidebar"
import { SourceDisplay } from "./source-display"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface ChatWindowProps {
  chatId: string | null
  initialMessage?: string | null
}

export function ChatWindow({ chatId, initialMessage }: ChatWindowProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({ type: null, message: '' })
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const { currentChat, addMessage, refreshSessions, setCurrentChat, addFile, getFiles, removeFile } = useChatSessions()
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  // Track processed initial messages per chatId to prevent duplicate sends
  const processedInitialMessagesRef = useRef<Map<string, Set<string>>>(new Map())
  
  // Get messages from currentChat (must be defined before useLayoutEffect)
  const messages = currentChat?.messages || []
  
  // Ensure currentChatId in hook matches the chatId prop
  useEffect(() => {
    if (chatId) {
      setCurrentChat(chatId)
    }
  }, [chatId, setCurrentChat])
  
  // Load uploaded files for current chat (client-side only to avoid hydration issues)
  // Sync with both currentChat from hook and localStorage to ensure consistency
  useEffect(() => {
    if (chatId && typeof window !== "undefined") {
      // First try to get from currentChat (hook state) - most up-to-date
      const filesFromHook = currentChat?.uploadedFiles || []
      
      // Also check localStorage as fallback to ensure we have the latest
      const filesFromStorage = getFiles(chatId)
      
      // Use the longer array (most recent) to handle race conditions
      const files = filesFromHook.length >= filesFromStorage.length ? filesFromHook : filesFromStorage
      
      setUploadedFiles(files)
    } else {
      setUploadedFiles([])
    }
  }, [chatId, currentChat?.uploadedFiles])
  
  // Auto-scroll to bottom when messages change
  useLayoutEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])
  
  // Cleanup timeout if chatId changes
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }
  }, [chatId])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !chatId) return

    // Clear previous status
    setUploadStatus({ type: null, message: '' })
    setIsUploading(true)

    // Get file extension
    const fileExt = file.name.split('.').pop()?.toLowerCase() || ''
    const fileType = fileExt === 'docx' || fileExt === 'doc' ? 'docx' : fileExt

    // Add file to chat session with "uploading" status
    addFile({
      name: file.name,
      type: fileType,
      status: "uploading",
    }, chatId)

    // Store the file ID to update its status later
    let fileId: string | null = null

    try {
      // Upload the file with conversation_id
      const response = await uploadFile(file, chatId)
      
      // Update file status to "success" in chat session
      const sessions = getChatSessions()
      const sessionIndex = sessions.findIndex((s) => s.id === chatId)
      if (sessionIndex !== -1 && sessions[sessionIndex].uploadedFiles) {
        const files = sessions[sessionIndex].uploadedFiles
        const lastFile = files[files.length - 1]
        if (lastFile && lastFile.status === "uploading") {
          fileId = lastFile.id
          lastFile.status = "success"
          sessions[sessionIndex].updatedAt = Date.now()
          saveChatSessions(sessions)
          // Update local state immediately - useEffect will also sync but this ensures UI updates
          setUploadedFiles([...files])
        } else {
          // If we couldn't find the uploading file, refresh from storage
          const updatedFiles = getFiles(chatId)
          setUploadedFiles(updatedFiles)
        }
      } else {
        // Session not found or no files - refresh from storage
        const updatedFiles = getFiles(chatId)
        setUploadedFiles(updatedFiles)
      }
      // Refresh sessions once after all updates
      refreshSessions()
      
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
      // Update file status to "error" in chat session
      const sessions = getChatSessions()
      const sessionIndex = sessions.findIndex((s) => s.id === chatId)
      if (sessionIndex !== -1 && sessions[sessionIndex].uploadedFiles) {
        const files = sessions[sessionIndex].uploadedFiles
        const lastFile = files[files.length - 1]
        if (lastFile && lastFile.status === "uploading") {
          fileId = lastFile.id
          lastFile.status = "error"
          sessions[sessionIndex].updatedAt = Date.now()
          saveChatSessions(sessions)
          // Update local state immediately - useEffect will also sync but this ensures UI updates
          setUploadedFiles([...files])
        } else {
          // If we couldn't find the uploading file, refresh from storage
          const updatedFiles = getFiles(chatId)
          setUploadedFiles(updatedFiles)
        }
      } else {
        // Session not found or no files - refresh from storage
        const updatedFiles = getFiles(chatId)
        setUploadedFiles(updatedFiles)
      }
      // Refresh sessions once after all updates
      refreshSessions()
      
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

  // Handle initial message from home page (passed via URL params)
  useEffect(() => {
    // Skip if no initialMessage, no chatId, currently loading, or already processed
    if (!initialMessage || !chatId || isLoading) return
    
    const userMessageContent = initialMessage.trim()
    if (!userMessageContent) return
    
    // Get processed messages for this chatId
    const processedSet = processedInitialMessagesRef.current.get(chatId) || new Set<string>()
    
    // Check if this exact message was already processed for this chat
    if (processedSet.has(userMessageContent)) {
      // Already processed, return immediately
      return
    }
    
    // Check if chat already has a user message matching initialMessage
    // This is more reliable than checking messages.length === 0
    const hasMatchingUserMessage = messages.some(
      (msg) => msg.role === "user" && msg.content.trim() === userMessageContent
    )
    
    // If matching message exists, mark as processed and return
    if (hasMatchingUserMessage) {
      processedSet.add(userMessageContent)
      processedInitialMessagesRef.current.set(chatId, processedSet)
      return
    }
    
    // Mark as processed immediately to prevent duplicate sends
    processedSet.add(userMessageContent)
    processedInitialMessagesRef.current.set(chatId, processedSet)
    
    // Set the input value
    setInputValue(initialMessage)
    
    // Use setTimeout to ensure state is updated and chat is ready
    setTimeout(async () => {
      if (!chatId) {
        return;
      }
      
      // Ensure currentChatId is set in the hook
      setCurrentChat(chatId)
      
      // Calculate turn_index: count user messages before adding the new one
      const userMessages = messages.filter(m => m.role === "user");
      const turnIndex = userMessages.length;
      
      // Clear input
      setInputValue("")
      
      // Add user message using the hook
      addMessage({
        role: "user",
        content: userMessageContent,
      }, chatId)
      
      // Set loading state
      setIsLoading(true)
      
      try {
        // Call the API to get the answer with conversation_id and turn_index
        const response = await chat(userMessageContent, chatId, turnIndex)
        
        // Store answer and sources separately
        // Use addMessage hook instead of addMessageToChat directly
        // Pass chatId directly to ensure message is added to correct chat
        // This ensures state updates properly and triggers re-render
        addMessage({
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        }, chatId)
        
        // Message successfully processed - already marked in processedSet above
      } catch (error) {
        // Handle errors
        
        // Use addMessage hook instead of addMessageToChat directly
        // Pass chatId directly to ensure message is added to correct chat
        addMessage({
          role: "assistant",
          content: `Error: ${error instanceof Error ? error.message : "We're having trouble reaching the server — please try again later."}`,
        }, chatId)
        
        // On error, remove from processed set so user can retry explicitly
        // But keep it marked as processed for initialMessage to prevent auto-retry
        // The retry button will handle explicit retries
      } finally {
        // Clear loading state
        setIsLoading(false)
      }
    }, 200)
  }, [initialMessage, chatId, isLoading, messages, setCurrentChat, addMessage, refreshSessions])

  const handleSend = async () => {
    if (!inputValue.trim() || !chatId || isLoading) return

    // Capture the chatId at the time of sending to prevent stale closure issues
    const sendingChatId = chatId
    const userMessageContent = inputValue.trim()
    
    // Validate chatId is present (defensive check)
    if (!sendingChatId) {
      return;
    }

    // Ensure currentChatId is set in the hook
    if (chatId) {
      setCurrentChat(chatId)
    }

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Clear input immediately for better UX
    setInputValue("")

    // Calculate turn_index: count user messages before adding the new one
    const userMessages = messages.filter(m => m.role === "user");
    const turnIndex = userMessages.length;

    // Add user message using the hook (which updates state)
    // Pass chatId directly to avoid relying on async state updates
    // This should trigger a re-render with the new message
    addMessage({
      role: "user",
      content: userMessageContent,
    }, chatId)

    // Set loading state
    setIsLoading(true)

    try {
      // Call the API to get the answer with conversation_id and turn_index
      const response = await chat(userMessageContent, sendingChatId, turnIndex)
      
      // Verify the chatId is still the same before adding the response
      if (chatId === sendingChatId && sendingChatId) {
        // Store answer and sources separately
        // Use addMessage hook instead of addMessageToChat directly
        // Pass chatId directly to ensure message is added to correct chat
        // This ensures state updates properly and triggers re-render
        addMessage({
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        }, sendingChatId)
      }
    } catch (error) {
      // Handle errors
      
      // Verify the chatId is still the same before adding the error message
      if (chatId === sendingChatId && sendingChatId) {
        // Use addMessage hook instead of addMessageToChat directly
        // Pass chatId directly to ensure message is added to correct chat
        addMessage({
          role: "assistant",
          content: `Error: ${error instanceof Error ? error.message : "We're having trouble reaching the server — please try again later."}`,
        }, sendingChatId)
      }
    } finally {
      // Clear loading state
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Handle retry for failed messages
  const handleRetry = async (errorMessageIndex: number) => {
    if (!chatId || isLoading) return

    // Find the user message before the error message
    const errorMessage = messages[errorMessageIndex]
    if (!errorMessage || !errorMessage.content.startsWith("Error:")) return

    // Find the last user message before this error
    let lastUserMessage: Message | null = null
    for (let i = errorMessageIndex - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        lastUserMessage = messages[i]
        break
      }
    }

    if (!lastUserMessage) return

    const userMessageContent = lastUserMessage.content
    const sendingChatId = chatId

    // Calculate turn_index: count user messages up to and including the one being retried
    // Find the index of the user message in the messages array
    const userMessageIndex = messages.findIndex(m => m === lastUserMessage);
    const userMessagesBefore = messages.slice(0, userMessageIndex + 1).filter(m => m.role === "user");
    const turnIndex = userMessagesBefore.length - 1; // -1 because we want 0-indexed

    setIsLoading(true)

    try {
      // Call the API to get the answer with conversation_id and turn_index
      const response = await chat(userMessageContent, sendingChatId, turnIndex)

      // Replace the error message with the successful response
      // We'll update the message content and sources directly in the chat session
      const sessions = getChatSessions()
      const sessionIndex = sessions.findIndex((s) => s.id === sendingChatId)
      if (sessionIndex !== -1) {
        const messageIndex = sessions[sessionIndex].messages.findIndex(
          (m) => m.id === errorMessage.id
        )
        if (messageIndex !== -1) {
          sessions[sessionIndex].messages[messageIndex] = {
            ...sessions[sessionIndex].messages[messageIndex],
            content: response.answer,
            sources: response.sources,
          }
          sessions[sessionIndex].updatedAt = Date.now()
          saveChatSessions(sessions)
        }
      }
      refreshSessions()
    } catch (error) {
      // Error handling
      // Update the error message with the new error
      const sessions = getChatSessions()
      const sessionIndex = sessions.findIndex((s) => s.id === sendingChatId)
      if (sessionIndex !== -1) {
        const messageIndex = sessions[sessionIndex].messages.findIndex(
          (m) => m.id === errorMessage.id
        )
        if (messageIndex !== -1) {
          sessions[sessionIndex].messages[messageIndex] = {
            ...sessions[sessionIndex].messages[messageIndex],
            content: `Error: ${error instanceof Error ? error.message : "We're having trouble reaching the server — please try again later."}`,
          }
          sessions[sessionIndex].updatedAt = Date.now()
          saveChatSessions(sessions)
        }
      }
      refreshSessions()
    } finally {
      setIsLoading(false)
    }
  }

  // uploadedFiles is now managed via useState and useEffect above

  return (
    <div className="flex-1 flex bg-gray-50 rounded-r-2xl overflow-hidden">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Message List Area */}
      {messages.length === 0 ? (
        // Empty state: No scrollable container, just centered welcome message (matches home page)
        <div className="flex-1 flex flex-col items-center justify-center px-8 pb-24">
          <div className="w-full max-w-4xl mb-12">
            <h1 className="text-6xl font-bold text-blue-500 mb-2">Hello</h1>
            <p className="text-xl text-gray-600">I'm here to help you find answers and insights from your documents.</p>
          </div>
        </div>
      ) : (
        // Active chat: Scrollable container only appears when user starts chatting
        <div className="flex-1 overflow-y-auto px-8 min-h-0">
          <div className="max-w-4xl mx-auto py-6">
            <div className="space-y-4">
              {messages.map((message, messageIndex) => {
                const isError = message.content.startsWith("Error:")
                return (
                  <div
                    key={message.id}
                    className={message.role === "user" ? "flex justify-end" : "flex justify-start"}
                  >
                    <div className="flex flex-col gap-1 max-w-[80%]">
                      <div
                        className={message.role === "user"
                          ? "bg-blue-500 text-white rounded-lg px-4 py-2 break-words"
                          : isError
                          ? "bg-red-50 text-red-800 rounded-lg px-4 py-2 border border-red-200 break-words"
                          : "bg-white text-gray-800 rounded-lg px-4 py-2 border border-gray-200 break-words"}
                      >
                        <div className={`text-sm break-words overflow-wrap-anywhere prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0 prose-strong:font-bold ${
                          message.role === "user"
                            ? "prose-invert prose-p:text-white prose-strong:text-white prose-ul:text-white prose-ol:text-white prose-li:text-white"
                            : isError
                            ? "prose-p:text-red-800 prose-strong:text-red-900 prose-ul:text-red-800 prose-ol:text-red-800 prose-li:text-red-800"
                            : "prose-p:text-gray-800 prose-strong:text-gray-900 prose-ul:text-gray-800 prose-ol:text-gray-800 prose-li:text-gray-800"
                        }`}>
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                      {/* Sources display for assistant messages */}
                      {!isError && message.role === "assistant" && message.sources && message.sources.length > 0 && (
                        <SourceDisplay sources={message.sources} />
                      )}
                      {/* Retry button for error messages */}
                      {isError && message.role === "assistant" && (
                        <div className="flex justify-start">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRetry(messageIndex)}
                            disabled={isLoading}
                            className="h-7 px-3 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <RotateCw className="h-3 w-3 mr-1" />
                            Retry
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-800 rounded-lg px-4 py-2 max-w-[80%] border border-gray-200">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      <p className="text-sm text-gray-500">Thinking...</p>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
      )}

      {/* Chat Input Area at Bottom */}
      <div className="px-8 pb-8">
        <div className="max-w-4xl mx-auto">
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
              accept=".pdf,.txt,.doc,.docx,.xlsx,.xls"
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
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-700 placeholder:text-gray-400"
              disabled={!chatId || isLoading}
            />

            {/* Send Button */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSend}
                disabled={!inputValue.trim() || !chatId || isLoading}
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
      </div>

      {/* File Sidebar - Right Side */}
      {chatId && uploadedFiles.length > 0 && (
        <FileSidebar 
          files={uploadedFiles} 
          onRemoveFile={(fileId) => {
            removeFile(fileId, chatId)
            // Update local state after removal
            if (typeof window !== "undefined") {
              const updatedFiles = getFiles(chatId)
              setUploadedFiles(updatedFiles)
            }
          }} 
        />
      )}
    </div>
  )
}
