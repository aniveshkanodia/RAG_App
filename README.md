# RAG Application

A Retrieval-Augmented Generation (RAG) application that enables document-based question answering using local LLMs via Ollama, vector storage with ChromaDB, and document registry with Supabase.

## Project Overview

This RAG application allows users to:
- Upload documents (PDF, TXT, DOCX, DOC, XLSX, XLS) for indexing
- Chat with documents using natural language questions
- Maintain conversation isolation (each conversation only accesses its own documents)
- Evaluate RAG performance using multiple metrics

The application is built with:
- **Backend**: FastAPI (Python) with LangChain for RAG pipeline
- **Frontend**: Next.js (React/TypeScript) with Tailwind CSS
- **LLM/Embeddings**: Ollama (local models)
- **Vector Database**: ChromaDB (local storage)
- **Document Registry**: Supabase (cloud database)
- **Evaluation**: DeepEval for RAG metrics

## Architecture

```
┌─────────────┐
│   Frontend  │  Next.js App (Port 3000)
│  (Next.js)  │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────┐
│   Backend   │  FastAPI Server (Port 8000)
│  (FastAPI)  │
└──────┬──────┘
       │
       ├──► Ollama (Port 11434)
       │    ├── LLM: deepseek-r1:1.5b
       │    └── Embeddings: qwen3-embedding:0.6b
       │
       ├──► ChromaDB (./db/chroma_db)
       │    └── Vector storage for document chunks
       │
       └──► Supabase
            └── Document registry (metadata, conversation mapping)
```

### Key Components

1. **Document Processing**: 
   - Uses DoclingLoader for structured documents (PDF, DOCX, XLSX) with semantic chunking
   - Uses standard text splitting for plain text files (TXT)
   - Extracts metadata and creates embeddings for each chunk

2. **Retrieval**:
   - Semantic search using ChromaDB vector database
   - Retrieves top-k most relevant chunks (default: 5)
   - Conversation isolation: only retrieves documents from the same conversation

3. **Generation**:
   - Uses Ollama LLM to generate answers based on retrieved context
   - Includes source citations in responses

4. **Evaluation**:
   - Offline evaluation on conversation logs
   - Golden dataset evaluation with ground truth
   - Multiple metrics: Faithfulness, Answer Relevancy, Contextual Precision/Recall/Relevancy

## Prerequisites

Before setting up the application, ensure you have:

- **Python 3.8+** with pip
- **Node.js 18+** and npm
- **Ollama** installed and running (see [SETUP_GUIDE.md](./SETUP_GUIDE.md))
- **Supabase account** and project (see [SETUP_GUIDE.md](./SETUP_GUIDE.md))

## Quick Start

1. **Install Ollama and pull required models**:
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # In another terminal, pull required models
   ollama pull qwen3-embedding:0.6b
   ollama pull deepseek-r1:1.5b
   ```

2. **Set up Supabase**:
   - Create a Supabase project at https://supabase.com
   - Create a `documents` table (see [SETUP_GUIDE.md](./SETUP_GUIDE.md) for schema)
   - Get your project URL and anon key

3. **Clone and set up the project**:
   ```bash
   cd RAG_App
   
   # Backend setup
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file from template
   cp .env.example .env
   # Edit .env with your Supabase credentials
   
   # Frontend setup
   cd frontend
   npm install
   cd ..
   ```

4. **Run the application**:
   ```bash
   # Terminal 1: Start backend
   python run_server.py
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

5. **Access the application**:
   - Open http://localhost:3000 in your browser

For detailed setup instructions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md).

## Usage Guide

### Uploading Documents

1. Click "New Chat" or start a conversation
2. Click the upload button or drag-and-drop a file
3. Supported file types: PDF, TXT, DOCX, DOC, XLSX, XLS
4. Wait for the upload confirmation message showing number of chunks indexed

**Note**: Each conversation maintains its own document collection. Documents uploaded in one conversation are not accessible in other conversations.

### Chatting with Documents

1. After uploading documents, type your question in the chat input
2. The system will:
   - Retrieve relevant chunks from your uploaded documents
   - Generate an answer based on the retrieved context
   - Display source citations
3. Continue the conversation with follow-up questions

### Conversation Isolation

Each conversation has a unique `conversation_id`. Documents are tagged with this ID when uploaded, and retrieval only searches documents from the same conversation. This ensures:
- Privacy: Documents from one conversation are not accessible in another
- Organization: Each conversation maintains its own document context
- Clean separation: No cross-contamination between different use cases

## Evaluation

The application includes comprehensive evaluation capabilities for assessing RAG performance.

### Available Evaluation Scripts

1. **Offline Log Evaluation** (`evaluation/run_offline_deepeval.py`):
   - Evaluates conversation logs from `logs/rag_turns.jsonl`
   - Uses reference-free metrics (no ground truth required)
   - Metrics: Answer Relevancy, Faithfulness, Contextual Relevancy, Contextual Precision, Contextual Recall

