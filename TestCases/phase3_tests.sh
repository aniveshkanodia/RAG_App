#!/bin/bash
# Phase 3: Chat Feature (Frontend) - Test Cases
# Test suite for frontend chat integration with backend API

BASE_URL="http://localhost:8000/api/chat"
FRONTEND_DIR="frontend"
API_CLIENT_FILE="frontend/lib/api/client.ts"

echo "=========================================="
echo "Phase 3: Chat Feature (Frontend) - Test Suite"
echo "=========================================="
echo ""

# TC3.1: Verify API client file exists and exports chat function
echo "=== TC3.1: Verify API Client File Exists ==="
echo "Checking if $API_CLIENT_FILE exists..."
if [ -f "$API_CLIENT_FILE" ]; then
    echo "✓ File exists"
    echo "Checking if chat function is exported..."
    if grep -q "export.*function chat" "$API_CLIENT_FILE" || grep -q "export.*chat" "$API_CLIENT_FILE"; then
        echo "✓ chat function is exported"
    else
        echo "✗ chat function not found in exports"
    fi
else
    echo "✗ File does not exist"
fi
echo ""
echo "---"
echo ""

# TC3.2: Test API client base URL configuration
echo "=== TC3.2: Test API Client Base URL Configuration ==="
echo "Checking base URL configuration..."
if grep -q "localhost:8000" "$API_CLIENT_FILE"; then
    echo "✓ Base URL defaults to http://localhost:8000"
else
    echo "✗ Base URL configuration not found or incorrect"
fi
echo ""
echo "---"
echo ""

# TC3.3: Test chat function makes correct API call (via backend endpoint)
echo "=== TC3.3: Test Chat Function API Call ==="
echo "Testing that the API endpoint works correctly (simulating frontend call)..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"test\"}"
echo "Expected: Status 200, response contains answer and sources"
echo ""
response=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' \
  -w "\nHTTP_STATUS:%{http_code}")
http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')

if [ "$http_code" = "200" ]; then
    echo "✓ API call successful (Status 200)"
    if echo "$body" | grep -q "answer"; then
        echo "✓ Response contains answer field"
    else
        echo "✗ Response missing answer field"
    fi
else
    echo "✗ API call failed (Status $http_code)"
    echo "Response: $body"
fi
echo ""
echo "---"
echo ""

# TC3.4: Test chat window sends message on submit (API endpoint test)
echo "=== TC3.4: Test Message Submission (API Endpoint) ==="
echo "Testing message submission via API..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"What is this document about?\"}"
echo "Expected: Status 200, valid response"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC3.5: Test loading state (API response time check)
echo "=== TC3.5: Test Response Time (Loading State) ==="
echo "Testing API response time to verify loading state would appear..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"test question\"}"
echo "Expected: Response time < 30 seconds"
echo ""
time curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "test question"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  -o /dev/null -s
echo ""
echo "---"
echo ""

# TC3.6: Test assistant response appears after API call
echo "=== TC3.6: Test Assistant Response ==="
echo "Testing that API returns valid assistant response..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"Hello\"}"
echo "Expected: Status 200, response contains answer"
echo ""
response=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}' \
  -w "\nHTTP_STATUS:%{http_code}")
http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')

if [ "$http_code" = "200" ]; then
    echo "✓ Response received (Status 200)"
    echo "Response preview:"
    echo "$body" | head -c 200
    echo "..."
else
    echo "✗ Request failed (Status $http_code)"
fi
echo ""
echo "---"
echo ""

# TC3.7: Test error handling displays user-friendly message
echo "=== TC3.7: Test Error Handling ==="
echo "Testing error handling with invalid request..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"\"}"
echo "Expected: Status 400 with error message"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "Testing with missing field..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC3.8: Test Enter key submits message (API endpoint test)
echo "=== TC3.8: Test Enter Key Submission (API Endpoint) ==="
echo "Note: This test verifies the API endpoint accepts requests."
echo "Frontend Enter key behavior should be tested manually in browser."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"Enter key test\"}"
echo "Expected: Status 200"
echo ""
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "Enter key test"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
echo "---"
echo ""

# TC3.9: Test empty message cannot be sent
echo "=== TC3.9: Test Empty Message Validation ==="
echo "Testing that empty messages are rejected..."
echo "Request: POST $BASE_URL"
echo "Body: {\"question\": \"\"}"
echo "Expected: Status 400 with error message"
echo ""
response=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}' \
  -w "\nHTTP_STATUS:%{http_code}")
http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)

if [ "$http_code" = "400" ]; then
    echo "✓ Empty message correctly rejected (Status 400)"
else
    echo "✗ Empty message not rejected (Status $http_code)"
fi
echo ""
echo "---"
echo ""

echo "=========================================="
echo "Phase 3 Test Suite Complete"
echo "=========================================="
echo ""
echo "NOTE: Some tests (TC3.4, TC3.5, TC3.8) require manual browser testing:"
echo "  - TC3.4: Verify message appears in chat window after clicking send"
echo "  - TC3.5: Verify loading indicator appears while waiting for response"
echo "  - TC3.8: Verify Enter key submits message (test in browser)"
echo ""
echo "To test in browser:"
echo "  1. Start backend: fastapi dev api_server.py"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Open http://localhost:3000"
echo "  4. Create a new chat and test the features above"

