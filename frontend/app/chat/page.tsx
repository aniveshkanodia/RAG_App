"use client"

import { Suspense } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatWindow } from "@/components/chat-window"
import { useSearchParams } from "next/navigation"
import { useChatSessions } from "@/lib/hooks/useChatSessions"
import { useEffect } from "react"

function ChatPageContent() {
  const searchParams = useSearchParams()
  const chatId = searchParams.get("chatId")
  const { setCurrentChat } = useChatSessions()

  useEffect(() => {
    if (chatId) {
      setCurrentChat(chatId)
    }
  }, [chatId, setCurrentChat])

  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <ChatWindow chatId={chatId} />
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

