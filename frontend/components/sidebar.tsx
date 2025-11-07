"use client"

import { useState, Suspense, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, MessageSquare, X, Home } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useChatSessions } from "@/lib/hooks/useChatSessions"

function SidebarContent() {
  const pathname = usePathname()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { sessions, createNewChat, deleteChat } = useChatSessions()
  const currentChatId = searchParams.get("chatId")
  const [hoveredChatId, setHoveredChatId] = useState<string | null>(null)
  
  // Sidebar state management
  // Initialize with default values to avoid hydration mismatch
  const [isPinned, setIsPinned] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(240)
  const [isResizing, setIsResizing] = useState(false)
  
  // Load from localStorage only on client side after mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedPinned = localStorage.getItem("sidebar_pinned")
      if (savedPinned === "true") {
        setIsPinned(true)
      }
      
      const savedWidth = localStorage.getItem("sidebar_width")
      if (savedWidth) {
        const width = parseInt(savedWidth, 10)
        // Ensure saved width is at least 140px
        setSidebarWidth(Math.max(width, 140))
      }
    }
  }, [])
  
  const minWidth = 64 // Minimum width when collapsed
  const minExpandedWidth = 140 // Minimum width when expanded/pinned
  const maxWidth = 200
  
  // Determine if sidebar should be expanded
  const isExpanded = isPinned || isHovered
  
  // Ensure sidebarWidth is at least minExpandedWidth when pinned
  useEffect(() => {
    if (isPinned && sidebarWidth < minExpandedWidth) {
      setSidebarWidth(minExpandedWidth)
      if (typeof window !== "undefined") {
        localStorage.setItem("sidebar_width", String(minExpandedWidth))
      }
    }
  }, [isPinned, sidebarWidth, minExpandedWidth])

  // Get current width - ensure expanded width is at least minExpandedWidth
  const currentWidth = isExpanded 
    ? Math.max(sidebarWidth, minExpandedWidth) 
    : minWidth

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

  // Toggle pin state
  const handleTogglePin = () => {
    const newPinnedState = !isPinned
    setIsPinned(newPinnedState)
    if (typeof window !== "undefined") {
      localStorage.setItem("sidebar_pinned", String(newPinnedState))
    }
  }

  // Handle resize start
  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsResizing(true)
  }

  // Handle resize
  useEffect(() => {
    if (!isResizing) return

    const handleMouseMove = (e: MouseEvent) => {
      // Calculate width based on mouse X position (sidebar starts at 0)
      // Use minExpandedWidth when resizing (since sidebar must be expanded to resize)
      const newWidth = Math.min(Math.max(e.clientX, minExpandedWidth), maxWidth)
      setSidebarWidth(newWidth)
      if (typeof window !== "undefined") {
        localStorage.setItem("sidebar_width", String(newWidth))
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    // Prevent text selection while resizing
    const handleSelectStart = (e: Event) => {
      e.preventDefault()
    }

    document.addEventListener("mousemove", handleMouseMove)
    document.addEventListener("mouseup", handleMouseUp)
    document.addEventListener("selectstart", handleSelectStart)
    document.body.style.cursor = "col-resize"
    document.body.style.userSelect = "none"

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
      document.removeEventListener("selectstart", handleSelectStart)
      document.body.style.cursor = ""
      document.body.style.userSelect = ""
    }
  }, [isResizing, minExpandedWidth, maxWidth])

  return (
    <motion.div
      className="h-screen bg-gray-100 rounded-l-2xl flex flex-col py-4 gap-4 overflow-hidden relative"
      initial={{ width: minWidth }}
      animate={{ width: currentWidth }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      onMouseEnter={() => !isPinned && setIsHovered(true)}
      onMouseLeave={() => !isPinned && setIsHovered(false)}
      style={{ cursor: isResizing ? "col-resize" : "default" }}
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

      {/* Toggle Pin Button */}
      <div className="px-2">
        <div className="relative">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleTogglePin}
            className={cn(
              "w-10 h-10 rounded-full hover:bg-gray-200 flex-shrink-0 transition-all duration-300 group",
              isPinned && "bg-gray-200"
            )}
          >
            {/* Custom Sidebar Toggle Icon */}
            <svg
              className="h-5 w-5 text-gray-700"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {/* Rounded rectangle outline */}
              <rect x="3" y="5" width="18" height="14" rx="2" ry="2" />
              {/* Vertical divider line */}
              <line x1="9" y1="5" x2="9" y2="19" />
              {/* Two horizontal lines in left section */}
              <line x1="5" y1="9" x2="8" y2="9" />
              <line x1="5" y1="15" x2="8" y2="15" />
            </svg>
          </Button>
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
            Toggle Sidebar
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
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

      {/* Spacer */}
      <div className="flex-1" />

      {/* Home Icon */}
      <div className="px-2">
        <Link href="/">
          <Button
            variant="ghost"
            className={cn(
              "rounded-full hover:bg-gray-200 flex-shrink-0 transition-all duration-300",
              pathname === "/" && "bg-gray-200",
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

      {/* Resize Handle */}
      {isExpanded && (
        <div
          className="absolute right-0 top-0 bottom-0 w-1 bg-transparent hover:bg-blue-400 cursor-col-resize transition-colors z-10"
          onMouseDown={handleResizeStart}
          style={{ cursor: "col-resize" }}
        >
          <div className="absolute right-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-1 h-12 bg-gray-400 rounded-full opacity-0 hover:opacity-100 transition-opacity" />
        </div>
      )}
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

