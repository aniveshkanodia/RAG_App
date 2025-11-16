# Test Cases

This directory contains test scripts for each phase of the frontend-backend integration.

## Test Scripts

### Phase 2: Chat Feature (Backend)
- **File**: `phase2_tests.sh`
- **Description**: Test suite for POST /api/chat endpoint
- **Usage**: 
  ```bash
  ./TestCases/phase2_tests.sh
  ```
  Or:
  ```bash
  bash TestCases/phase2_tests.sh
  ```

### Phase 3: Chat Feature (Frontend)
- **File**: `phase3_tests.sh`
- **Description**: Test suite for frontend chat integration with backend API
- **Usage**: 
  ```bash
  ./TestCases/phase3_tests.sh
  ```
  Or:
  ```bash
  bash TestCases/phase3_tests.sh
  ```
- **Manual Tests**: `phase3_manual_tests.md`
  - Detailed checklist for browser-based testing
  - Tests UI interactions, loading states, and error handling

## Test Cases Included

### Phase 2 Test Cases:
- **TC2.1**: Test chat endpoint with valid question
- **TC2.2**: Test chat endpoint with empty question
- **TC2.3**: Test chat endpoint with missing question field
- **TC2.4**: Test chat endpoint with no documents indexed
- **TC2.5**: Test chat endpoint response time

### Phase 3 Test Cases:
- **TC3.1**: Verify API client file exists and exports chat function
- **TC3.2**: Test API client base URL configuration
- **TC3.3**: Test chat function makes correct API call
- **TC3.4**: Test chat window sends message on submit (manual)
- **TC3.5**: Test loading state appears while waiting for response (manual)
- **TC3.6**: Test assistant response appears after API call
- **TC3.7**: Test error handling displays user-friendly message
- **TC3.8**: Test Enter key submits message (manual)
- **TC3.9**: Test empty message cannot be sent

## Prerequisites

Before running the tests, ensure:
1. The FastAPI server is running on `http://localhost:8000`
2. You have `curl` installed
3. The server is accessible

## Running Tests

### Phase 2 Tests (Backend)

Make sure the server is running:
```bash
python run_server.py
```

Then run the test script:
```bash
./TestCases/phase2_tests.sh
```

### Phase 3 Tests (Frontend)

**Automated Tests:**
1. Make sure the backend server is running on `http://localhost:8000`
2. Run the automated test script:
   ```bash
   ./TestCases/phase3_tests.sh
   ```

**Manual Tests:**
1. Start backend: `python run_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to `http://localhost:3000`
4. Follow the checklist in `phase3_manual_tests.md`

