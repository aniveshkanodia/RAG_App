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

## Test Cases Included

### Phase 2 Test Cases:
- **TC2.1**: Test chat endpoint with valid question
- **TC2.2**: Test chat endpoint with empty question
- **TC2.3**: Test chat endpoint with missing question field
- **TC2.4**: Test chat endpoint with no documents indexed
- **TC2.5**: Test chat endpoint response time

## Prerequisites

Before running the tests, ensure:
1. The FastAPI server is running on `http://localhost:8000`
2. You have `curl` installed
3. The server is accessible

## Running Tests

Make sure the server is running:
```bash
fastapi dev api_server.py
# or
uvicorn api_server:app --reload --port 8000
```

Then run the test script:
```bash
./TestCases/phase2_tests.sh
```

