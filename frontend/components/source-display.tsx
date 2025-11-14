"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"
import type { SourceInfo } from "@/lib/api/client"

interface SourceDisplayProps {
  sources: SourceInfo[]
}

interface SourceCardProps {
  source: SourceInfo
  index: number
}

function SourceCard({ source, index }: SourceCardProps) {
  const [isCardExpanded, setIsCardExpanded] = useState(true)
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false)

  // Extract metadata
  const metadata = source.metadata || {}
  
  // Extract source file name - prefer filename over source path
  const fileName = metadata.filename || (metadata.source ? metadata.source.split('/').pop() : "") || "Unknown source"
  const sourcePath = metadata.source || ""
  
  // Extract headings from dl_meta
  let headings: string[] = []
  if (metadata.dl_meta) {
    try {
      const dl_meta = typeof metadata.dl_meta === 'string' 
        ? JSON.parse(metadata.dl_meta) 
        : metadata.dl_meta
      if (dl_meta.headings && Array.isArray(dl_meta.headings)) {
        headings = dl_meta.headings
      }
    } catch (e) {
      // Ignore parsing errors
    }
  }
  
  // Extract page number from dl_meta
  let pageNumber: number | null = null
  if (metadata.dl_meta) {
    try {
      const dl_meta = typeof metadata.dl_meta === 'string' 
        ? JSON.parse(metadata.dl_meta) 
        : metadata.dl_meta
      if (dl_meta.doc_items && Array.isArray(dl_meta.doc_items)) {
        for (const item of dl_meta.doc_items) {
          const provs = item?.prov
          if (Array.isArray(provs) && provs.length > 0 && provs[0]?.page_no) {
            pageNumber = provs[0].page_no
            break
          }
        }
      }
    } catch (e) {
      // Ignore parsing errors
    }
  }

  // Preview text
  const previewText = source.content
  const previewLength = 200
  const shouldTruncate = previewText.length > previewLength
  const displayPreview = isPreviewExpanded || !shouldTruncate
    ? previewText
    : previewText.substring(0, previewLength) + "..."

  const sourceId = `source-${index + 1}`

  return (
    <div className="border border-gray-200 rounded-lg bg-white hover:border-gray-300 transition-colors">
      {/* Card Header - Always visible */}
      <button
        onClick={() => setIsCardExpanded(!isCardExpanded)}
        className="w-full flex items-center justify-between p-2 text-left hover:bg-gray-50 transition-colors rounded-t-lg"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span id={sourceId} className="font-semibold text-sm text-gray-900">Source {index + 1}</span>
            {pageNumber !== null && (
              <span className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                Page {pageNumber}
              </span>
            )}
          </div>
          <div className="text-xs text-gray-700 font-mono truncate" title={sourcePath}>
            {fileName}
          </div>
          {headings.length > 0 && (
            <div className="text-xs text-gray-600 mt-0.5">
              Section: {headings.join(", ")}
            </div>
          )}
        </div>
        <div className="ml-2 flex-shrink-0">
          {isCardExpanded ? (
            <ChevronUp className="h-3 w-3 text-gray-500" />
          ) : (
            <ChevronDown className="h-3 w-3 text-gray-500" />
          )}
        </div>
      </button>

      {/* Card Body - Expandable */}
      {isCardExpanded && (
        <div className="px-2 pb-2 border-t border-gray-100">
          <div className="pt-2">
            <div className="text-xs font-semibold text-gray-700 mb-1">Preview:</div>
            <div className="text-xs text-gray-600 whitespace-pre-wrap break-words">
              <a
                href={`#${sourceId}`}
                onClick={(e) => {
                  e.preventDefault()
                  const element = document.getElementById(sourceId)
                  if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    // Highlight the source briefly
                    element.classList.add('ring-2', 'ring-blue-400')
                    setTimeout(() => {
                      element.classList.remove('ring-2', 'ring-blue-400')
                    }, 1000)
                  }
                }}
                className="text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
              >
                {displayPreview}
              </a>
            </div>
            {shouldTruncate && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsPreviewExpanded(!isPreviewExpanded)
                }}
                className="mt-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                {isPreviewExpanded ? "Show less" : "Show more"}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function SourceDisplay({ sources }: SourceDisplayProps) {
  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs font-semibold text-gray-700 mb-1">Sources</div>
      <div className="space-y-1.5">
        {sources.map((source, index) => (
          <SourceCard key={index} source={source} index={index} />
        ))}
      </div>
    </div>
  )
}

