# Quick Start Guide

## What Was Done

✅ Created a minimal Next.js frontend with extracted components from chatbot-ui
✅ Created FastAPI backend wrapper for your RAG pipeline
✅ Connected frontend to backend via API routes
✅ Added RAG-specific features (source citations)

## Quick Setup

### 1. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `frontend/.env.local`:
```bash
FASTAPI_URL=http://localhost:8000
```

### 3. Run Backend

```bash
# Terminal 1
python backend/api.py
```

Or:
```bash
uvicorn backend.api:app --reload --port 8000
```

### 4. Run Frontend

```bash
# Terminal 2
cd frontend
npm run dev
```

### 5. Open Browser

Visit: `http://localhost:3000`

## What You Get

- ✅ Modern chat interface with markdown support
- ✅ File upload (PDF, TXT, DOCX, DOC)
- ✅ Source citations with page numbers
- ✅ Responsive design
- ✅ Clean, minimal codebase

## Project Structure

```
RAG_App/
├── frontend/          # Next.js frontend (extracted components)
│   ├── app/          # Next.js app directory
│   ├── components/   # React components
│   └── lib/          # Utilities
├── backend/          # FastAPI backend
│   └── api.py        # API wrapper
└── rag_docling.py    # Your existing RAG code
```

## Components Extracted

From chatbot-ui, we extracted:
- Chat UI components (input, messages)
- File upload component
- UI primitives (button, card, etc.)
- Markdown renderer

**No full chatbot-ui repo needed!**

## Next Steps

1. Test the application
2. Customize styling in `frontend/app/globals.css`
3. Add more features as needed
4. Deploy when ready

## Troubleshooting

**Backend not connecting?**
- Check `FASTAPI_URL` in `.env.local`
- Ensure backend is running on port 8000
- Check CORS settings in `backend/api.py`

**Frontend not building?**
- Run `npm install` in frontend directory
- Check Node.js version (v18+)
- Check TypeScript errors

**File upload not working?**
- Check file type is supported (PDF, TXT, DOCX, DOC)
- Check file size (default max 10MB)
- Check backend logs for errors

