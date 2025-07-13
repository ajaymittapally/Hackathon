from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection URI and database name from environment
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in .env file")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_default_database()

# Collections
users_collection = db["users"]
conversations_collection = db["conversations"]
documents_collection = db["documents"]
document_chunks_collection = db["document_chunks"]
calendar_events_collection = db["calendar_events"]

# Utility function to test database connection
def test_connection():
    try:
        db.command("ping")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        print(f"Connection URI: {MONGO_URI}")
      
        return False
