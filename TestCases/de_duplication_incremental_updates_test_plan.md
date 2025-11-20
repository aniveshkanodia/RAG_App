# Test Plan: De-duplication and Incremental Updates

## Overview
This test plan covers the de-duplication and incremental update features for the RAG application. The system should prevent duplicate indexing and handle document updates efficiently.

## Test Environment Setup

### Prerequisites
1. Supabase project "RAG App" is accessible
2. ChromaDB is initialized and empty (or can be cleared)
3. **RLS policies are configured** on the `documents` table (see `RLS_SETUP.md`)
4. Test files available:
   - `test_document_v1.pdf` (original version)
   - `test_document_v2.pdf` (modified version, same filename)
   - `duplicate_content.pdf` (different filename, same content as v1)
   - `new_document.pdf` (completely new file)

### Environment Variables
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key

### RLS Verification
Before running tests, verify RLS policies are in place:
```sql
SELECT policyname, cmd, roles 
FROM pg_policies 
WHERE tablename = 'documents';
```
All four operations (SELECT, INSERT, UPDATE, DELETE) should have policies for the `anon` role.

## Test Categories

### 1. De-duplication Tests

#### Test 1.1: Same File Uploaded Twice
**Objective**: Verify that uploading the same file twice skips re-indexing.

**Steps**:
1. Upload `test_document_v1.pdf` for the first time
2. Verify document is indexed (check ChromaDB and Supabase registry)
3. Upload `test_document_v1.pdf` again (same file)
4. Verify system returns "already indexed" message
5. Verify no duplicate chunks in ChromaDB
6. Verify registry shows only one entry

**Expected Results**:
- First upload: Success message with chunk count
- Second upload: "already indexed (duplicate content detected)" message
- ChromaDB: Only one set of chunks exists
- Supabase: Only one document record with matching hash

**Pass Criteria**: 
- ✅ No duplicate chunks created
- ✅ Appropriate skip message returned
- ✅ Registry shows single entry

---

#### Test 1.2: Different Filename, Same Content
**Objective**: Verify that files with different names but same content are detected as duplicates.

**Steps**:
1. Upload `test_document_v1.pdf`
2. Upload `duplicate_content.pdf` (same content, different filename)
3. Verify system detects duplicate by hash
4. Check registry for both filenames with same hash

**Expected Results**:
- First upload: Successfully indexed
- Second upload: "already indexed (duplicate content detected)" message
- Registry: Two entries with same `content_hash` but different `filename` values

**Pass Criteria**:
- ✅ Duplicate detected by hash (not filename)
- ✅ Appropriate skip message
- ✅ Registry correctly tracks both filenames

---

#### Test 1.3: Hash Computation Accuracy
**Objective**: Verify SHA256 hash computation is consistent.

**Steps**:
1. Compute hash of `test_document_v1.pdf` using utility function
2. Upload the file
3. Query registry for the document by hash
4. Verify hash matches exactly

**Expected Results**:
- Hash computed before upload matches hash in registry
- Hash is 64-character hexadecimal string

**Pass Criteria**:
- ✅ Hash computation is deterministic
- ✅ Hash format is correct (SHA256 hex)

---

### 2. Incremental Update Tests

#### Test 2.1: Same Filename, Different Content (Update Scenario)
**Objective**: Verify that updated documents delete old chunks and re-index.

**Steps**:
1. Upload `test_document_v1.pdf`
2. Note the chunk count and hash from registry
3. Upload `test_document_v2.pdf` (same filename, modified content)
4. Verify old chunks are deleted
5. Verify new chunks are indexed
6. Verify registry is updated with new hash

**Expected Results**:
- First upload: Successfully indexed with hash H1
- Second upload: "Successfully updated and re-indexed" message
- ChromaDB: Old chunks with hash H1 deleted, new chunks with hash H2 exist
- Registry: Document record updated with new hash H2 and new chunk count
- No chunks with old hash H1 remain

**Pass Criteria**:
- ✅ Old chunks deleted from ChromaDB
- ✅ New chunks indexed successfully
- ✅ Registry updated with new hash
- ✅ Update message returned

