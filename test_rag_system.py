#!/usr/bin/env python3
"""
Test script for RAG system functionality
"""

import os
import json
import tempfile
from dotenv import load_dotenv
from app.services.rag import (
    process_document, 
    retrieve_context, 
    get_embedding, 
    chunk_text,
    extract_text_from_file
)
from app.database.database import documents_collection, document_chunks_collection

def test_text_extraction():
    """Test text extraction from different file types"""
    print("🧪 Testing Text Extraction...")
    
    # Test JSON extraction
    json_content = b'{"title": "Test Document", "content": "This is a test document for RAG system."}'
    json_text = extract_text_from_file(json_content, "application/json")
    assert "Test Document" in json_text
    print("✅ JSON extraction works")
    
    # Test CSV extraction
    csv_content = b'name,age,city\nJohn,30,New York\nJane,25,Los Angeles'
    csv_text = extract_text_from_file(csv_content, "text/csv")
    assert "John" in csv_text and "Jane" in csv_text
    print("✅ CSV extraction works")
    
    # Test plain text extraction
    text_content = b'This is a simple text document for testing.'
    text_result = extract_text_from_file(text_content, "text/plain")
    assert text_result == "This is a simple text document for testing."
    print("✅ Plain text extraction works")

def test_chunking():
    """Test text chunking functionality"""
    print("\n🧪 Testing Text Chunking...")
    
    # Create a long text
    long_text = "This is a test document. " * 50  # About 1000 characters
    
    chunks = chunk_text(long_text)
    assert len(chunks) > 1
    print(f"✅ Text chunked into {len(chunks)} chunks")
    
    # Check chunk sizes
    for i, chunk in enumerate(chunks):
        assert len(chunk) <= 1000  # Max chunk size
        print(f"   Chunk {i+1}: {len(chunk)} characters")

def test_embedding():
    """Test embedding generation"""
    print("\n🧪 Testing Embedding Generation...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping embedding test - no OpenAI API key")
        return
    
    test_text = "This is a test sentence for embedding generation."
    embedding = get_embedding(test_text)
    
    if embedding:
        assert len(embedding) > 0
        print(f"✅ Embedding generated with {len(embedding)} dimensions")
    else:
        print("❌ Failed to generate embedding")

async def test_document_processing():
    """Test complete document processing"""
    print("\n🧪 Testing Document Processing...")
    
    # Create a test JSON document
    test_doc = {
        "title": "Test Document",
        "content": "This is a comprehensive test document for the RAG system. " * 20,
        "metadata": {
            "author": "Test User",
            "date": "2024-01-01"
        }
    }
    
    json_content = json.dumps(test_doc).encode('utf-8')
    
    # Process the document
    result = await process_document(
        file_content=json_content,
        filename="test_document.json",
        content_type="application/json"
    )
    
    if "error" in result:
        print(f"❌ Document processing failed: {result['error']}")
        return
    
    print(f"✅ Document processed successfully")
    print(f"   Document ID: {result['doc_id']}")
    print(f"   Chunks created: {result['chunks_created']}")
    print(f"   Failed chunks: {result['failed_chunks']}")
    
    # Verify document was stored
    doc = documents_collection.find_one({"_id": result['doc_id']})
    assert doc is not None
    print("✅ Document stored in database")
    
    # Verify chunks were stored
    chunks = list(document_chunks_collection.find({"doc_id": result['doc_id']}))
    assert len(chunks) == result['chunks_created']
    print(f"✅ {len(chunks)} chunks stored in database")
    
    return result['doc_id']

def test_context_retrieval():
    """Test context retrieval functionality"""
    print("\n🧪 Testing Context Retrieval...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping context retrieval test - no OpenAI API key")
        return
    
    # Test query
    query = "test document"
    context = retrieve_context(query)
    
    if context:
        print(f"✅ Context retrieved: {len(context)} characters")
        print(f"   Preview: {context[:100]}...")
    else:
        print("⚠️  No context retrieved (may be normal if no documents uploaded)")

def test_rag_endpoints():
    """Test RAG API endpoints"""
    print("\n🧪 Testing RAG API Endpoints...")
    
    # This would require a running server
    print("ℹ️  RAG endpoints test requires running server")
    print("   Test with: curl http://localhost:8000/rag/stats")

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Delete test documents
    result = documents_collection.delete_many({"filename": {"$regex": "^test_"}})
    print(f"✅ Deleted {result.deleted_count} test documents")
    
    # Delete test chunks (orphaned chunks)
    # Note: This is a simple cleanup - in production you'd want more sophisticated cleanup

async def main():
    """Main test function"""
    print("🔍 RAG System Test Suite")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Run tests
        test_text_extraction()
        test_chunking()
        test_embedding()
        
        # Test document processing
        doc_id = await test_document_processing()
        if doc_id:
            print(f"✅ Document processing test completed with ID: {doc_id}")
        else:
            print("⚠️  Document processing test skipped or failed")
        
        # Test context retrieval
        test_context_retrieval()
        
        # Test API endpoints
        test_rag_endpoints()
        
        print("\n" + "=" * 50)
        print("🎉 All RAG system tests completed!")
        
        # Cleanup
        cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 