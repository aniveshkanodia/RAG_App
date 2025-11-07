<!-- 480652e3-35fd-448c-9552-42b14b82d095 32d13097-3cc4-45f2-85b6-de05e780b4f7 -->
# Frontend-Backend Integration Plan

## Overview

Transform the Gradio-based backend into a REST API using FastAPI, and connect the Next.js frontend to consume these APIs for chat and file upload functionality. Implementation will be done step-by-step, one feature at a time.

## Step-by-Step Implementation Order

### Phase 1: Backend Foundation

1. **Step 1**: Create basic FastAPI server structure (`api_server.py`) with CORS configuration for port 8000
2. **Step 2**: Add health check endpoint (`GET /api/health`) to verify server is running
3. **Step 3**: Update `requirements.txt` with FastAPI dependencies (fastapi, uvicorn, python-multipart)

**Test Cases for Phase 1:**

- **TC1.1**: Start FastAPI server and verify it runs on port 8000
  - Command: `uvicorn api_server:app --reload --port 8000`
  - Expected: Server starts without errors
- **TC1.2**: Test health check endpoint returns 200 OK
  - Request: `GET http://localhost:8000/api/health`
  - Expected Response: `{"status": "healthy"}` with status code 200
- **TC1.3**: Verify CORS headers are present in response
  - Request: `OPTIONS http://localhost:8000/api/health` from browser
  - Expected: Response includes `Access-Control-Allow-Origin: *` header
- **TC1.4**: Verify dependencies are installed
  - Command: `pip list | grep -E "fastapi|uvicorn|python-multipart"`
  - Expected: All three packages are listed

### Phase 2: Chat Feature (Backend)

**Backend File Organization (Simpler Structure):**

When implementing Phase 2, organize backend files using a simpler structure:

```text
RAG_App/
├── api_server.py               # FastAPI app with routes
├── backend/                    # Backend logic (NEW)
│   ├── __init__.py
│   ├── rag.py                  # RAG pipeline (extracted from rag_docling.py)
│   │   - init_rag()
│   │   - run_pipeline()
│   │   - answer_question()
│   │
│   └── document_processor.py   # Document processing (extracted from rag_docling.py)
│       - load_document()
│       - process_documents_for_chunking()
│       - process_and_index_file()
│
├── rag_docling.py              # Keep as reference, gradually migrate
├── requirements.txt
└── db/                          # Database (existing)
```

**Migration Steps for Phase 2:**

1. Create `backend/` directory with `__init__.py`
2. Extract RAG functions from `rag_docling.py` to `backend/rag.py`:
   - `init_rag()`
   - `run_pipeline()`
   - `answer_question()`
3. Import in `api_server.py`: `from backend.rag import run_pipeline, answer_question`
4. Keep `rag_docling.py` as reference during migration

**Note:** Document processing functions will be extracted to `backend/document_processor.py` in Phase 4.

4.**Step 4**: Implement chat endpoint (`POST /api/chat`) that accepts questions and returns answers using `run_pipeline()` from `backend/rag.py`
5.**Step 5**: Test chat endpoint independently with curl/Postman to verify backend works

**Test Cases for Phase 2:**

- **TC2.1**: Test chat endpoint with valid question
  - Request: `POST http://localhost:8000/api/chat`
  - Body: `{"question": "What is this document about?"}`
  - Expected: Status 200, response contains `{"answer": "...", "sources": [...]}`
- **TC2.2**: Test chat endpoint with empty question
  - Request: `POST http://localhost:8000/api/chat`
  - Body: `{"question": ""}`
  - Expected: Status 400 with error message
- **TC2.3**: Test chat endpoint with missing question field
  - Request: `POST http://localhost:8000/api/chat`
  - Body: `{}`
  - Expected: Status 422 (validation error)
- **TC2.4**: Test chat endpoint with no documents indexed
  - Request: `POST http://localhost:8000/api/chat`
  - Body: `{"question": "test question"}`
  - Expected: Status 200, answer indicates no context found or empty response
- **TC2.5**: Test chat endpoint response time
  - Request: `POST http://localhost:8000/api/chat`
  - Body: `{"question": "test question"}`
  - Expected: Response time < 30 seconds (reasonable for LLM processing)

### Phase 3: Chat Feature (Frontend)

6.**Step 6**: Create API client utility (`frontend/lib/api/client.ts`) with base URL configuration
7.**Step 7**: Implement `chat()` function in API client to call `POST /api/chat`
8.**Step 8**: Update `chat-window.tsx` `handleSend()` to call chat API instead of placeholder
9.**Step 9**: Add loading states and error handling to chat window for better UX

**Test Cases for Phase 3:**

