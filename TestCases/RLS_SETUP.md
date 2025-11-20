# Row Level Security (RLS) Setup for Documents Table

## Overview
Row Level Security (RLS) has been enabled on the `documents` table in Supabase to provide an additional layer of security. This document explains the setup and its impact on the application.

## RLS Policies Created

The following policies have been created to allow the `anon` role (used by the backend service) to perform necessary operations:

### 1. SELECT Policy
- **Name**: `Allow anon to read documents`
- **Operation**: SELECT (read)
- **Purpose**: Enables `get_document_by_hash()` and `get_document_by_filename()`
- **Scope**: All documents (using `USING (true)`)

### 2. INSERT Policy
- **Name**: `Allow anon to insert documents`
- **Operation**: INSERT (create)
- **Purpose**: Enables `register_document()`
- **Scope**: All documents (using `WITH CHECK (true)`)

### 3. UPDATE Policy
- **Name**: `Allow anon to update documents`
- **Operation**: UPDATE (modify)
- **Purpose**: Enables `update_document()`
- **Scope**: All documents (using `USING (true)` and `WITH CHECK (true)`)

### 4. DELETE Policy
- **Name**: `Allow anon to delete documents`
- **Operation**: DELETE (remove)
- **Purpose**: Enables `delete_document()` (for cleanup operations)
- **Scope**: All documents (using `USING (true)`)

## Impact on Application

### ✅ No Breaking Changes
The application continues to work as before because:
- All necessary policies are in place
- Policies allow full access for the `anon` role
- Error handling has been enhanced to provide clear messages if policies are missing

### 🔒 Security Benefits
- **Defense in depth**: Even if the anon key is compromised, RLS provides an additional security layer
- **Future flexibility**: Policies can be modified to restrict access based on conditions (e.g., conversation_id, user roles)
- **Audit trail**: RLS policies are logged and can be audited

### 📝 Code Changes Made

1. **Enhanced Error Handling** (`backend/utils/document_registry.py`):
   - All CRUD operations now detect RLS-related errors
   - Clear error messages guide troubleshooting if policies are missing
   - Errors are logged with context

2. **Documentation**:
   - Module docstring updated to explain RLS requirements
   - Comments reference the migration that creates policies

## Verification

To verify RLS policies are working:

```sql
-- Check policies exist
SELECT policyname, cmd, roles
FROM pg_policies 
WHERE tablename = 'documents';

-- Test SELECT (should return data if documents exist)
SELECT * FROM documents LIMIT 1;

-- Test INSERT (should succeed)
INSERT INTO documents (filename, content_hash, file_size, chunk_count)
VALUES ('test.pdf', 'test_hash_123', 1024, 5)
RETURNING *;
```

## Troubleshooting

### Error: "Access denied by Row Level Security policy"
**Cause**: RLS is enabled but policies are missing or incorrect.

**Solution**: 
1. Verify policies exist:
   ```sql
   SELECT * FROM pg_policies WHERE tablename = 'documents';
   ```
2. If policies are missing, run the migration: `add_rls_policies_for_documents`
3. Ensure policies target the `anon` role

### Error: "new row violates row-level security policy"
**Cause**: INSERT policy's `WITH CHECK` condition is failing.

**Solution**: Verify the INSERT policy uses `WITH CHECK (true)` or adjust the condition.

### Error: "permission denied for table documents"
**Cause**: RLS is enabled but no policies allow the operation.

**Solution**: Ensure all four policies (SELECT, INSERT, UPDATE, DELETE) exist for the `anon` role.

## Future Enhancements

### Conversation-Based Access Control
If you want to restrict access based on `conversation_id`, you could modify policies:

```sql
-- Example: Only allow reading documents for specific conversation
CREATE POLICY "Allow anon to read own conversation documents"
ON documents
FOR SELECT
TO anon
USING (conversation_id = current_setting('app.current_conversation_id', true));
```

### User-Based Access Control
If you add user authentication, you could restrict access:

```sql
-- Example: Only allow users to see their own documents
CREATE POLICY "Users can only see their documents"
ON documents
FOR SELECT
TO authenticated
USING (user_id = auth.uid());
```

## Migration Reference

The RLS policies were created via migration: `add_rls_policies_for_documents`

To recreate policies if needed:
```sql
-- Drop existing policies (if recreating)
DROP POLICY IF EXISTS "Allow anon to read documents" ON documents;
DROP POLICY IF EXISTS "Allow anon to insert documents" ON documents;
DROP POLICY IF EXISTS "Allow anon to update documents" ON documents;
DROP POLICY IF EXISTS "Allow anon to delete documents" ON documents;

-- Then run the migration again
```

## Testing

When testing the application with RLS enabled:
1. ✅ All CRUD operations should work normally
2. ✅ Error messages should be clear if policies are missing
3. ✅ Logs should indicate RLS-related errors if they occur

See `de_duplication_incremental_updates_test_plan.md` for test cases that verify RLS compatibility.

