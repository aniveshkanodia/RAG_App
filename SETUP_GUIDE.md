# RAG Application Setup Guide

This guide provides detailed step-by-step instructions for setting up the RAG application on macOS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Ollama Setup](#ollama-setup)
3. [Supabase Setup](#supabase-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- **macOS** (this guide is for macOS)
- **Python 3.8+** installed (check with `python3 --version`)
- **Node.js 18+** and npm installed (check with `node --version` and `npm --version`)
- **Homebrew** installed (for Ollama installation)

### Installing Prerequisites

If you don't have Python 3.8+:
```bash
# Install Python via Homebrew
brew install python3
```

If you don't have Node.js:
```bash
# Install Node.js via Homebrew
brew install node
```

## Ollama Setup

Ollama is used to run local LLM and embedding models. Follow these steps to set it up.

### Step 1: Install Ollama

```bash
# Install Ollama using Homebrew
brew install ollama
```

Alternatively, download from https://ollama.ai/download

### Step 2: Start Ollama Service

Ollama runs as a service. Start it with:

```bash
ollama serve
```

This will start the Ollama server on `http://localhost:11434`. Keep this terminal window open.

**Note**: On macOS, Ollama may also run as a background service. If `ollama serve` says the service is already running, you can proceed to the next step.

### Step 3: Pull Required Models

Open a **new terminal window** (keep the Ollama service running) and pull the required models:

```bash
# Pull embedding model (required)
ollama pull qwen3-embedding:0.6b

# Pull LLM model (required)
ollama pull deepseek-r1:1.5b

# Pull evaluation model (optional, for running evaluations)
ollama pull qwen3:0.6b
```

**Expected Output**:
```
pulling manifest
pulling 00e1317cbf74... 100% ▕████████████████▏ 123 MB
pulling 7c23fb36d801... 100% ▕████████████████▏ 456 MB
...
```

This may take several minutes depending on your internet connection. The models are:
- `qwen3-embedding:0.6b`: ~600MB (for generating embeddings)
- `deepseek-r1:1.5b`: ~1.5GB (for generating answers)
- `qwen3:0.6b`: ~600MB (for evaluation, optional)

### Step 4: Verify Models

Verify that models are installed:

```bash
ollama list
```

You should see:
```
NAME                      SIZE    MODIFIED
deepseek-r1:1.5b         1.5 GB  2 hours ago
qwen3-embedding:0.6b     600 MB  2 hours ago
qwen3:0.6b               600 MB  2 hours ago
```

### Step 5: Test Ollama Connection

Test that Ollama is responding:

```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with your installed models.

## Supabase Setup

Supabase is used as a document registry to track uploaded documents and their metadata.

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click "Start your project" or "Sign up"
3. Create an account (you can use GitHub, Google, or email)

### Step 2: Create a New Project

1. After logging in, click "New Project"
2. Fill in:
   - **Name**: Choose a name (e.g., "rag-app")
   - **Database Password**: Create a strong password (save it securely)
   - **Region**: Choose the closest region
3. Click "Create new project"
4. Wait for the project to be created (2-3 minutes)

### Step 3: Get Project Credentials

1. In your project dashboard, go to **Settings** → **API**
2. Find the following values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: A long string starting with `eyJ...`

**Important**: Save these values - you'll need them for the `.env` file.

### Step 4: Create Documents Table

1. In your Supabase dashboard, go to **Table Editor**
2. Click "New Table"
3. Configure the table:
   - **Name**: `documents`
   - **Description**: "Document registry for RAG application"
4. Add the following columns:

| Column Name | Type | Default | Nullable | Primary Key |
|------------|------|---------|----------|-------------|
| `content_hash` | `text` | - | No | Yes |
| `filename` | `text` | - | No | No |
| `file_size` | `bigint` | - | No | No |
| `chunk_count` | `integer` | - | No | No |
| `conversation_id` | `text` | - | Yes | No |
| `upload_timestamp` | `timestamptz` | `now()` | No | No |
| `last_indexed_timestamp` | `timestamptz` | `now()` | No | No |

**SQL Alternative**: You can also run this SQL in the SQL Editor:

```sql
CREATE TABLE documents (
    content_hash TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    chunk_count INTEGER NOT NULL,
    conversation_id TEXT,
    upload_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_indexed_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Step 5: Configure Row Level Security (RLS)

The application uses the `anon` key, so we need to enable RLS and create policies.

1. Go to **Authentication** → **Policies**
2. Find the `documents` table
3. Click "Enable RLS" if not already enabled
4. Create the following policies (click "New Policy" for each):

**Policy 1: Allow SELECT for anon**
- Policy Name: `Allow anon to select documents`
- Allowed Operation: `SELECT`
- Target Roles: `anon`
- USING Expression: `true`

**Policy 2: Allow INSERT for anon**
- Policy Name: `Allow anon to insert documents`
- Allowed Operation: `INSERT`
- Target Roles: `anon`
- WITH CHECK Expression: `true`

**Policy 3: Allow UPDATE for anon**
- Policy Name: `Allow anon to update documents`
- Allowed Operation: `UPDATE`
- Target Roles: `anon`
- USING Expression: `true`
- WITH CHECK Expression: `true`

**Policy 4: Allow DELETE for anon**
- Policy Name: `Allow anon to delete documents`
- Allowed Operation: `DELETE`
- Target Roles: `anon`
- USING Expression: `true`

**SQL Alternative**: Run this in the SQL Editor:

```sql
-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow anon to select documents"
    ON documents FOR SELECT
    TO anon
    USING (true);

CREATE POLICY "Allow anon to insert documents"
    ON documents FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY "Allow anon to update documents"
    ON documents FOR UPDATE
    TO anon
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow anon to delete documents"
    ON documents FOR DELETE
    TO anon
    USING (true);
```

### Step 6: Verify Supabase Setup

Test the connection using the Supabase client:

```bash
# Install Supabase Python client (if not already installed)
pip install supabase

# Test connection (create a test script)
python3 << EOF
from supabase import create_client
import os

url = "YOUR_SUPABASE_URL"
key = "YOUR_ANON_KEY"

client = create_client(url, key)
result = client.table("documents").select("*").limit(1).execute()
print("✓ Supabase connection successful!")
print(f"Table exists: {result is not None}")
EOF
```

Replace `YOUR_SUPABASE_URL` and `YOUR_ANON_KEY` with your actual values.

## Backend Setup

### Step 1: Navigate to Project Directory

```bash
cd /path/to/RAG_App
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

**Note**: Always activate the virtual environment before working with the backend:
```bash
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
# Ensure you're in the project root directory
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI and Uvicorn (web server)
- LangChain and related packages (RAG pipeline)
- ChromaDB (vector database)
- Supabase (document registry)
- DeepEval (evaluation)

**Expected Output**:
```
Collecting fastapi...
Collecting langchain-ollama...
...
Successfully installed ...
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your Supabase credentials
nano .env  # or use your preferred editor
```

Edit the `.env` file and set:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**Important**: 
- Replace `your-project-id` with your actual Supabase project ID
- Replace `your-anon-key-here` with your actual anon key
- Do NOT commit the `.env` file to version control

### Step 5: Create Required Directories

```bash
# Create logs directory (if it doesn't exist)
mkdir -p logs

# Create db directory (will be created automatically, but you can create it now)
mkdir -p db
```

### Step 6: Verify Backend Setup

Test that the backend can start:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Test import (should not error)
python3 -c "from backend.main import app; print('✓ Backend imports successful')"

# Check Ollama connection
python3 -c "
from backend.core.embeddings import get_embeddings
emb = get_embeddings()
print('✓ Ollama embeddings connection successful')
"
```

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

This will install all required packages including:
- Next.js 14
- React 18
- Tailwind CSS
- TypeScript

**Expected Output**:
```
added 500+ packages, and audited 501 packages in 30s
```

### Step 3: Configure Frontend Environment (Optional)

The frontend defaults to `http://localhost:8000` for the backend API. If your backend runs on a different URL, create a `.env.local` file:

```bash
# In the frontend/ directory
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

Or set it when running:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

### Step 4: Verify Frontend Setup

Test that the frontend can build:

```bash
# Build the frontend (this may take a minute)
npm run build
```

If the build succeeds, you're ready to run the application.

## Verification

### Step 1: Start Backend Server

In **Terminal 1**:

```bash
cd /path/to/RAG_App
source venv/bin/activate
python run_server.py
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 2: Test Backend Health

In **Terminal 2** (new terminal):

```bash
curl http://localhost:8000/api/health
```

**Expected Output**:
```json
{"status":"healthy"}
```

### Step 3: Start Frontend Server

In **Terminal 2**:

```bash
cd /path/to/RAG_App/frontend
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 14.2.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

### Step 4: Access the Application

1. Open your browser
2. Navigate to http://localhost:3000
3. You should see the RAG application interface

### Step 5: Test Document Upload

1. Click "New Chat" or start a conversation
2. Upload a test PDF or text file
3. Wait for the upload confirmation
4. Try asking a question about the document

If everything works, your setup is complete!

## Troubleshooting

### Ollama Issues

**Problem**: `Connection refused` when starting backend
- **Solution**: Ensure Ollama is running: `ollama serve` or check if it's running as a service

**Problem**: Model not found errors
- **Solution**: Verify models are pulled: `ollama list`. If missing, run `ollama pull <model-name>`

**Problem**: Slow model loading
- **Solution**: First request is slower (model loads into memory). Subsequent requests are faster.

### Supabase Issues

**Problem**: `SUPABASE_URL` or `SUPABASE_ANON_KEY` not found
- **Solution**: 
  - Check `.env` file exists in project root
  - Verify variables are set correctly (no quotes around values)
  - Ensure you're using the `anon/public` key, not the `service_role` key

**Problem**: RLS policy errors
- **Solution**: 
  - Verify RLS is enabled on the `documents` table
  - Check that all four policies (SELECT, INSERT, UPDATE, DELETE) are created
  - Ensure policies allow `anon` role

**Problem**: Table doesn't exist
- **Solution**: Create the `documents` table following Step 4 in Supabase Setup

### Backend Issues

**Problem**: `ModuleNotFoundError` when running server
- **Solution**: 
  - Ensure virtual environment is activated: `source venv/bin/activate`
  - Reinstall dependencies: `pip install -r requirements.txt`

**Problem**: Port 8000 already in use
- **Solution**: 
  - Change port in `.env`: `API_PORT=8001`
  - Or stop the process using port 8000: `lsof -ti:8000 | xargs kill`

**Problem**: ChromaDB errors
- **Solution**: 
  - Clear the database: `python scripts/clear_chroma_db.py`
  - Check disk space and permissions on `./db/chroma_db`

### Frontend Issues

**Problem**: Cannot connect to backend
- **Solution**: 
  - Verify backend is running on port 8000
  - Check `NEXT_PUBLIC_API_URL` in frontend `.env.local` (or use default)
  - Check browser console for CORS errors

**Problem**: Build errors
- **Solution**: 
  - Delete `node_modules` and `.next`: `rm -rf node_modules .next`
  - Reinstall: `npm install`
  - Check Node.js version: `node --version` (should be 18+)

**Problem**: Port 3000 already in use
- **Solution**: 
  - Use a different port: `npm run dev -- -p 3001`
  - Or stop the process: `lsof -ti:3000 | xargs kill`

### General Issues

**Problem**: Python version mismatch
- **Solution**: Ensure Python 3.8+ is used. Check with `python3 --version`

**Problem**: Permission errors
- **Solution**: 
  - Check file permissions on project directory
  - Ensure you have write access to `./db` and `./logs` directories

## Next Steps

Once setup is complete:

1. Read the [README.md](./README.md) for usage instructions
2. Check [EVALUATION_GUIDE.md](./EVALUATION_GUIDE.md) to learn about evaluation
3. Upload some documents and start chatting!
4. Review logs in `logs/rag_turns.jsonl` to see conversation history

## Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