- **TC3.1**: Verify API client file exists and exports chat function
  - File: `frontend/lib/api/client.ts`
  - Expected: File exists with `chat(question: string)` function exported
- **TC3.2**: Test API client base URL configuration
  - Expected: Base URL defaults to `http://localhost:8000`
- **TC3.3**: Test chat function makes correct API call
  - Mock fetch and verify: POST to `/api/chat` with correct body
  - Expected: Request includes `{"question": "test"}` in body
- **TC3.4**: Test chat window sends message on submit
  - Action: Type message and click send
  - Expected: User message appears in chat window
- **TC3.5**: Test loading state appears while waiting for response
  - Action: Send message
  - Expected: Loading indicator appears (spinner or "thinking..." message)
- **TC3.6**: Test assistant response appears after API call
  - Action: Send message and wait for response
  - Expected: Assistant message appears with answer from backend
- **TC3.7**: Test error handling displays user-friendly message
  - Action: Stop backend server and send message
  - Expected: Error message displayed to user (e.g., "Failed to get response")
- **TC3.8**: Test Enter key submits message
  - Action: Type message and press Enter
  - Expected: Message is sent (same as clicking send button)
- **TC3.9**: Test empty message cannot be sent
  - Action: Try to send empty or whitespace-only message
  - Expected: Message is not sent, input remains empty

### Bug Fix: Home Page Message Sending

**Issue:** Users cannot send messages from the home page. They must create a new chat first.

**Ideal Behavior:** 
- User should be able to start a conversation directly from the home page
- When a user sends a message from home page, it should automatically create a new chat and navigate to it
- The message should be sent and displayed in the new chat

**Implementation Steps:**

1. **Step BF1**: Add state management to `HomeScreen` component
   - Add `useState` for input value
   - Add `useState` for loading state
   - Import `useChatSessions` hook and `useRouter` from Next.js

2. **Step BF2**: Implement `handleSend` function in `HomeScreen`
   - Create a new chat session using `createNewChat()` from `useChatSessions` hook
   - Navigate to `/chat?chatId={newChatId}` using Next.js router
   - Store the message to send after navigation completes
   - Send the message once on the chat page (or use URL params to trigger send)

3. **Step BF3**: Add Enter key support
   - Add `onKeyPress` handler to Input field
   - Call `handleSend` when Enter is pressed (without Shift)

4. **Step BF4**: Add loading state indicator
   - Show loading spinner in send button when sending from home page
   - Disable input and send button during loading

5. **Step BF5**: Handle message sending after navigation
   - Option A: Use URL search params to pass message and trigger send on chat page
   - Option B: Store message in session storage and retrieve on chat page
   - Option C: Send message immediately after navigation using the chatId

**Files to Modify:**
- `frontend/components/home-screen.tsx` - Add message sending functionality, state management, and navigation

**Test Cases for Bug Fix:**

- **TCBF1**: Test message sending from home page
  - Action: Type message on home page and click send
  - Expected: New chat is created, navigates to chat page, message is sent and displayed

- **TCBF2**: Test Enter key from home page
  - Action: Type message on home page and press Enter
  - Expected: Same as TCBF1

- **TCBF3**: Test loading state on home page
  - Action: Send message from home page
  - Expected: Loading spinner appears, input is disabled

- **TCBF4**: Test empty message validation on home page
  - Action: Try to send empty message from home page
  - Expected: Message is not sent, no navigation occurs

### Phase 4: File Upload Feature (Backend)

10.**Step 10**: Implement file upload endpoint (`POST /api/upload`) that processes files using `process_and_index_file()` from `rag_docling.py`
11.**Step 11**: Test file upload endpoint independently to verify backend works

**Test Cases for Phase 4:**

- **TC4.1**: Test file upload with valid PDF file
  - Request: `POST http://localhost:8000/api/upload`
  - Body: FormData with PDF file
  - Expected: Status 200, response contains `{"message": "Successfully uploaded...", "chunks": N}`
- **TC4.2**: Test file upload with valid TXT file
  - Request: `POST http://localhost:8000/api/upload`
  - Body: FormData with TXT file
  - Expected: Status 200, success message
- **TC4.3**: Test file upload with valid DOCX file
  - Request: `POST http://localhost:8000/api/upload`
  - Body: FormData with DOCX file
  - Expected: Status 200, success message
- **TC4.4**: Test file upload with unsupported file type
  - Request: `POST http://localhost:8000/api/upload`
  - Body: FormData with .jpg file
  - Expected: Status 400 with error message about unsupported file type
- **TC4.5**: Test file upload with no file
  - Request: `POST http://localhost:8000/api/upload`
  - Body: Empty FormData
  - Expected: Status 400 with error message
