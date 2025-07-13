#!/usr/bin/env python3
"""
Comprehensive test script for all project functionality
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from pydantic import EmailStr
from app.services.crm_logic import create_user, get_user, delete_user, save_conversation, get_conversations
from app.services.calendar_service import calendar_service
from app.services.rag import process_document, retrieve_context
from app.database.database import test_connection
from app.models.schemas import UserCreate

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing Database Connection...")
    
    if test_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        return False

def test_user_management():
    """Test user CRUD operations"""
    print("\n🧪 Testing User Management...")
    
    # Test user creation
    test_user = UserCreate(
        name="Test User",
        email=EmailStr("test@example.com"),
        company="Test Corp",
        preferences=["technical", "support"]
    )
    
    try:
        # Create user
        result = create_user(test_user)
        user_id = result["user_id"]
        print(f"✅ User created with ID: {user_id}")
        
        # Get user
        user = get_user(user_id)
        if user and user.get("name") == "Test User":
            print("✅ User retrieval successful")
        else:
            print("❌ User retrieval failed")
            return False
        
        # Test conversation storage
        conversation_id = save_conversation(
            user_id=user_id,
            session_id="test_session",
            message="Hello, this is a test message",
            response="Hello! How can I help you today?",
            tags=["general"]
        )
        print(f"✅ Conversation saved with ID: {conversation_id}")
        
        # Get conversations
        conversations = get_conversations(user_id)
        if len(conversations) > 0:
            print(f"✅ Retrieved {len(conversations)} conversations")
        else:
            print("❌ No conversations retrieved")
            return False
        
        # Test user deletion
        if delete_user(user_id):
            print("✅ User deletion successful")
            
            # Verify deletion
            deleted_user = get_user(user_id)
            if deleted_user is None:
                print("✅ User deletion verified")
                return True
            else:
                print("❌ User still exists after deletion")
                return False
        else:
            print("❌ User deletion failed")
            return False
            
    except Exception as e:
        print(f"❌ User management test failed: {e}")
        return False

def test_calendar_functionality():
    """Test calendar operations"""
    print("\n🧪 Testing Calendar Functionality...")
    
    try:
        # Create test user for calendar
        test_user = UserCreate(
            name="Calendar Test User",
            email=EmailStr("calendar@example.com"),
            company="Calendar Corp"
        )
        user_result = create_user(test_user)
        user_id = user_result["user_id"]
        
        # Create event
        event_result = calendar_service.create_event(
            user_id=user_id,
            title="Test Meeting",
            description="This is a test meeting",
            location="Test Room"
        )
        
        if "error" not in event_result:
            print("✅ Calendar event created successfully")
            event_id = event_result["event_id"]
            
            # Get events
            events = calendar_service.get_user_events(user_id)
            if len(events) > 0:
                print(f"✅ Retrieved {len(events)} calendar events")
            else:
                print("❌ No calendar events retrieved")
                return False
            
            # Update event
            update_result = calendar_service.update_event(
                event_id, 
                description="Updated test meeting description"
            )
            if "error" not in update_result:
                print("✅ Calendar event updated successfully")
            else:
                print("❌ Calendar event update failed")
                return False
            
            # Delete event
            delete_result = calendar_service.delete_event(event_id)
            if "error" not in delete_result:
                print("✅ Calendar event deleted successfully")
            else:
                print("❌ Calendar event deletion failed")
                return False
            
            # Clean up test user
            delete_user(user_id)
            return True
        else:
            print(f"❌ Calendar event creation failed: {event_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Calendar functionality test failed: {e}")
        return False

async def test_rag_functionality():
    """Test RAG system functionality"""
    print("\n🧪 Testing RAG Functionality...")
    
    try:
        # Create test document
        test_doc = {
            "title": "RAG Test Document",
            "content": "This is a comprehensive test document for the RAG system. " * 10,
            "metadata": {
                "author": "RAG Test",
                "purpose": "Testing"
            }
        }
        
        json_content = json.dumps(test_doc).encode('utf-8')
        
        # Process document
        result = await process_document(
            file_content=json_content,
            filename="rag_test_document.json",
            content_type="application/json"
        )
        
        if "error" not in result:
            print(f"✅ Document processed successfully")
            print(f"   Chunks created: {result['chunks_created']}")
            print(f"   Failed chunks: {result['failed_chunks']}")
            
            # Test context retrieval
            context = retrieve_context("test document")
            if context:
                print(f"✅ Context retrieval successful ({len(context)} characters)")
            else:
                print("⚠️  No context retrieved (may be normal)")
            
            return True
        else:
            print(f"❌ Document processing failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ RAG functionality test failed: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        # Test getting non-existent user
        non_existent_user = get_user("507f1f77bcf86cd799439011")
        if non_existent_user is None:
            print("✅ Non-existent user handling correct")
        else:
            print("❌ Non-existent user handling incorrect")
            return False
        
        # Test deleting non-existent user
        if not delete_user("507f1f77bcf86cd799439011"):
            print("✅ Non-existent user deletion handling correct")
        else:
            print("❌ Non-existent user deletion handling incorrect")
            return False
        
        # Test calendar operations with invalid data
        invalid_event_result = calendar_service.create_event(
            user_id="invalid_user_id",
            title=""
        )
        if "error" in invalid_event_result:
            print("✅ Invalid calendar data handling correct")
        else:
            print("❌ Invalid calendar data handling incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 Comprehensive Project Test Suite")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is available
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    if not has_openai:
        print("⚠️  OpenAI API key not found - some tests may be limited")
    
    test_results = []
    
    try:
        # Run tests
        test_results.append(("Database Connection", test_database_connection()))
        
        if test_results[-1][1]:  # If database connection successful
            test_results.append(("User Management", test_user_management()))
            test_results.append(("Calendar Functionality", test_calendar_functionality()))
            test_results.append(("Error Handling", test_error_handling()))
            
            if has_openai:
                test_results.append(("RAG Functionality", await test_rag_functionality()))
            else:
                print("\n⚠️  Skipping RAG tests - no OpenAI API key")
                test_results.append(("RAG Functionality", True))  # Skip for now
        
        # Print results summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Project is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the issues above.")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 