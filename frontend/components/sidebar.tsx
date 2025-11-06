"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, Home, RotateCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function Sidebar() {
  const pathname = usePathname()
  const [isExpanded, setIsExpanded] = useState(false)

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
        <Link href="/">
          <Button
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
        </Link>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

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

