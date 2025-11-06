"use client"

import { MessageMarkdown } from "./message-markdown"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Copy, FileText } from "lucide-react"
import { useState } from "react"

export interface Message {
  role: "user" | "assistant"
  content: string
  sources?: Source[]
}

export interface Source {
  page?: number
  section?: string
  source: string
  preview: string
}

interface MessageProps {
  message: Message
}

export function Message({ message }: MessageProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const isUser = message.role === "user"

  return (
    <div
      className={`flex w-full gap-4 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`flex flex-col gap-2 max-w-[80%] ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground"
          }`}
        >
          <MessageMarkdown content={message.content} />
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full space-y-2 mt-2">
            <div className="text-xs text-muted-foreground font-medium">
              Sources:
            </div>
            {message.sources.map((source, idx) => (
              <Card key={idx} className="p-3">
                <CardContent className="p-0 space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    {source.page && (
                      <Badge variant="outline">Page {source.page}</Badge>
                    )}
                    {source.section && (
                      <Badge variant="outline">{source.section}</Badge>
                    )}
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <FileText className="h-3 w-3" />
                      {source.source}
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {source.preview}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!isUser && (
          <Button
            variant="ghost"
            size="sm"
            onClick={copyToClipboard}
            className="h-7 w-7 p-0"
          >
            <Copy className="h-4 w-4" />
            {copied && (
              <span className="absolute -top-8 text-xs">Copied!</span>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}