- **TC4.6**: Test file upload processes and indexes document
  - Action: Upload PDF, then query chat endpoint
  - Expected: Chat endpoint can answer questions about uploaded document
- **TC4.7**: Test file upload with large file (>10MB)
  - Request: `POST http://localhost:8000/api/upload`
  - Body: FormData with large PDF
  - Expected: Status 200 or appropriate timeout/error handling
- **TC4.8**: Test multiple file uploads
  - Action: Upload multiple files sequentially
  - Expected: All files are processed and indexed successfully

### Phase 5: File Upload Feature (Frontend)

12.**Step 12**: Implement `uploadFile()` function in API client to call `POST /api/upload` with FormData
13.**Step 13**: Update file upload handler in `chat-window.tsx` to call upload API
14.**Step 14**: Update file upload handler in `home-screen.tsx` to call upload API
15.**Step 15**: Add upload progress/status feedback in UI components

**Test Cases for Phase 5:**

- **TC5.1**: Verify API client has uploadFile function
  - File: `frontend/lib/api/client.ts`
  - Expected: `uploadFile(file: File)` function exported
- **TC5.2**: Test uploadFile makes correct API call
  - Mock fetch and verify: POST to `/api/upload` with FormData
  - Expected: Request includes file in FormData
- **TC5.3**: Test file upload from chat window
  - Action: Click upload button in chat window, select PDF file
  - Expected: File is uploaded and success message appears
- **TC5.4**: Test file upload from home screen
  - Action: Click upload button on home screen, select PDF file
  - Expected: File is uploaded and success message appears
- **TC5.5**: Test upload progress indicator
  - Action: Upload large file
  - Expected: Progress indicator or "Uploading..." message appears
- **TC5.6**: Test upload success message
  - Action: Upload file successfully
  - Expected: Success message displayed (e.g., "File uploaded successfully")
- **TC5.7**: Test upload error handling
  - Action: Upload unsupported file type or stop backend
  - Expected: Error message displayed to user
- **TC5.8**: Test file input accepts correct file types
  - Action: Click file input
  - Expected: File picker shows only .pdf, .txt, .doc, .docx files
- **TC5.9**: Test uploaded file can be queried immediately
  - Action: Upload file, then send chat message about file content
  - Expected: Chat can answer questions about uploaded file
- **TC5.10**: Test multiple file uploads
  - Action: Upload multiple files sequentially
  - Expected: All uploads succeed and files are indexed

## Implementation Details

### API Response Format

- `/api/chat` response: `{ answer: string, sources?: Array<{content: string, metadata: any}> }`
- `/api/upload` response: `{ message: string, chunks?: number }`

### Error Handling

- Frontend: Display error messages in UI
- Backend: Return appropriate HTTP status codes (400, 500, etc.)

### File Upload Flow

1. User selects file in frontend
2. Frontend sends file as FormData to `/api/upload`
3. Backend saves file temporarily, processes with `process_and_index_file()` from `backend/document_processor.py`
4. Backend returns success/error message
5. Frontend displays status to user

### Chat Flow

1. User submits question in frontend
2. Frontend sends POST to `/api/chat` with question
3. Backend calls `run_pipeline()` from `backend/rag.py`
4. Backend returns answer and sources
5. Frontend displays response in chat window

### To-dos

- [ ] Step 1: Create basic FastAPI server structure (api_server.py) with CORS configuration for port 8000
- [ ] Step 2: Add health check endpoint (GET /api/health) to verify server is running
- [ ] Step 3: Update requirements.txt with fastapi, uvicorn, and python-multipart dependencies
- [ ] Step 4: Implement chat endpoint (POST /api/chat) that accepts questions and returns answers using run_pipeline() from backend/rag.py
- [ ] Step 5: Test chat endpoint independently with curl/Postman to verify backend works
- [ ] Step 6: Create API client utility (frontend/lib/api/client.ts) with base URL configuration
- [ ] Step 7: Implement chat() function in API client to call POST /api/chat
- [ ] Step 8: Update chat-window.tsx handleSend() to call chat API instead of placeholder
- [ ] Step 9: Add loading states and error handling to chat window for better UX
- [ ] Step 10: Implement file upload endpoint (POST /api/upload) that processes files using process_and_index_file() from backend/document_processor.py
- [ ] Step 11: Test file upload endpoint independently to verify backend works
- [ ] Step 12: Implement uploadFile() function in API client to call POST /api/upload with FormData
- [ ] Step 13: Update file upload handler in chat-window.tsx to call upload API
- [ ] Step 14: Update file upload handler in home-screen.tsx to call upload API
- [ ] Step 15: Add upload progress/status feedback in UI components
