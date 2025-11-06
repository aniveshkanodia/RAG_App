"use client"

import { useState, Suspense } from "react"
import Link from "next/link"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, Home, RotateCw, MessageSquare, Trash2, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useChatSessions } from "@/lib/hooks/useChatSessions"

function SidebarContent() {
  const pathname = usePathname()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isExpanded, setIsExpanded] = useState(false)
  const { sessions, createNewChat, refreshSessions, deleteChat } = useChatSessions()
  const currentChatId = searchParams.get("chatId")
  const [hoveredChatId, setHoveredChatId] = useState<string | null>(null)

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Delete the chat
    deleteChat(chatId)
    
    // If the deleted chat is the current one, navigate to home
    if (currentChatId === chatId) {
      router.push("/")
    }
  }

  return (
    <motion.div
      className="h-screen bg-gray-100 rounded-l-2xl flex flex-col py-4 gap-4 overflow-hidden"
      initial={{ width: 64 }}
      animate={{ width: isExpanded ? 240 : 64 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* App Icon - Red/Blue Pinwheel Design */}
      <div className="flex items-center justify-center px-2">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 via-red-400 to-blue-500 flex items-center justify-center flex-shrink-0">
          <div className="w-6 h-6 relative">
            <div className="absolute inset-0 border-2 border-white rounded-full"></div>
            <div className="absolute inset-0 border-2 border-transparent border-t-white border-r-white rotate-45 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-2">
        <Button
          onClick={() => {
            const newChat = createNewChat()
            router.push(`/chat?chatId=${newChat.id}`)
          }}
          className={cn(
            "rounded-xl bg-blue-500 hover:bg-blue-600 text-white flex-shrink-0 transition-all duration-300",
            pathname === "/" && "bg-blue-600",
            isExpanded ? "w-full justify-start gap-3 px-4 py-3" : "w-12 h-12 justify-center"
          )}
        >
          <Plus className="h-5 w-5 flex-shrink-0" />
          <AnimatePresence>
            {isExpanded && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2 }}
                className="whitespace-nowrap font-medium"
              >
                New Chat
              </motion.span>
            )}
          </AnimatePresence>
        </Button>
      </div>

      {/* Chat History List */}
      {isExpanded && sessions.length > 0 && (
        <div className="flex-1 overflow-y-auto px-2 mt-2 space-y-1 min-h-0">
          {sessions.slice(0, 10).map((session) => (
            <div
              key={session.id}
              className="relative group"
              onMouseEnter={() => setHoveredChatId(session.id)}
              onMouseLeave={() => setHoveredChatId(null)}
            >
              <Link href={`/chat?chatId=${session.id}`}>
                <Button
                  variant="ghost"
                  className={cn(
                    "w-full justify-start gap-3 px-3 py-2 h-auto rounded-lg hover:bg-gray-200 text-left pr-10",
                    currentChatId === session.id && "bg-gray-200"
                  )}
                >
                  <MessageSquare className="h-4 w-4 text-gray-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700 truncate">
                      {session.title}
                    </p>
                    {session.messages.length > 0 && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">
                        {session.messages[session.messages.length - 1]?.content.substring(0, 30)}
                        {session.messages[session.messages.length - 1]?.content.length > 30 && "..."}
                      </p>
                    )}
                  </div>
                </Button>
              </Link>
              {/* Delete Button - appears on hover */}
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => handleDeleteChat(e, session.id)}
                className={cn(
                  "absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full hover:bg-red-100 hover:text-red-600 transition-opacity",
                  hoveredChatId === session.id ? "opacity-100" : "opacity-0"
                )}
                title="Delete chat"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Spacer - only show if no chat history */}
      {(!isExpanded || sessions.length === 0) && <div className="flex-1" />}

      {/* Home Icon */}
      <div className="px-2">
        <Link href="/">
          <Button
            variant="ghost"
            className={cn(
              "rounded-full hover:bg-gray-200 flex-shrink-0 transition-all duration-300",
              (pathname === "/" || pathname === "/chat") && "bg-gray-200",
              isExpanded ? "w-full justify-start gap-3 px-4 py-2.5" : "w-10 h-10 justify-center"
            )}
          >
            <Home className="h-5 w-5 text-gray-700 flex-shrink-0" />
            <AnimatePresence>
              {isExpanded && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{ duration: 0.2 }}
                  className="whitespace-nowrap text-gray-700"
                >
                  Home
                </motion.span>
              )}
            </AnimatePresence>
          </Button>
        </Link>
      </div>

      {/* Refresh Icon */}
      <div className="px-2">
        <Button
          variant="ghost"
          onClick={refreshSessions}
          className={cn(
            "rounded-full hover:bg-gray-200 flex-shrink-0 transition-all duration-300",
            isExpanded ? "w-full justify-start gap-3 px-4 py-2.5" : "w-10 h-10 justify-center"
          )}
        >
          <RotateCw className="h-5 w-5 text-gray-700 flex-shrink-0" />
          <AnimatePresence>
            {isExpanded && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2 }}
                className="whitespace-nowrap text-gray-700"
              >
                Refresh
              </motion.span>
            )}
          </AnimatePresence>
        </Button>
      </div>
    </motion.div>
  )
}

export function Sidebar() {
  return (
    <Suspense fallback={
      <div className="h-screen w-16 bg-gray-100 rounded-l-2xl flex flex-col items-center py-4 gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 via-red-400 to-blue-500 flex items-center justify-center flex-shrink-0">
          <div className="w-6 h-6 relative">
            <div className="absolute inset-0 border-2 border-white rounded-full"></div>
            <div className="absolute inset-0 border-2 border-transparent border-t-white border-r-white rotate-45 rounded-full"></div>
          </div>
        </div>
      </div>
    }>
      <SidebarContent />
    </Suspense>
  )
}