2. **Golden Dataset Evaluation** (`evaluation/evaluate_goldens.py`):
   - Evaluates against a golden dataset with expected answers
   - Requires running RAG API server
   - Metrics: Contextual Precision, Contextual Recall

3. **Reference-Free Log Evaluation** (`evaluation/evaluate_logs.py`):
   - Similar to offline evaluation but only reference-free metrics
   - Metrics: Answer Relevancy, Faithfulness, Contextual Relevancy

For detailed evaluation instructions, see [EVALUATION_GUIDE.md](./EVALUATION_GUIDE.md).

## Configuration

### Environment Variables

See [.env.example](./.env.example) for all available environment variables.

**Required**:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous/public key

**Optional** (with defaults):
- `API_HOST`: Backend server host (default: "0.0.0.0")
- `API_PORT`: Backend server port (default: "8000")
- `API_RELOAD`: Enable auto-reload for development (default: "true")
- `RAG_LOG_PATH`: Path to RAG turn logs (default: "logs/rag_turns.jsonl")
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend (default: "http://localhost:8000")

### Model Configuration

Models are configured in `backend/core/config.py`:
- **Embedding Model**: `qwen3-embedding:0.6b`
- **LLM Model**: `deepseek-r1:1.5b`
- **Top-K Retrieval**: 5 documents (configurable)

### Vector Database

- **Location**: `./db/chroma_db` (created automatically)
- **Collection Name**: `documents`
- **Storage**: Local filesystem (persistent across restarts)

### Chunking Strategy

- **Docling Files** (PDF, DOCX, DOC, XLSX, XLS): Uses DoclingLoader with `ExportType.DOC_CHUNKS` for semantic chunking that preserves document structure
- **Plain Text** (TXT): Uses RecursiveCharacterTextSplitter with chunk size 1000 and overlap 100

## Project Structure

```
RAG_App/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes and models
│   ├── config/             # Configuration and settings
│   ├── core/               # Core RAG components (LLM, embeddings, vectorstore)
│   ├── processing/         # Document loaders and chunkers
│   ├── services/           # Business logic (RAG service, document service)
│   └── utils/              # Utilities (document registry, metadata)
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app router pages
│   ├── components/         # React components
│   └── lib/                # Utilities and API client
├── evaluation/             # Evaluation scripts
│   ├── evaluate_goldens.py      # Golden dataset evaluation
│   ├── evaluate_logs.py         # Reference-free log evaluation
│   └── run_offline_deepeval.py  # Full offline evaluation
├── scripts/                # Utility scripts
│   └── clear_chroma_db.py  # Clear vector database
├── logs/                   # RAG conversation logs (JSONL format)
├── db/                     # ChromaDB storage (created automatically)
├── requirements.txt        # Python dependencies
├── run_server.py          # Backend server entry point
└── README.md              # This file
```

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError` when running server
- **Solution**: Ensure you're in the virtual environment: `source venv/bin/activate`

**Issue**: `Connection refused` to Ollama
- **Solution**: Ensure Ollama is running: `ollama serve` or check if it's running as a service

**Issue**: `SUPABASE_URL` or `SUPABASE_ANON_KEY` not found
- **Solution**: Create `.env` file from `.env.example` and add your Supabase credentials

**Issue**: ChromaDB errors
- **Solution**: Try clearing the database: `python scripts/clear_chroma_db.py`

### Frontend Issues

**Issue**: Cannot connect to backend
- **Solution**: 
  - Ensure backend is running on port 8000
  - Check `NEXT_PUBLIC_API_URL` in frontend environment (or use default)
  - Check CORS settings in backend

**Issue**: Build errors
- **Solution**: 
  - Delete `node_modules` and `.next` directory
  - Run `npm install` again
  - Check Node.js version (requires 18+)

### Model Issues

**Issue**: Model not found errors
- **Solution**: Ensure models are pulled: `ollama pull qwen3-embedding:0.6b` and `ollama pull deepseek-r1:1.5b`

**Issue**: Slow response times
- **Solution**: 
  - Models are running locally; first request may be slower (model loading)
  - Consider using smaller models or optimizing chunk size
  - Check system resources (CPU/RAM)

### Evaluation Issues

**Issue**: Evaluation script can't find logs
- **Solution**: Ensure `RAG_LOG_PATH` points to correct file, or logs exist at default location `logs/rag_turns.jsonl`

**Issue**: Evaluation fails with Ollama connection errors
- **Solution**: Ensure Ollama is running and evaluation model is pulled (default: `qwen3:0.6b`)

## Clearing the Database

To clear all indexed documents:

```bash
# Clear ChromaDB collection and cache
python scripts/clear_chroma_db.py

# Full reset (also deletes database directory and Supabase registry)
python scripts/clear_chroma_db.py --full
```

**Warning**: This will delete all indexed documents. The database will be automatically recreated when you upload new documents.

## Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [DeepEval Documentation](https://docs.confident-ai.com/)

## License

This is a learning project. Feel free to use and modify as needed.

## Support

For setup issues, refer to:
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed setup instructions
- [EVALUATION_GUIDE.md](./EVALUATION_GUIDE.md) - Evaluation documentation