---

#### Test 2.2: Multiple Sequential Updates
**Objective**: Verify system handles multiple updates to same filename correctly.

**Steps**:
1. Upload `test_document_v1.pdf` → hash H1
2. Upload `test_document_v2.pdf` → hash H2
3. Upload `test_document_v1.pdf` again → hash H1
4. Verify each update deletes previous chunks
5. Verify final state has only chunks with hash H1

**Expected Results**:
- Each update deletes previous version's chunks
- Final state: Only chunks with latest hash (H1)
- Registry: Shows latest hash and chunk count
- No orphaned chunks from intermediate versions

**Pass Criteria**:
- ✅ Each update processes correctly
- ✅ No orphaned chunks remain
- ✅ Registry reflects latest state

---

#### Test 2.3: Update with Different Conversation ID
**Objective**: Verify updates work correctly with conversation-scoped documents.

**Steps**:
1. Upload `test_document_v1.pdf` with `conversation_id="conv1"`
2. Upload `test_document_v2.pdf` with `conversation_id="conv1"` (same conversation)
3. Verify old chunks deleted and new ones indexed
4. Verify conversation_id preserved in registry and chunks

**Expected Results**:
- Update processes correctly within same conversation
- Conversation ID maintained in registry
- Chunk metadata includes correct conversation_id

**Pass Criteria**:
- ✅ Update works with conversation scoping
- ✅ Conversation ID preserved

---

### 3. New Document Tests

#### Test 3.1: Completely New Document
**Objective**: Verify new documents are indexed normally.

**Steps**:
1. Upload `new_document.pdf` (never seen before)
2. Verify document is indexed
3. Verify registry entry created
4. Verify chunk metadata includes hash and timestamps

**Expected Results**:
- Success message with chunk count
- Registry entry created with correct metadata
- Chunks indexed in ChromaDB
- Chunk metadata includes content_hash, upload_timestamp, last_indexed_timestamp

**Pass Criteria**:
- ✅ New document indexed successfully
- ✅ Registry entry created
- ✅ Metadata complete and correct

---

### 4. Registry and Metadata Tests

#### Test 4.1: Registry Query by Hash
**Objective**: Verify document lookup by content hash works correctly.

**Steps**:
1. Upload a test document
2. Compute hash of the file
3. Query registry using `get_document_by_hash()`
4. Verify returned document matches

**Expected Results**:
- Function returns document record
- All fields present and correct (filename, hash, size, timestamps, chunk_count)

**Pass Criteria**:
- ✅ Query returns correct document
- ✅ All metadata fields present

---

#### Test 4.2: Registry Query by Filename
**Objective**: Verify querying by filename returns all versions.

**Steps**:
1. Upload `test_document_v1.pdf` (hash H1)
2. Upload `test_document_v2.pdf` (same filename, hash H2)
3. Query registry using `get_document_by_filename()`
4. Verify all versions returned

**Expected Results**:
- Function returns list of documents
- Both versions (H1 and H2) present in results
- Results sorted appropriately

**Pass Criteria**:
- ✅ Returns all versions of filename
- ✅ Multiple entries with different hashes

---

#### Test 4.3: Chunk Metadata Mirroring
**Objective**: Verify chunk metadata mirrors registry essentials.

**Steps**:
1. Upload a test document
2. Retrieve chunks from ChromaDB
3. Verify chunk metadata includes:
   - `content_hash`
   - `upload_timestamp`
   - `last_indexed_timestamp`
   - `filename`
4. Compare with registry entry

**Expected Results**:
- All chunks have `content_hash` matching registry
- Timestamps in chunks match registry timestamps
- Filename matches registry filename

**Pass Criteria**:
- ✅ Chunk metadata includes all essential fields
- ✅ Metadata matches registry values

---

### 5. Error Handling Tests

#### Test 5.1: Supabase Connection Failure
**Objective**: Verify graceful handling of Supabase connection issues.

**Steps**:
1. Set invalid `SUPABASE_URL` or `SUPABASE_ANON_KEY`
2. Attempt to upload a document
3. Verify error handling

