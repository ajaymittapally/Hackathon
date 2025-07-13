import os
import csv
import json
import PyPDF2

import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.database.database import documents_collection, document_chunks_collection
from dotenv import load_dotenv

# Try to import numpy, fallback to manual calculation if not available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

load_dotenv()

# Initialize OpenAI client for embeddings
openai_client = None
if os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SIMILARITY_THRESHOLD = 0.1
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_CHUNKS_PER_DOCUMENT = 100  # Prevent processing extremely large documents

def retrieve_context(query: str) -> str:
    """Retrieve relevant context from document chunks using semantic search"""
    try:
        if not openai_client:
            return ""
        
        # Get query embedding
        query_embedding = get_embedding(query)
        if not query_embedding:
            return ""
        
        # Find similar chunks
        similar_chunks = find_similar_chunks(query_embedding, limit=3)
        
        if similar_chunks:
            return "\n".join([chunk["content"] for chunk in similar_chunks])
        return ""
        
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

def get_embedding(text: str) -> Optional[List[float]]:
    """Get embedding for text using OpenAI"""
    try:
        if not openai_client:
            return None
        
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def find_similar_chunks(query_embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
    """Find similar document chunks using cosine similarity"""
    try:
        chunks = list(document_chunks_collection.find({}))
        similar_chunks = []
        
        for chunk in chunks:
            if "embedding" in chunk:
                similarity = cosine_similarity(query_embedding, chunk["embedding"])
                if similarity > SIMILARITY_THRESHOLD:
                    similar_chunks.append({
                        "id": str(chunk["_id"]),
                        "content": chunk["content"],
                        "similarity": similarity
                    })
        
        # Sort by similarity and return top results
        similar_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_chunks[:limit]
        
    except Exception as e:
        print(f"Error finding similar chunks: {e}")
        return []

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        if NUMPY_AVAILABLE:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0
            
            return dot_product / (norm1 * norm2)
        else:
            # Manual calculation without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0
            
            return dot_product / (norm1 * norm2)
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0

def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - CHUNK_OVERLAP
        
        if start >= len(text):
            break
    
    return chunks

async def process_document(file_content: bytes, filename: str, content_type: str) -> dict:
    """Process uploaded document and store chunks with embeddings"""
    try:
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            return {"error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"}
        
        # Validate filename
        if not filename or len(filename.strip()) == 0:
            filename = f"uploaded_file_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract text based on file type
        text_content = extract_text_from_file(file_content, content_type)
        if not text_content:
            return {"error": "Could not extract text from file. File may be empty or corrupted."}
        
        # Check if document already exists
        existing_doc = documents_collection.find_one({"filename": filename})
        if existing_doc:
            return {"error": f"Document with filename '{filename}' already exists"}
        
        # Create document record
        doc_id = documents_collection.insert_one({
            "filename": filename,
            "content_type": content_type,
            "size": len(file_content),
            "text_length": len(text_content),
            "processed": False,  # Will be set to True after processing
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }).inserted_id
        
        # Chunk the text
        chunks = chunk_text(text_content)
        
        # Validate chunk count
        if len(chunks) > MAX_CHUNKS_PER_DOCUMENT:
            return {"error": f"Document too large. Maximum {MAX_CHUNKS_PER_DOCUMENT} chunks allowed"}
        
        # Process each chunk
        chunk_count = 0
        failed_chunks = 0
        
        for i, chunk in enumerate(chunks):
            try:
                # Skip empty chunks
                if not chunk.strip():
                    continue
                
                # Get embedding for chunk
                embedding = get_embedding(chunk)
                if embedding:
                    # Store chunk with embedding
                    document_chunks_collection.insert_one({
                        "doc_id": str(doc_id),
                        "chunk_index": i,
                        "content": chunk,
                        "embedding": embedding,
                        "chunk_size": len(chunk),
                        "created_at": datetime.utcnow()
                    })
                    chunk_count += 1
                else:
                    failed_chunks += 1
                    print(f"Failed to get embedding for chunk {i}")
            except Exception as e:
                failed_chunks += 1
                print(f"Error processing chunk {i}: {e}")
        
        # Update document status
        documents_collection.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "processed": True,
                    "chunks_created": chunk_count,
                    "failed_chunks": failed_chunks,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "doc_id": str(doc_id),
            "chunks_created": chunk_count,
            "failed_chunks": failed_chunks,
            "total_chunks": len(chunks),
            "content_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "processing_time": "completed"
        }
        
    except Exception as e:
        return {"error": f"Failed to process document: {str(e)}"}

def extract_text_from_file(file_content: bytes, content_type: str) -> str:
    """Extract text from different file types"""
    try:
        if content_type == "application/pdf":
            return extract_text_from_pdf(file_content)
        elif content_type == "text/plain":
            return file_content.decode('utf-8')
        elif content_type == "text/csv":
            return extract_text_from_csv(file_content)
        elif content_type == "application/json":
            return extract_text_from_json(file_content)
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_csv(file_content: bytes) -> str:
    """Extract text from CSV file"""
    try:
        csv_text = file_content.decode('utf-8')
        reader = csv.reader(io.StringIO(csv_text))
        text = ""
        for row in reader:
            text += " ".join(row) + "\n"
        return text
    except Exception as e:
        print(f"Error extracting CSV text: {e}")
        return ""

def extract_text_from_json(file_content: bytes) -> str:
    """Extract text from JSON file"""
    try:
        json_data = json.loads(file_content.decode('utf-8'))
        return json.dumps(json_data, indent=2)
    except Exception as e:
        print(f"Error extracting JSON text: {e}")
        return ""
