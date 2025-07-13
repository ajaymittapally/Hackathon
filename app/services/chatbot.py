import time
import uuid
from typing import List, Dict, Any, Optional
from app.services.rag import retrieve_context
from app.services.crm_logic import save_conversation, get_conversation_history_for_context, get_user
from openai import OpenAI
import os
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessageParam
from app.utils.tagging import extract_tags_from_response


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client only if API key is available
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}")
        client = None

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())



def get_chat_response(user_id: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Enhanced chat response with CRM integration and conversation memory"""
    start_time = time.time()
    
    # Generate session ID if not provided
    if not session_id:
        session_id = generate_session_id()
    
    # Get user information for personalization
    user_info = get_user(user_id)
    user_context = ""
    if user_info:
        user_context = f"User: {user_info['name']} from {user_info['company'] or 'Unknown Company'}. "
        if user_info['preferences']:
            user_context += f"Preferences: {', '.join(user_info['preferences'])}. "
    
    # Step 1: Get RAG-relevant context
    rag_context = retrieve_context(message)
    
    # Step 2: Get conversation history for context
    conversation_history = get_conversation_history_for_context(user_id)
    
    # Step 3: Create comprehensive prompt
    system_prompt = f"""You are a helpful AI assistant with access to a knowledge base and conversation history. 
{user_context}

Your responses should be:
- Helpful and accurate
- Based on the provided context when available
- Aware of the user's conversation history
- Professional and friendly

If you find relevant information in the knowledge base, use it to provide more accurate answers.
If the user asks about something not in the knowledge base, provide a general helpful response."""

    # Build the conversation context
    context_parts = []
    
    if rag_context:
        context_parts.append(f"Relevant Knowledge Base Information:\n{rag_context}")
    
    if conversation_history:
        context_parts.append(f"Recent Conversation History:\n{conversation_history}")
    
    context_text = "\n\n".join(context_parts) if context_parts else ""
    
    # Create messages for OpenAI
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt}
    ]
    
    if context_text:
        messages.append({"role": "user", "content": f"Context:\n{context_text}\n\nCurrent question: {message}"})
    else:
        messages.append({"role": "user", "content": message})
    
    # Step 4: Call LLM (OpenAI)
    try:
        if client is None:
            raise RuntimeError("OpenAI client is not initialized. Check your API key.")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    # Step 5: Extract tags from response
    safe_answer = answer or ""
    tags = extract_tags_from_response(safe_answer)
    
    # Step 6: Store conversation in CRM
    conversation_id = save_conversation(user_id, session_id, message, safe_answer, tags)
    
    # Step 7: Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Step 8: Return enhanced response
    return {
        "response": safe_answer,
        "tags": tags,
        "session_id": session_id,
        "conversation_id": conversation_id,
        "response_time_ms": response_time_ms,
        "context_used": [rag_context] if rag_context else [],
        "user_info": {
            "name": user_info.get('name') if user_info else None,
            "company": user_info.get('company') if user_info else None
        }
    }
