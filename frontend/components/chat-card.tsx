"use client"

import Link from "next/link"
import { FileText, File, FileType } from "lucide-react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ChatCardProps {
  title: string
  icon: React.ReactNode
  iconColor: string
  href: string
}

export function ChatCard({ title, icon, iconColor, href }: ChatCardProps) {
  return (
    <Link href={href}>
      <Card className="h-48 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer border-gray-200 shadow-sm flex flex-col justify-between p-6 relative overflow-hidden">
        <h3 className="text-center text-gray-800 font-medium text-lg">
          {title}
        </h3>
        <div className={cn("absolute bottom-4 right-4", iconColor)}>
          {icon}
        </div>
      </Card>
    </Link>
  )
}

export function ChatWithPDFCard() {
  return (
    <ChatCard
      title="Chat with a PDF"
      icon={<FileText className="h-8 w-8 text-blue-500" />}
      iconColor="text-blue-500"
      href="/chat"
    />
  )
}

export function ChatWithTextCard() {
  return (
    <ChatCard
      title="Chat with a Text File"
      icon={<File className="h-8 w-8 text-orange-500" />}
      iconColor="text-orange-500"
      href="/chat"
    />
  )
}

export function ChatWithWordCard() {
  return (
    <ChatCard
      title="Chat with a word document"
      icon={<FileType className="h-8 w-8 text-green-500" />}
      iconColor="text-green-500"
      href="/chat"
    />
  )
}

