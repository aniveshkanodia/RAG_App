#!/usr/bin/env python3
"""
Quick test script to verify RAG logging functionality.
Run this after starting the API server to test logging.
"""

import requests
import json
import os
import time
from pathlib import Path

API_BASE_URL = "http://localhost:8000"
LOG_PATH = os.getenv("RAG_LOG_PATH", "logs/rag_turns.jsonl")


def test_chat_request(question: str, conversation_id: str = None, turn_index: int = None):
    """Send a test chat request."""
    url = f"{API_BASE_URL}/api/chat"
    payload = {"question": question}
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if turn_index is not None:
        payload["turn_index"] = turn_index
    
    print(f"\n📤 Sending request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Response received: {len(data.get('answer', ''))} characters")
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def check_log_file():
    """Check if log file exists and display its contents."""
    log_file = Path(LOG_PATH)
    
    if not log_file.exists():
        print(f"\n❌ Log file not found at: {LOG_PATH}")
        return False
    
    print(f"\n✅ Log file found at: {LOG_PATH}")
    print(f"   Size: {log_file.stat().st_size} bytes")
    
    # Read and display log entries
    print("\n📋 Log entries:")
    print("=" * 80)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            try:
                record = json.loads(line.strip())
                print(f"\nEntry {i}:")
                print(f"  Timestamp: {record.get('timestamp')}")
                print(f"  Conversation ID: {record.get('conversation_id')}")
                print(f"  Turn Index: {record.get('turn_index')}")
                print(f"  User Query: {record.get('user_query', '')[:60]}...")
                print(f"  Answer Length: {len(record.get('answer', ''))} chars")
                print(f"  Contexts: {len(record.get('contexts', []))} chunks")
                print(f"  Chunking Strategy: {record.get('chunking_strategy')}")
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Invalid JSON on line {i}: {e}")
    
    print("=" * 80)
    return True


def main():
    """Run logging tests."""
    print("🧪 Testing RAG Logging Functionality")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️  Server returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start it first:")
        print("   python run_server.py")
        return
    
    # Test 1: Request without conversation_id (should generate one)
    print("\n" + "=" * 80)
    print("Test 1: Request without conversation_id")
    print("=" * 80)
    test_chat_request("What is artificial intelligence?")
    time.sleep(1)  # Give server time to write log
    
    # Test 2: Request with conversation_id (same conversation)
    print("\n" + "=" * 80)
    print("Test 2: Request with conversation_id (same conversation)")
    print("=" * 80)
    conv_id = "test-conversation-123"
    test_chat_request("Tell me more about machine learning.", conversation_id=conv_id, turn_index=0)
    time.sleep(1)
    test_chat_request("What are neural networks?", conversation_id=conv_id, turn_index=1)
    time.sleep(1)
    
    # Test 3: Request with conversation_id but no turn_index (should auto-increment)
    print("\n" + "=" * 80)
    print("Test 3: Request with conversation_id but no turn_index")
    print("=" * 80)
    conv_id2 = "test-conversation-456"
    test_chat_request("What is Python?", conversation_id=conv_id2)
    time.sleep(1)
    test_chat_request("What is JavaScript?", conversation_id=conv_id2)
    time.sleep(1)
    
    # Check log file
    print("\n" + "=" * 80)
    print("Checking Log File")
    print("=" * 80)
    check_log_file()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()

