"use client"

import { useRef } from "react"
import { Plus, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function HomeScreen() {
  const fileInputRef = useRef<HTMLInputElement>(null)

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
              type="text"
              placeholder="Ask anything from here"
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-700 placeholder:text-gray-400"
            />

            {/* Send Button */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                className="w-8 h-8 rounded-full bg-white hover:bg-gray-200"
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

