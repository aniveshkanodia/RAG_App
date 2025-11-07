# Phase 3: Chat Feature (Frontend) - Manual Test Checklist

This document provides a manual testing checklist for Phase 3 frontend features that require browser interaction.

## Prerequisites

1. Backend server running: `fastapi dev api_server.py` (on http://localhost:8000)
2. Frontend server running: `cd frontend && npm run dev` (on http://localhost:3000)
3. Browser open to http://localhost:3000

## Test Cases

### TC3.4: Test chat window sends message on submit

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Type a message in the input field (e.g., "What is this document about?")
4. Click the Send button

**Expected Result:**
- ✓ User message appears in chat window immediately
- ✓ Message is displayed in blue bubble on the right side
- ✓ Input field is cleared after sending

**Status:** ☐ Pass ☐ Fail

---

### TC3.5: Test loading state appears while waiting for response

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Type a message and click Send
4. Observe the UI while waiting for response

**Expected Result:**
- ✓ Send button shows a spinning loader instead of send icon
- ✓ "Thinking..." message appears in chat window
- ✓ Input field is disabled during loading
- ✓ Send button is disabled during loading

**Status:** ☐ Pass ☐ Fail

---

### TC3.6: Test assistant response appears after API call

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Type a message and click Send
4. Wait for the response

**Expected Result:**
- ✓ Assistant response appears in chat window
- ✓ Response is displayed in white bubble on the left side
- ✓ Response contains the answer from the backend
- ✓ If sources are available, they are displayed with metadata
- ✓ Loading indicator disappears when response arrives

**Status:** ☐ Pass ☐ Fail

---

### TC3.7: Test error handling displays user-friendly message

**Steps:**
1. Stop the backend server (or disconnect from network)
2. Open the application in browser
3. Click "New Chat" button
4. Type a message and click Send
5. Observe the error message

**Expected Result:**
- ✓ Error message appears in chat window
- ✓ Error message is displayed in red bubble
- ✓ Error message is user-friendly (e.g., "Failed to get response from server")
- ✓ Loading indicator disappears when error occurs

**Status:** ☐ Pass ☐ Fail

---

### TC3.8: Test Enter key submits message

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Type a message in the input field
4. Press Enter key (without Shift)

**Expected Result:**
- ✓ Message is sent when Enter is pressed
- ✓ Message appears in chat window
- ✓ Input field is cleared
- ✓ Shift+Enter does NOT send the message (allows multi-line input)

**Status:** ☐ Pass ☐ Fail

---

### TC3.9: Test empty message cannot be sent

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Try to send an empty message (click Send with empty input)
4. Try to send a message with only whitespace

**Expected Result:**
- ✓ Send button is disabled when input is empty
- ✓ Send button is disabled when input contains only whitespace
- ✓ No message is sent when input is empty
- ✓ Input field remains empty (no error message needed)

**Status:** ☐ Pass ☐ Fail

---

## Additional Integration Tests

### Test Source Attribution Display

**Steps:**
1. Upload a document (if file upload is implemented)
2. Ask a question about the document
3. Check the response

**Expected Result:**
- ✓ Response includes source information
- ✓ Sources show file name, section, and preview
- ✓ Sources are formatted clearly

**Status:** ☐ Pass ☐ Fail

---

### Test Multiple Messages in Conversation

**Steps:**
1. Open the application in browser
2. Click "New Chat" button
3. Send multiple messages in sequence
4. Verify conversation history

**Expected Result:**
- ✓ All messages appear in order
- ✓ User messages on right, assistant messages on left
- ✓ Conversation history is maintained
- ✓ Previous messages remain visible when scrolling

**Status:** ☐ Pass ☐ Fail

---

## Notes

- Some tests require the backend to be running
- Error handling test (TC3.7) requires stopping the backend
- All tests should be performed in a modern browser (Chrome, Firefox, Safari, Edge)

