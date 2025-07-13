# Multi-Agentic Conversational AI

A Python-based RESTful API application that enables natural language conversation with Large Language Models (LLMs), integrated with Retrieval Augmented Generation (RAG) and a custom-built CRM system.

## 🚀 Features

### 1. Conversational Chatbot with RAG
- **Natural Language Processing**: Accept user messages through API endpoints
- **OpenAI Integration**: Uses GPT-3.5-turbo for intelligent responses
- **RAG System**: Dynamically retrieves relevant documents from knowledge base
- **Conversation Memory**: Maintains full history of prior conversations
- **Contextual Awareness**: Seamlessly blends RAG results with LLM prompts

### 2. CRM User Data Capture
- **User Management**: Create, update, and delete user profiles
- **Data Storage**: MongoDB database for scalable, flexible storage
- **Conversation Tracking**: Full conversation history linked to each user
- **Personalization**: User preferences and company information for tailored responses

### 3. Document Processing & RAG
- **Multi-format Support**: PDF, TXT, CSV, JSON file processing
- **Intelligent Chunking**: Text segmentation with overlap for better context
- **Vector Embeddings**: OpenAI embeddings for semantic search
- **Similarity Search**: Cosine similarity for relevant document retrieval

### 4. Advanced Features
- **Session Management**: Unique session IDs for conversation tracking
- **Dynamic Tagging**: Automatic conversation categorization
- **Memory Reset**: Selective or complete conversation memory clearing
- **Health Monitoring**: API health check endpoints

## 🏗️ Architecture

```
project/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database/
│   │   └── database.py      # MongoDB database management
│   ├── models/
│   │   └── schemas.py       # Pydantic data models
│   ├── routes/
│   │   ├── chat.py         # Chat endpoints
│   │   ├── crm.py          # CRM endpoints
│   │   ├── upload.py       # Document upload endpoints
│   │   └── calendar.py     # Calendar endpoints
│   └── services/
│       ├── chatbot.py      # Chat processing logic
│       ├── crm_logic.py    # CRM business logic
│       ├── rag.py          # RAG system implementation
│       └── calendar_service.py # Calendar operations
├── requirements.txt         # Python dependencies
└── README.md              # Project documentation
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key
- MongoDB (local installation or cloud service)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB=conversational_ai
   ```

5. **Test MongoDB Connection (Optional)**
   ```bash
   python test_mongodb.py
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Chat Endpoints

**POST** `/chat/`
- **Description**: Send a message and receive AI response
- **Request Body**:
  ```json
  {
    "user_id": "string",
    "message": "string",
    "session_id": "string (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "response": "string",
    "tags": ["string"],
    "session_id": "string",
    "conversation_id": "string",
    "response_time_ms": 1234,
    "context_used": true
  }
  ```

#### Document Upload

**POST** `/upload_docs/`
- **Description**: Upload documents for RAG processing
- **Supported Formats**: PDF, TXT, CSV, JSON
- **Request**: Multipart form data with file
- **Response**:
  ```json
  {
    "status": "success",
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "size": 12345,
    "result": {
      "doc_id": "uuid",
      "chunks_created": 5,
      "failed_chunks": 0,
      "total_chunks": 5,
      "content_preview": "..."
    }
  }
  ```

#### RAG Management

**GET** `/rag/documents`
- **Description**: List all uploaded documents

**GET** `/rag/documents/{doc_id}`
- **Description**: Get document details and chunk count

**DELETE** `/rag/documents/{doc_id}`
- **Description**: Delete document and all its chunks

**GET** `/rag/documents/{doc_id}/chunks`
- **Description**: Get chunks for a specific document
- **Parameters**: `limit` (optional), `offset` (optional)

**GET** `/rag/search?query={search_term}&limit={limit}`
- **Description**: Search documents using semantic search
- **Parameters**: `query` (required), `limit` (optional, default: 5)

**GET** `/rag/stats`
- **Description**: Get RAG system statistics

#### CRM Endpoints

**POST** `/crm/create_user`
- **Description**: Create a new user
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Tech Corp",
    "phone": "+1234567890",
    "role": "Developer",
    "preferences": ["technical", "coding"]
  }
  ```

**PUT** `/crm/update_user`
- **Description**: Update existing user
- **Request Body**: Same as create_user + `user_id`

**GET** `/crm/conversations/{user_id}`
- **Description**: Get conversation history for user

**GET** `/crm/user/{user_id}`
- **Description**: Get user information

**DELETE** `/crm/user/{user_id}`
- **Description**: Delete user and all associated data

#### Memory Management

**POST** `/reset`
- **Description**: Reset conversation memory
- **Request Body**:
  ```json
  {
    "user_id": "string (optional)",
    "session_id": "string (optional)"
  }
  ```

#### Utility Endpoints

**GET** `/`
- **Description**: API information and available endpoints

**GET** `/health`
- **Description**: Health check endpoint

## 🔧 Configuration

### Database
- **Type**: MongoDB
- **Collections**:
  - `users`: User profiles and preferences
  - `conversations`: Conversation history and metadata
  - `documents`: Document metadata for RAG
  - `document_chunks`: Text chunks with embeddings
  - `calendar_events`: Calendar integration

### RAG Configuration
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Embedding Model**: text-embedding-ada-002
- **Similarity Threshold**: 0.1

## 🎯 Usage Examples

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/crm/create_user" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@techcorp.com",
    "company": "TechCorp",
    "preferences": ["technical", "product"]
  }'
```

### 2. Start a Conversation
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_uuid_here",
    "message": "What are the latest features in your product?"
  }'
```

### 3. Upload a Document
```bash
curl -X POST "http://localhost:8000/upload_docs/" \
  -F "file=@product_manual.pdf"
```

### 4. Search Documents
```bash
curl -X GET "http://localhost:8000/rag/search?query=product%20features&limit=3"
```

### 5. List All Documents
```bash
curl -X GET "http://localhost:8000/rag/documents"
```

### 6. Get RAG Statistics
```bash
curl -X GET "http://localhost:8000/rag/stats"
```

### 7. Get Conversation History
```bash
curl -X GET "http://localhost:8000/crm/conversations/user_uuid_here"
```

## 🔮 Future Enhancements

### Calendar Integration
The system is designed to support calendar integration:

1. **Event Creation**: Users can create calendar events through conversation
2. **Meeting Scheduling**: AI can suggest and schedule meetings
3. **Reminder System**: Automated reminders based on conversation context
4. **Integration APIs**: Connect with Google Calendar, Outlook, etc.

### Implementation Approach
```python
# Calendar event creation through conversation
if "schedule" in user_message.lower():
    # Extract date, time, and details
    # Create calendar event
    # Send confirmation
```

### Advanced Features
- **Multi-language Support**: Internationalization for global users
- **Voice Integration**: Speech-to-text and text-to-speech
- **Analytics Dashboard**: Conversation insights and metrics
- **Webhook Support**: Real-time notifications
- **Rate Limiting**: API usage management
- **Authentication**: JWT-based user authentication

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Verify API key in `.env` file
   - Check API quota and billing

2. **Database Errors**
   - Ensure MongoDB is running and accessible
   - Check MongoDB connection string in .env file

3. **File Upload Issues**
   - Verify file format is supported
   - Check file size limits

4. **Import Errors**
   - Ensure all dependencies are installed
   - Activate virtual environment

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` when running the server
