#!/bin/bash
# Phase 2: Chat Feature (Backend) - Test Cases
# Test suite for POST /api/chat endpoint

BASE_URL="http://localhost:8000/api/chat"

echo "=========================================="
echo "Phase 2: Chat Feature (Backend) - Test Suite"
echo "=========================================="
echo ""

# TC2.1: Test chat endpoint with valid question
echo "=== TC2.1: Valid Question ==="
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"What is this document about?\"}"
echo "Expected: Status 200, response contains {\"answer\": \"...\", \"sources\": [...]}"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC2.2: Test chat endpoint with empty question
echo "=== TC2.2: Empty Question ==="
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"\"}"
echo "Expected: Status 400 with error message"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC2.3: Test chat endpoint with missing question field
echo "=== TC2.3: Missing Question Field ==="
echo "Request: POST $BASE_URL"
echo "Body: {}"
echo "Expected: Status 422 (validation error)"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC2.4: Test chat endpoint with no documents indexed
echo "=== TC2.4: No Documents Indexed ==="
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"test question\"}"
echo "Expected: Status 200, answer indicates no context found or empty response"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "test question"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC2.5: Test chat endpoint response time
echo "=== TC2.5: Response Time ==="
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"test question\"}"
echo "Expected: Response time < 30 seconds (reasonable for LLM processing)"
echo ""
time curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "test question"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

echo "=========================================="
echo "Phase 2 Test Suite Complete"
echo "=========================================="

