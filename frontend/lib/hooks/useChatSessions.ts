"use client"

import { useState, useEffect, useCallback } from "react"
import {
  ChatSession,
  Message,
  getChatSessions,
  createChatSession,
  updateChatSession,
  addMessageToChat,
  deleteChatSession,
  getChatSession,
} from "@/lib/utils/chatUtils"

export function useChatSessions() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load sessions from localStorage on mount
  useEffect(() => {
    const loadedSessions = getChatSessions()
    setSessions(loadedSessions)
    setIsLoading(false)
  }, [])

  // Create a new chat session
  const createNewChat = useCallback((): ChatSession => {
    const newSession = createChatSession()
    setSessions((prev) => [newSession, ...prev])
    setCurrentChatId(newSession.id)
    return newSession
  }, [])

  // Get current chat session
  const getCurrentChat = useCallback((): ChatSession | null => {
    if (!currentChatId) return null
    return getChatSession(currentChatId)
  }, [currentChatId])

  // Set current chat ID
  const setCurrentChat = useCallback((chatId: string | null) => {
    setCurrentChatId(chatId)
  }, [])

  // Add a message to current chat
  const addMessage = useCallback(
    (message: Omit<Message, "id" | "timestamp">) => {
      if (!currentChatId) return

      const newMessage: Message = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        ...message,
        timestamp: Date.now(),
      }

      addMessageToChat(currentChatId, newMessage)
      
      // Update local state
      setSessions((prev) => {
        const updated = prev.map((session) => {
          if (session.id === currentChatId) {
            const updatedMessages = [...session.messages, newMessage]
            return {
              ...session,
              messages: updatedMessages,
              updatedAt: Date.now(),
              // Update title if it's the first user message
              title:
                session.title === "New Chat" && message.role === "user"
                  ? message.content.substring(0, 50) || "New Chat"
                  : session.title,
            }
          }
          return session
        })
        return updated
      })
    },
    [currentChatId]
  )

  // Delete a chat session
  const deleteChat = useCallback((chatId: string) => {
    deleteChatSession(chatId)
    setSessions((prev) => prev.filter((session) => session.id !== chatId))
    if (currentChatId === chatId) {
      setCurrentChatId(null)
    }
  }, [currentChatId])

  // Refresh sessions from localStorage
  const refreshSessions = useCallback(() => {
    const loadedSessions = getChatSessions()
    setSessions(loadedSessions)
  }, [])

  return {
    sessions,
    currentChatId,
    currentChat: getCurrentChat(),
    isLoading,
    createNewChat,
    setCurrentChat,
    addMessage,
    deleteChat,
    refreshSessions,
  }
}

