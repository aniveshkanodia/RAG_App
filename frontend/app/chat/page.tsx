"use client"

import { Suspense } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatWindow } from "@/components/chat-window"
import { useSearchParams, useRouter } from "next/navigation"
import { useChatSessions } from "@/lib/hooks/useChatSessions"
import { useEffect, useState } from "react"

function ChatPageContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const chatId = searchParams.get("chatId")
  const messageParam = searchParams.get("message")
  const { setCurrentChat } = useChatSessions()
  const [processedMessage, setProcessedMessage] = useState<string | null>(null)

  useEffect(() => {
    if (chatId) {
      setCurrentChat(chatId)
    }
  }, [chatId, setCurrentChat])
  
  // Clean up URL by removing message param immediately after it's detected
  // This prevents the initialMessage prop from persisting
  useEffect(() => {
    if (messageParam && chatId && !processedMessage) {
      // Mark as processed immediately
      setProcessedMessage(messageParam)
      // Remove message param from URL to keep it clean
      const newUrl = `/chat?chatId=${chatId}`
      router.replace(newUrl, { scroll: false })
    }
  }, [messageParam, chatId, router, processedMessage])
  
  // Reset processed message when chatId changes
  useEffect(() => {
    setProcessedMessage(null)
  }, [chatId])

  // Only pass initialMessage if it hasn't been processed yet
  const effectiveMessageParam = processedMessage === messageParam ? null : messageParam

  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <ChatWindow chatId={chatId} initialMessage={effectiveMessageParam || null} />
    </div>
  )
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="flex h-screen bg-white">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  )
}

