"use client"

import { FileText, File, CheckCircle2 } from "lucide-react"

interface FileDisplayProps {
  fileName: string
  fileType: string
  uploadStatus: "success" | "uploading" | "error"
  onRemove?: () => void
}

export function FileDisplay({ fileName, fileType, uploadStatus, onRemove }: FileDisplayProps) {
  // Get file icon based on file type
  const getFileIcon = () => {
    const ext = fileType.toLowerCase()
    if (ext === "pdf") {
      return <FileText className="h-8 w-8 text-red-600" />
    }
    return <File className="h-8 w-8 text-blue-600" />
  }

  // Format file type for display
  const formatFileType = (type: string) => {
    return type.toUpperCase()
  }

  return (
    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 hover:bg-gray-100 transition-colors">
      <div className="flex items-start gap-3">
        {/* File Icon */}
        <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 bg-white rounded border border-gray-200">
          {getFileIcon()}
        </div>
        
        {/* File Info */}
        <div className="flex-1 min-w-0">
          {/* File Name */}
          <p className="text-sm font-medium text-gray-900 truncate">
            {fileName}
          </p>
          
          {/* File Type */}
          <p className="text-xs text-gray-500 mt-0.5">
            {formatFileType(fileType)}
          </p>
          
          {/* Upload Status */}
          {uploadStatus === "success" && (
            <div className="flex items-center gap-1 mt-2">
              <CheckCircle2 className="h-3 w-3 text-green-600 flex-shrink-0" />
              <p className="text-xs text-green-600 font-medium">
                Successfully Uploaded
              </p>
            </div>
          )}
          
          {uploadStatus === "uploading" && (
            <div className="flex items-center gap-1 mt-2">
              <div className="h-3 w-3 border-2 border-gray-400 border-t-transparent rounded-full animate-spin flex-shrink-0" />
              <p className="text-xs text-gray-500">
                Uploading...
              </p>
            </div>
          )}
          
          {uploadStatus === "error" && (
            <div className="flex items-center gap-1 mt-2">
              <p className="text-xs text-red-600">
                Upload failed
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

