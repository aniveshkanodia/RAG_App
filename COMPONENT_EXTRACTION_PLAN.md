# Component Extraction Plan for RAG Application

## Approach: Selective Component Extraction

Instead of cloning the entire chatbot-ui repo, we'll extract only the essential components we need for a RAG application.

## Components to Extract

### 1. Core Chat Components
- **Chat Messages Display** (`components/messages/message.tsx`)
  - Display user and assistant messages
  - Markdown rendering
  - Copy functionality
  
- **Chat Input** (`components/chat/chat-input.tsx`)
  - Text input with send button
  - Keyboard shortcuts
  - File attachment support

### 2. UI Components (from `components/ui/`)
- Button
- Input
- Textarea
- Card
- ScrollArea
- Separator
- Badge (for source citations)

### 3. Message Rendering
- **Markdown Renderer** (`components/messages/message-markdown.tsx`)
  - Code syntax highlighting
  - Math rendering
  - GFM support

### 4. File Upload
- **File Picker** (`components/chat/file-picker.tsx`)
  - Drag & drop
  - File type validation
  - Upload progress

## Minimal Frontend Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main chat page
│   └── api/
│       ├── chat/route.ts   # Chat API endpoint
│       └── upload/route.ts # File upload endpoint
├── components/
│   ├── chat/
│   │   ├── chat-input.tsx
│   │   └── file-picker.tsx
│   ├── messages/
│   │   ├── message.tsx
│   │   └── message-markdown.tsx
│   └── ui/                 # Shadcn UI components
│       ├── button.tsx
│       ├── input.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   └── utils.ts            # Utility functions
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Dependencies Needed

### Core
- `next` - React framework
- `react` & `react-dom`
- `typescript`

### UI
- `tailwindcss` - Styling
- `@radix-ui/*` - UI primitives (for components)
- `lucide-react` - Icons
- `class-variance-authority` - Component variants
- `clsx` & `tailwind-merge` - Class utilities

### Markdown
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub Flavored Markdown
- `react-syntax-highlighter` - Code highlighting

### API
- `ai` - Vercel AI SDK (for streaming)

## Backend Integration

### FastAPI Backend (`backend/api.py`)
- `/chat` - RAG query endpoint
- `/upload` - Document upload endpoint
- `/health` - Health check

### Next.js API Routes
- `/api/chat` - Proxy to FastAPI `/chat`
- `/api/upload` - Proxy to FastAPI `/upload`

## Steps

1. ✅ Create minimal Next.js structure
2. ✅ Extract UI components (button, input, card, etc.)
3. ✅ Extract chat message component
4. ✅ Extract chat input component
5. ✅ Extract file upload component
6. ✅ Create FastAPI backend
7. ✅ Create Next.js API routes
8. ✅ Integrate everything
9. ✅ Add RAG-specific features (source citations)

## Customizations for RAG

1. **Source Citations**
   - Display source documents below answers
   - Show page numbers, sections, previews
   - Clickable source links

2. **Document Management**
   - List uploaded documents
   - Delete documents
   - Show document status

3. **RAG Settings**
   - Top-K retrieval count
   - Temperature
   - Model selection

