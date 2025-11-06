# RAG Application Frontend

This is a minimal Next.js frontend that uses extracted components from chatbot-ui for the RAG application.

## Architecture

```
Frontend (Next.js) → API Routes → FastAPI Backend → RAG Pipeline
```

## Components Extracted

We've extracted only the essential components from chatbot-ui:

- **UI Components**: Button, Input, Textarea, Card, ScrollArea, Separator, Badge
- **Chat Components**: ChatInput, Message, MessageMarkdown
- **File Upload**: FilePicker

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```bash
cp .env.local.example .env.local
```

Update `FASTAPI_URL` if your backend runs on a different port.

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Backend Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run FastAPI Backend

```bash
cd backend
python api.py
```

Or using uvicorn directly:

```bash
uvicorn backend.api:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

## Features

- ✅ Chat interface with markdown support
- ✅ File upload (PDF, TXT, DOCX, DOC)
- ✅ Source citations with page numbers and sections
- ✅ Responsive design
- ✅ Dark mode support (via Tailwind)

## Customization

### Adding New Components

If you need additional components from chatbot-ui:

1. Copy the component file from chatbot-ui repository
2. Copy any dependencies (UI components, utilities)
3. Update imports to match your project structure
4. Test the component

### Styling

The app uses Tailwind CSS. Customize colors and styles in:
- `app/globals.css` - CSS variables
- `tailwind.config.ts` - Tailwind configuration

## Project Structure

```
frontend/
├── app/
│   ├── api/          # Next.js API routes
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Main chat page
│   └── globals.css    # Global styles
├── components/
│   ├── chat/         # Chat components
│   ├── messages/     # Message components
│   └── ui/           # UI primitives
├── lib/
│   └── utils.ts      # Utility functions
└── package.json
```

## Notes

- This is a minimal implementation - only essential components are included
- No Supabase or database dependencies - uses your Python backend
- No authentication - add if needed
- Components are simplified versions of chatbot-ui components

