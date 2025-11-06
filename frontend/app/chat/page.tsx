import { Sidebar } from "@/components/sidebar"
import { ChatWindow } from "@/components/chat-window"

export default function ChatPage() {
  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <ChatWindow />
    </div>
  )
}

