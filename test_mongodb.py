#!/usr/bin/env python3
"""
Test script for MongoDB connection and basic operations
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB configuration
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB", "conversational_ai")
    
    print(f"📡 Connecting to: {mongo_uri}")
    print(f"🗄️  Database: {db_name}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Test connection
        db.command("ping")
        print("✅ MongoDB connection successful!")
        
        # Test collections
        collections = ["users", "conversations", "documents", "document_chunks", "calendar_events"]
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"📊 Collection '{collection_name}': {count} documents")
        
        # Test basic operations
        test_collection = db["test"]
        
        # Insert test document
        result = test_collection.insert_one({"test": "data", "timestamp": "2024-01-01"})
        print(f"✅ Insert test: {result.inserted_id}")
        
        # Find test document
        doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Find test: {doc is not None}")
        
        # Delete test document
        delete_result = test_collection.delete_one({"_id": result.inserted_id})
        print(f"✅ Delete test: {delete_result.deleted_count} document(s)")
        
        # Clean up test collection
        db.drop_collection("test")
        
        print("\n🎉 All MongoDB tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MongoDB is running")
        print("2. Check your MONGO_URI in .env file")
        print("3. Ensure MongoDB is accessible from your network")
        return False

if __name__ == "__main__":
    test_mongodb_connection() 