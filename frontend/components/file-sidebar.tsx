"use client"

import { FileDisplay } from "./file-display"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { UploadedFile } from "@/lib/utils/chatUtils"

interface FileSidebarProps {
  files: UploadedFile[]
  onRemoveFile?: (fileId: string) => void
  onClose?: () => void
}

export function FileSidebar({ files, onRemoveFile, onClose }: FileSidebarProps) {
  if (files.length === 0) {
    return null
  }

  return (
    <div className="w-64 bg-white border-l border-gray-200 flex flex-col flex-shrink-0">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Uploaded Files</h3>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-6 w-6 rounded-full hover:bg-gray-100"
          >
            <X className="h-4 w-4 text-gray-500" />
          </Button>
        )}
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {files.map((file) => (
          <FileDisplay
            key={file.id}
            fileName={file.name}
            fileType={file.type}
            uploadStatus={file.status}
            onRemove={onRemoveFile ? () => onRemoveFile(file.id) : undefined}
          />
        ))}
      </div>
    </div>
  )
}

