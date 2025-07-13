from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.database.database import documents_collection, document_chunks_collection
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = list(documents_collection.find({}, {"_id": 0, "embedding": 0}))
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document details"""
    try:
        document = documents_collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunk count for this document
        chunk_count = document_chunks_collection.count_documents({"doc_id": doc_id})
        
        document["_id"] = str(document["_id"])
        document["chunk_count"] = chunk_count
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document and all its chunks"""
    try:
        # Check if document exists
        document = documents_collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete all chunks for this document
        chunks_deleted = document_chunks_collection.delete_many({"doc_id": doc_id})
        
        # Delete the document
        documents_collection.delete_one({"_id": ObjectId(doc_id)})
        
        return {
            "message": "Document deleted successfully",
            "chunks_deleted": chunks_deleted.deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(doc_id: str, limit: Optional[int] = 10, offset: Optional[int] = 0):
    """Get chunks for a specific document"""
    try:
        # Check if document exists
        document = documents_collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Set default values
        limit_val = limit if limit is not None else 10
        offset_val = offset if offset is not None else 0
        
        # Get chunks
        chunks = list(document_chunks_collection.find(
            {"doc_id": doc_id},
            {"embedding": 0}  # Exclude embeddings to reduce response size
        ).skip(offset_val).limit(limit_val).sort("chunk_index", 1))
        
        # Convert ObjectIds to strings
        for chunk in chunks:
            chunk["_id"] = str(chunk["_id"])
        
        return {
            "doc_id": doc_id,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "offset": offset,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")

@router.get("/search")
async def search_documents(query: str, limit: Optional[int] = 5):
    """Search documents using semantic search"""
    try:
        from app.services.rag import retrieve_context, get_embedding, find_similar_chunks
        
        # Get query embedding
        query_embedding = get_embedding(query)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Set default limit
        limit_val = limit if limit is not None else 5
        
        # Find similar chunks
        similar_chunks = find_similar_chunks(query_embedding, limit=limit_val)
        
        # Get document details for each chunk
        results = []
        for chunk in similar_chunks:
            doc_chunk = document_chunks_collection.find_one({"_id": ObjectId(chunk["_id"])})
            if doc_chunk:
                doc = documents_collection.find_one({"_id": ObjectId(doc_chunk["doc_id"])})
                if doc:
                    results.append({
                        "document": {
                            "doc_id": str(doc["_id"]),
                            "filename": doc["filename"],
                            "content_type": doc["content_type"]
                        },
                        "chunk": {
                            "content": chunk["content"],
                            "similarity": chunk["similarity"],
                            "chunk_index": doc_chunk.get("chunk_index", 0)
                        }
                    })
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        total_documents = documents_collection.count_documents({})
        total_chunks = document_chunks_collection.count_documents({})
        processed_documents = documents_collection.count_documents({"processed": True})
        
        # Get document types distribution
        pipeline = [
            {"$group": {"_id": "$content_type", "count": {"$sum": 1}}}
        ]
        type_distribution = list(documents_collection.aggregate(pipeline))
        
        return {
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "total_chunks": total_chunks,
            "document_types": type_distribution,
            "system_status": "operational" if total_documents > 0 else "no_documents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") 