**Expected Results**:
- Error caught and logged
- User-friendly error message returned
- System doesn't crash

**Pass Criteria**:
- ✅ Errors handled gracefully
- ✅ Appropriate error messages

---

#### Test 5.2: Hash Computation Failure
**Objective**: Verify handling of file read errors during hash computation.

**Steps**:
1. Attempt to hash a non-existent file
2. Attempt to hash a file with read permissions denied
3. Verify error handling

**Expected Results**:
- `FileNotFoundError` raised for missing file
- Appropriate error for permission issues
- Error propagated with clear message

**Pass Criteria**:
- ✅ Errors raised appropriately
- ✅ Error messages are clear

---

#### Test 5.3: Deletion Failure Recovery
**Objective**: Verify system continues even if chunk deletion fails.

**Steps**:
1. Upload a document
2. Simulate deletion failure (mock ChromaDB error)
3. Attempt update
4. Verify system attempts re-indexing despite deletion failure

**Expected Results**:
- Deletion failure logged
- System continues with re-indexing
- New chunks still created (may have duplicates, but system doesn't crash)

**Pass Criteria**:
- ✅ System doesn't crash on deletion failure
- ✅ Errors logged appropriately

---

#### Test 5.4: Registry Update Failure
**Objective**: Verify system handles registry update failures gracefully.

**Steps**:
1. Upload a document
2. Simulate Supabase update failure
3. Verify indexing still completes
4. Verify error is logged

**Expected Results**:
- Document indexed successfully
- Registry update failure logged
- System continues operation (best-effort sync)

**Pass Criteria**:
- ✅ Indexing completes despite registry failure
- ✅ Errors logged for debugging

---

#### Test 5.5: Row Level Security (RLS) Compatibility
**Objective**: Verify system works correctly with RLS enabled on documents table.

**Steps**:
1. Verify RLS is enabled on documents table
2. Verify all four RLS policies exist (SELECT, INSERT, UPDATE, DELETE)
3. Upload a new document
4. Query document by hash
5. Update document metadata
6. Verify all operations succeed

**Expected Results**:
- All CRUD operations work with RLS enabled
- No "permission denied" or "row-level security" errors
- Error messages are clear if policies are missing

**Pass Criteria**:
- ✅ All operations succeed with RLS enabled
- ✅ Clear error messages if policies are missing
- ✅ No security-related errors in logs

**SQL Verification**:
```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'documents';

-- Check policies exist
SELECT policyname, cmd, roles FROM pg_policies WHERE tablename = 'documents';
```

---

### 6. Integration Tests

#### Test 6.1: Full Workflow - New Document
**Objective**: Verify complete workflow for new document.

**Steps**:
1. Upload new document via API endpoint
2. Verify:
   - Hash computed
   - Registry checked (not found)
   - Document loaded and chunked
   - Chunks indexed
   - Registry entry created
   - Status message returned

**Expected Results**:
- All steps execute successfully
- Status message indicates success
- Data consistent across ChromaDB and Supabase

**Pass Criteria**:
- ✅ Complete workflow succeeds
- ✅ Data consistency maintained

---

#### Test 6.2: Full Workflow - Duplicate Detection
**Objective**: Verify complete workflow for duplicate document.

**Steps**:
1. Upload document (first time)
2. Upload same document again
3. Verify:
   - Hash computed
   - Registry checked (found)
   - Processing skipped
   - Appropriate message returned

**Expected Results**:
- Duplicate detected early (before processing)
- No unnecessary processing
- Appropriate skip message

**Pass Criteria**:
- ✅ Duplicate detected efficiently
- ✅ Processing skipped correctly

---

#### Test 6.3: Full Workflow - Update Scenario
**Objective**: Verify complete workflow for document update.

**Steps**:
1. Upload document v1
2. Upload document v2 (same filename, different content)
3. Verify:
   - Hash computed (different from v1)
   - Registry checked (filename found, hash different)
   - Old chunks deleted
   - New chunks indexed
   - Registry updated

**Expected Results**:
- Update detected correctly
- Old chunks removed
- New chunks indexed
- Registry reflects update

**Pass Criteria**:
- ✅ Update workflow completes successfully
- ✅ No orphaned chunks
- ✅ Registry updated correctly

---

### 7. Performance Tests

#### Test 7.1: Large File Handling
**Objective**: Verify system handles large files efficiently.

**Steps**:
1. Upload a large file (>10MB)
2. Measure time for hash computation
3. Verify processing completes successfully

**Expected Results**:
- Hash computation completes (may take time for large files)
- Processing continues normally
- No memory issues

**Pass Criteria**:
- ✅ Large files processed successfully
- ✅ Hash computation efficient (chunked reading)

---

#### Test 7.2: Multiple Concurrent Uploads
**Objective**: Verify system handles concurrent uploads correctly.

**Steps**:
1. Upload multiple different files concurrently
2. Verify all process correctly
3. Verify no race conditions in registry

**Expected Results**:
- All uploads process successfully
- Registry entries created correctly
- No data corruption

**Pass Criteria**:
- ✅ Concurrent uploads handled correctly
- ✅ No race conditions

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Supabase project accessible
- [ ] ChromaDB initialized/cleared
- [ ] Test files prepared
- [ ] Environment variables set
- [ ] Dependencies installed (`supabase` package)

### Test Execution Order
1. [ ] Run de-duplication tests (1.1, 1.2, 1.3)
2. [ ] Run incremental update tests (2.1, 2.2, 2.3)
3. [ ] Run new document tests (3.1)
4. [ ] Run registry and metadata tests (4.1, 4.2, 4.3)
5. [ ] Run error handling tests (5.1, 5.2, 5.3, 5.4)
6. [ ] Run integration tests (6.1, 6.2, 6.3)
7. [ ] Run performance tests (7.1, 7.2)

### Post-Test Verification
- [ ] ChromaDB state verified
- [ ] Supabase registry verified
- [ ] No orphaned data
- [ ] Logs reviewed for errors

## Test Data Requirements

### Test Files Needed
1. `test_document_v1.pdf` - Original document (can be any PDF)
2. `test_document_v2.pdf` - Modified version of v1 (same filename, different content)
3. `duplicate_content.pdf` - Same content as v1, different filename
4. `new_document.pdf` - Completely new document
5. `large_file.pdf` - File >10MB for performance testing

### Registry Verification Queries
```sql
-- Check all documents
SELECT * FROM documents ORDER BY created_at DESC;

-- Check for duplicates (same hash, different filenames)
SELECT content_hash, COUNT(*) as count, array_agg(filename) as filenames
FROM documents
GROUP BY content_hash
HAVING COUNT(*) > 1;

-- Check for updates (same filename, different hashes)
SELECT filename, COUNT(*) as versions, array_agg(content_hash) as hashes
FROM documents
GROUP BY filename
HAVING COUNT(*) > 1;
```

## Success Criteria

### Functional Requirements
- ✅ Duplicate documents (same hash) are detected and skipped
- ✅ Updated documents (same filename, different hash) delete old chunks and re-index
- ✅ New documents are indexed normally
- ✅ Registry accurately tracks all documents
- ✅ Chunk metadata mirrors registry essentials

### Non-Functional Requirements
- ✅ Error handling is graceful (no crashes)
- ✅ Performance acceptable for large files
- ✅ Concurrent uploads handled correctly
- ✅ Data consistency maintained between ChromaDB and Supabase

## Known Limitations / Edge Cases

1. **Race Conditions**: If same file uploaded simultaneously from different requests, both may pass duplicate check. Unique constraint in Supabase will handle this.
2. **Partial Failures**: If indexing succeeds but registry update fails, data may be inconsistent. System logs errors for manual reconciliation.
3. **Chunk ID Reconstruction**: Chunk IDs are reconstructed from filename pattern. If filename sanitization changes, old chunks may not be deletable by ID pattern.

## Notes

- All timestamps are stored in UTC
- Hash is SHA256 (64 hex characters)
- Registry uses `content_hash` as UNIQUE constraint (hash is the real identity)
- Filename is not unique (allows multiple versions)
- Deletion uses metadata filters, not chunk IDs (more reliable)

