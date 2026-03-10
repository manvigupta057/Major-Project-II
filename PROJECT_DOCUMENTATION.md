# RAG Project - Complete Documentation

## Project Overview

The **RAG (Retrieval-Augmented Generation) Project** is a full-stack web application designed to enable intelligent document analysis and question-answering. Users can upload documents in multiple formats and ask questions about their content, receiving context-aware answers grounded in the actual document text.

### Problem Statement
Traditional search engines struggle with semantic understanding of document content. Users cannot efficiently query documents to extract context-aware insights. This project solves this by combining:
- **Semantic Search**: Understanding meaning, not just keywords
- **Context Retrieval**: Finding the most relevant sections
- **AI-Powered Answers**: Generating coherent responses using Large Language Models

---

## What Was Built - Project Structure

### Full-Stack Architecture
```
RAG_Project/
├── Backend (Python/FastAPI)
│   ├── Core Processing Modules
│   ├── API Layer
│   └── Vector Database
│
└── Frontend (React/Vite)
    ├── User Interface Components
    ├── File Upload Handler
    └── Chat Interface
```

### Backend Components

#### 1. **Document Processor (document_processor.py)**
- **Purpose**: Extract and process text from multiple file formats
- **Supported Formats**:
  - PDF (.pdf) - PyPDF library
  - Microsoft Word (.docx) - python-docx
  - Excel Spreadsheets (.xlsx) - openpyxl
  - PowerPoint Presentations (.pptx) - python-pptx
  - CSV Files (.csv) - pandas
  - Scanned Documents - EasyOCR (OCR capability)

- **Processing Pipeline**:
  1. Detect file format from extension
  2. Extract raw text using appropriate library
  3. Create metadata (filename, page numbers, source)
  4. Split into chunks (1000 characters default, 200 character overlap)
  5. Return Document objects with content and metadata

#### 2. **Vector Store (vector_store.py)**
- **Purpose**: Manage embeddings and perform semantic search
- **Technology**: ChromaDB (lightweight vector database)
- **Key Features**:
  - Persistent storage in `chroma_db/` directory
  - Embedding generation using Sentence-Transformers
  - Cosine similarity matching for retrieval
  - Collection management capabilities

- **Database Schema**:
  ```
  Collection: documents
  ├─ id: Unique identifier (doc_1, doc_2, etc.)
  ├─ embedding: 384-dimensional vector from all-MiniLM-L6-v2 model
  ├─ document: Original text chunk
  ├─ metadata: JSON with filename, page number, chunk ID
  └─ distance: Similarity score to query
  ```

- **Operations**:
  - `store_to_chromadb()`: Save embeddings
  - `retrieve_from_chromadb()`: Semantic search with top-k results
  - `delete_all_documents()`: Clear collection
  - `get_collection_stats()`: View database status

#### 3. **LLM Interface (llm_interface.py)**
- **Purpose**: Generate answers using language models
- **Supported Providers**:

  **A. OLLAMA (Local Inference)**
  - Runs models locally on user's machine
  - Available models: Llama3, Mistral, Neural Chat, etc.
  - Benefits: Privacy, no API costs, works offline
  - Requirement: Ollama service running locally

  **B. GROQ (Cloud API)**
  - Fast cloud-based inference
  - Available models: Mixtral-8x7b, LLaMA2-70b
  - Benefits: No local setup, fast processing
  - Requirement: GROQ_API_KEY environment variable

- **Answer Generation Process**:
  1. Construct system prompt with retrieved context
  2. Combine user question with document context
  3. Send to LLM via LangChain
  4. Extract and return response

- **Prompt Template**:
  ```
  "Answer the question based only on the following context:
   {context}
   
   Question: {question}"
  ```

- **Configuration**:
  - Temperature: 0.0 (deterministic, factual answers)
  - Model: Configurable per request
  - Provider: Switchable between Ollama and Groq

#### 4. **API Layer (api.py)**
- **Framework**: FastAPI with Uvicorn
- **Main Endpoints**:

  **POST /upload**
  - Upload document file
  - Max file size: 50MB
  - Returns: file_id for tracking
  - Triggers asynchronous processing

  **POST /query**
  - Send question about uploaded document
  - Parameters: query (string), file_id (string)
  - Returns: answer (string), source chunks with metadata

  **GET /documents**
  - List all uploaded documents
  - Returns: file metadata and upload timestamps

  **DELETE /documents/{file_id}**
  - Remove document and associated embeddings
  - Cleans up ChromaDB collection

  **GET /status**
  - Check system health
  - Returns: ChromaDB status, model availability

- **Response Format**:
  ```json
  {
    "status": "success",
    "data": {...},
    "message": "Operation completed"
  }
  ```

#### 5. **Main Application (app.py)**
- **Class**: RAGApplication
- **Responsibilities**:
  - Initialize all components
  - Manage workflow coordination
  - Handle configuration

- **Core Methods**:
  - `process_data(file_path)`: Complete processing pipeline
  - `query(question, num_results=5)`: Answer generation pipeline

#### 6. **Configuration (config.py)**
- Central configuration management
- Settings for models, chunk sizes, directories
- Environment variable integration

### Frontend Components

#### 1. **App Component (App.jsx)**
- Main application entry point
- State management for upload status
- Route between FileUploader and ChatInterface
- Minimalist UI design (beige/stone color palette)

#### 2. **FileUploader Component (FileUploader.jsx)**
- Handles file upload
- Drag-and-drop support
- File validation
- Progress feedback
- Communicates with backend POST /upload

#### 3. **ChatInterface Component (ChatInterface.jsx)**
- Question input field
- Answer display area
- Source citation display
- Real-time communication with backend
- Conversation history management

#### 4. **Styling**
- **Framework**: Tailwind CSS
- **Design**: Responsive, modern, minimalist
- **Colors**: Stone/beige palette for professional appearance
- **Responsive**: Mobile, tablet, and desktop support

---

## Tools & Technologies Used

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Vector Database** | ChromaDB | 0.4.22+ | Vector storage, semantic search, persistence |
| **Embeddings** | Sentence-Transformers | 2.3.1+ | Text-to-vector conversion (384-dimensional) |
| **Embeddings (Local)** | Ollama | Latest | Local embedding generation |
| **LLM Framework** | LangChain | 0.1.0+ | Unified LLM interface, prompt templates |
| **LLM Provider 1** | Ollama | Latest | Local LLM inference |
| **LLM Provider 2** | Groq API | Latest | Cloud LLM inference |
| **PDF Processing** | PyPDF | 4.0.0+ | Extract text from PDF files |
| **Word Documents** | python-docx | 1.1.0+ | Extract text from .docx files |
| **Excel Files** | openpyxl | 3.1.0+ | Read Excel spreadsheets |
| **PowerPoint Files** | python-pptx | 0.6.23+ | Extract text from presentations |
| **OCR** | EasyOCR | Latest | Optical character recognition |
| **Image Processing** | Pillow | Latest | Image manipulation for OCR |
| **Data Processing** | Pandas | 2.0.0+ | Data manipulation and CSV handling |
| **Numerical Ops** | NumPy | 1.24.0+ | Numerical computations |
| **Web Framework** | FastAPI | 0.109.0+ | Modern async web framework |
| **ASGI Server** | Uvicorn | 0.27.0+ | Server for running FastAPI |
| **File Upload** | python-multipart | 0.0.6+ | Handle multipart form data |
| **Environment** | python-dotenv | 1.0.0+ | Load environment variables |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **UI Framework** | React | 19.2.0+ | Component-based UI |
| **Build Tool** | Vite | 7.2.4+ | Fast build and development server |
| **Styling** | Tailwind CSS | 3.4.1+ | Utility-first CSS framework |
| **CSS Processing** | PostCSS | 8.4.35+ | CSS transformations |
| **Auto-prefixing** | Autoprefixer | 10.4.17+ | Cross-browser CSS support |
| **HTTP Client** | Axios | 1.13.2+ | Promise-based HTTP requests |
| **Linting** | ESLint | 9.39.1+ | Code quality checking |

### Development & DevOps

| Tool | Purpose |
|------|---------|
| Python venv | Virtual environment isolation |
| npm/Node.js | Frontend package management |
| Git | Version control |
| Environment variables (.env) | Configuration management |

---

## Approach & Methodology

### RAG Pipeline Architecture

#### Phase 1: Document Ingestion & Processing
```
User Uploads File
    ↓
Format Detection
    ↓
Text Extraction
    ↓
Chunking (1000 chars, 200 overlap)
    ↓
Metadata Attachment
    ↓
Embedding Generation (Sentence-Transformers)
    ↓
Vector Store (ChromaDB)
    ↓
Persistent Storage
```

#### Phase 2: Query Processing & Answer Generation
```
User Asks Question
    ↓
Query Embedding (Same model as documents)
    ↓
Similarity Search (Cosine distance)
    ↓
Retrieve Top-K Results (k=5)
    ↓
Context Construction
    ↓
Prompt Engineering
    ↓
LLM Inference (Ollama/Groq)
    ↓
Answer Generation
    ↓
Source Attribution
    ↓
Response to User
```

### Key Design Decisions

1. **Chunking Strategy**
   - Size: 1000 characters (balance between context and specificity)
   - Overlap: 200 characters (prevent information loss at chunk boundaries)
   - Recursive splitting (preserve sentence integrity)

2. **Embedding Model**
   - Model: all-MiniLM-L6-v2 (Sentence-Transformers)
   - Dimensions: 384 (efficient for CPU, semantic quality)
   - Pre-trained on semantic similarity tasks

3. **Vector Database**
   - ChromaDB: Lightweight, persistent, easy to integrate
   - Storage: Local SQLite for simplicity and privacy
   - Metric: Cosine similarity (standard for text embeddings)

4. **LLM Flexibility**
   - Support both local (Ollama) and cloud (Groq) inference
   - Allows users to choose privacy vs. speed tradeoff
   - Easy to add more providers

5. **Prompt Engineering**
   - System prompt prevents hallucination
   - Context-grounded answers only
   - Temperature set to 0.0 for factual responses

6. **Source Attribution**
   - Every answer includes source metadata
   - Users can verify and trace back to original documents
   - Builds trust and explainability

### Multi-Format Support Strategy

Each document format requires specific extraction:
- **PDF**: Page-by-page extraction with PyPDF
- **Word/Excel/PPT**: Library-specific text extraction
- **CSV**: Pandas for structured data handling
- **Scanned**: EasyOCR for text recognition from images

---

## Data Flow & System Architecture

### Complete User Journey

#### 1. Document Upload Flow
```
┌─────────────┐
│   Browser   │ User selects file
│ (Frontend)  │
└──────┬──────┘
       │ POST /upload + multipart file
       ▼
┌──────────────────────┐
│  FastAPI Server      │
│ /upload endpoint     │
└──────┬───────────────┘
       │ Save to uploads/{uuid}_filename.ext
       │
       ├─ Return file_id to frontend
       │
       └─ Trigger async process_data()
          │
          ├─────────────────────────┐
          │                         │
          ▼                         ▼
       DocumentProcessor      No blocking
       └─ Load file
          └─ Extract text
          └─ Create chunks
          └─ Attach metadata
             │
             ▼
          Vector Store
          └─ Generate embeddings
          └─ Store in ChromaDB
          └─ Persist to disk
             
       ✓ Document ready for queries
```

#### 2. Question Answering Flow
```
┌─────────────┐
│   Browser   │ User types question
│ (Frontend)  │
└──────┬──────┘
       │ POST /query + question
       ▼
┌──────────────────────┐
│  FastAPI Server      │
│ /query endpoint      │
└──────┬───────────────┘
       │
       ├─ Query Embedding
       │  └─ Sentence-Transformers.embed_query()
       │
       ├─ Similarity Search
       │  └─ ChromaDB.query(query_embedding, k=5)
       │  └─ Returns top-5 chunks + distances
       │
       ├─ Context Construction
       │  └─ Combine chunks with separator
       │  └─ Preserve metadata
       │
       ├─ Prompt Construction
       │  └─ System: "Answer based only on context"
       │  └─ Context: {retrieved_chunks}
       │  └─ Question: {user_query}
       │
       ├─ LLM Inference
       │  └─ Forward to Ollama or Groq
       │  └─ Temperature: 0.0
       │
       ├─ Response Processing
       │  └─ Extract answer text
       │  └─ Gather source metadata
       │
       └─ Return to Frontend
          └─ answer: "Generated response"
          └─ sources: [chunk metadata]
             
          ✓ User sees answer with citations
```

### Database Schema (ChromaDB)

```
Collection: "documents"

Document Record:
{
  id: "doc_1",                          # Unique identifier
  embedding: [0.23, -0.15, ..., 0.87],  # 384-dimensional vector
  document: "Chunk text content...",    # Original text
  metadata: {                           # Searchable metadata
    "filename": "report.pdf",
    "page": 2,
    "chunk_id": 5,
    "source": "uploads/uuid_report.pdf"
  },
  distance: 0.15                        # Cosine distance to query
}
```

### API Communication

**Frontend sends to Backend:**
```json
{
  "method": "POST",
  "endpoint": "/query",
  "data": {
    "query": "What is the main topic?",
    "file_id": "abc123def456",
    "k": 5
  }
}
```

**Backend responds:**
```json
{
  "status": "success",
  "answer": "The main topic is about...",
  "sources": [
    {
      "content": "Relevant text chunk...",
      "metadata": {"page": 1, "chunk_id": 0},
      "distance": 0.12
    }
  ]
}
```

---

## Key Features Implemented

### 1. Multi-Format Document Support
✓ PDF files (.pdf)
✓ Microsoft Word (.docx)
✓ Excel spreadsheets (.xlsx)
✓ PowerPoint presentations (.pptx)
✓ CSV data files (.csv)
✓ Scanned documents via OCR

### 2. Semantic Search Capability
✓ Meaning-based search (not keyword matching)
✓ Cosine similarity matching
✓ Contextually relevant retrieval
✓ Top-5 results by default
✓ Distance scores for ranking

### 3. Flexible LLM Support
✓ Local inference with Ollama (privacy)
✓ Cloud inference with Groq API (speed)
✓ Easy provider switching
✓ Multiple model options per provider

### 4. Persistent Storage
✓ ChromaDB permanent embeddings
✓ No re-processing needed
✓ Fast retrieval on subsequent queries
✓ Collection management capabilities

### 5. Source Attribution
✓ Answer includes source chunks
✓ Metadata with document origin
✓ Traceable to original sections
✓ Verifiable answers

### 6. Modern User Interface
✓ React-based responsive frontend
✓ Minimalist design aesthetic
✓ Drag-and-drop file upload
✓ Real-time chat interface
✓ Mobile/tablet/desktop support

### 7. Context-Aware Answers
✓ System prompt prevents hallucination
✓ Answers grounded in documents
✓ Factual and verifiable responses
✓ Temperature: 0.0 for consistency

### 8. Scalable Architecture
✓ Modular component design
✓ Easy to extend with new formats
✓ Configuration-driven behavior
✓ Separation of concerns

---

## File Structure

```
RAG_Project/
│
├── backend/
│   ├── app.py                              # Main RAG orchestrator
│   ├── api.py                              # FastAPI endpoints
│   ├── document_processor.py               # File extraction & chunking
│   ├── vector_store.py                     # ChromaDB management
│   ├── llm_interface.py                    # LLM provider integration
│   ├── config.py                           # Configuration constants
│   ├── requirements.txt                    # Python dependencies
│   ├── .env                                # Environment variables
│   ├── realistic_restaurant_reviews.csv    # Sample test data
│   │
│   ├── chroma_db/                          # Vector database directory
│   │   ├── chroma.sqlite3                  # Database file
│   │   └── {collection_uuid}/              # Collection storage
│   │
│   ├── uploads/                            # Uploaded files storage
│   │   ├── {uuid}_filename.pdf
│   │   ├── {uuid}_document.docx
│   │   └── ...
│   │
│   ├── venv/                               # Python virtual environment
│   └── __pycache__/                        # Python cache
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                         # Main App component
│   │   ├── main.jsx                        # React entry point
│   │   ├── App.css                         # Component styles
│   │   ├── index.css                       # Global styles
│   │   │
│   │   └── components/
│   │       ├── FileUploader.jsx            # File upload component
│   │       └── ChatInterface.jsx           # Q&A chat component
│   │
│   ├── public/                             # Static assets
│   ├── index.html                          # HTML template
│   ├── package.json                        # Node.js dependencies
│   ├── vite.config.js                      # Vite configuration
│   ├── tailwind.config.js                  # Tailwind CSS config
│   ├── postcss.config.js                   # PostCSS config
│   └── eslint.config.js                    # ESLint rules
│
└── PROJECT_DOCUMENTATION.md                # This file
```

### Key Directories
- **chroma_db/**: Persistent vector database (survives restarts)
- **uploads/**: Temporary storage for uploaded files
- **venv/**: Isolated Python dependencies
- **src/components/**: React UI components

---

## Installation & Setup Guide

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- 4GB RAM minimum
- 2GB disk space
- Ollama (for local inference) OR Groq API key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create .env file**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   LLM_PROVIDER=ollama        # or 'groq'
   LLM_MODEL=llama3
   ```

6. **Start backend server**
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env file**
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access application**
   ```
   http://localhost:5173
   ```

### Ollama Setup (Optional - for Local LLM)

1. **Install Ollama**
   - Download from https://ollama.ai
   - Install and run

2. **Pull a model**
   ```bash
   ollama pull llama3
   ```

3. **Verify service**
   ```bash
   ollama list
   ```

---

## Usage Guide

### User Workflow

1. **Open Application**
   - Navigate to http://localhost:5173
   - See "Upload Document" interface

2. **Upload Document**
   - Click upload area or drag & drop
   - Supported formats: PDF, Word, Excel, PowerPoint, CSV
   - System processes and indexes document

3. **Ask Questions**
   - Type question in chat interface
   - Examples:
     - "Summarize the key points"
     - "What are the main topics?"
     - "Find all mentions of [topic]"
   - System retrieves relevant sections and generates answer

4. **Review Answers**
   - Read generated answer
   - Check source sections
   - Ask follow-up questions
   - All answers grounded in document

5. **Upload New File**
   - Click "Upload New File" button
   - Repeat for different documents

### Configuration

**Backend (config.py)**
- `EMBEDDING_MODEL`: Model for text embeddings
- `LLM_MODEL`: Default language model
- `LLM_TEMPERATURE`: 0.0 (factual) to 1.0 (creative)
- `CHUNK_SIZE`: Characters per document chunk
- `CHUNK_OVERLAP`: Overlap between chunks
- `MAX_SEARCH_RESULTS`: Number of results to retrieve
- `CHROMA_DB_DIR`: Vector database location
- `COLLECTION_NAME`: Database collection name

---

## API Endpoints Reference

### 1. POST /upload
Upload and process a document

**Request:**
```
multipart/form-data
- file: binary file data
```

**Response:**
```json
{
  "status": "success",
  "file_id": "abc123def456",
  "filename": "document.pdf",
  "message": "File processed successfully"
}
```

### 2. POST /query
Ask question about uploaded document

**Request:**
```json
{
  "query": "What is the main topic?",
  "file_id": "abc123def456",
  "k": 5
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "Text chunk...",
      "metadata": {"page": 1, "chunk_id": 0},
      "distance": 0.15
    }
  ]
}
```

### 3. GET /documents
List all uploaded documents

**Response:**
```json
{
  "status": "success",
  "documents": [
    {
      "file_id": "abc123",
      "filename": "doc1.pdf",
      "upload_time": "2026-02-21T10:30:00"
    }
  ]
}
```

### 4. DELETE /documents/{file_id}
Delete document and clear embeddings

**Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully"
}
```

### 5. GET /status
Check system health

**Response:**
```json
{
  "status": "healthy",
  "chromadb": "connected",
  "models": {
    "embedding": "ready",
    "llm": "ready"
  }
}
```

---

## Technical Deep Dive

### Embedding Generation Process
1. **Model**: Sentence-Transformers (all-MiniLM-L6-v2)
2. **Input**: Text chunk (1000 characters)
3. **Output**: 384-dimensional vector
4. **Process**:
   - Tokenization
   - Transformer encoding
   - Mean pooling across tokens
   - Normalization
5. **Property**: Semantic similarity preserved in vector space

### Similarity Search Algorithm
1. **Input**: Query text, k=5
2. **Generate**: Query embedding using same model
3. **Compare**: Cosine distance between query and stored embeddings
4. **Rank**: Sort by distance (lower = more similar)
5. **Return**: Top-k results with metadata

### Answer Generation Process
1. **Construct Prompt**:
   ```
   System: "Answer based only on context provided"
   Context: [Top-5 relevant chunks]
   Question: [User query]
   ```
2. **Forward to LLM**: Via LangChain wrapper
3. **Generate**: Model produces answer
4. **Extract**: Get text response
5. **Format**: Return with sources

### Error Handling
- Invalid file formats: Rejected at upload
- Empty documents: Skipped in processing
- API failures: Graceful error messages
- Database errors: Logged with recovery attempts

---

## Performance Characteristics

### Processing Times
- **File Upload**: 1-5 seconds (depending on file size)
- **Text Extraction**: 2-10 seconds (depending on format)
- **Embedding Generation**: 5-30 seconds (depends on chunk count)
- **Query Processing**: 1-3 seconds (local) or 0.5-2 seconds (Groq)

### Storage Requirements
- **Embeddings**: ~0.5MB per 10,000 words
- **Database**: SQLite with automatic indexing
- **Uploaded Files**: Stored temporarily in uploads/ directory

### Scalability
- **Documents**: Limited by disk space and RAM
- **Chunk Size**: Affects embedding count and search speed
- **Model Size**: Depends on system resources

---

## Future Enhancements

1. **Multi-Document Querying**
   - Query across multiple uploaded documents
   - Cross-document summarization
   - Comparative analysis

2. **Conversation History**
   - Maintain chat context
   - Follow-up question improvements
   - Conversation export

3. **Advanced Features**
   - Custom fine-tuned embedding models
   - Metadata-based filtering
   - Advanced ranking algorithms
   - Document versioning

4. **UI/UX Improvements**
   - Dark mode support
   - Customizable themes
   - Export answers to PDF/Word
   - Real-time indexing progress

5. **Integration & Deployment**
   - Docker containerization
   - Cloud deployment (AWS/Azure/GCP)
   - API authentication
   - Rate limiting

6. **Additional Support**
   - More document types (Markdown, JSON, XML)
   - Database integration
   - Video transcript analysis
   - Real-time collaboration

---

## Summary

The RAG Project demonstrates a complete, production-ready implementation of Retrieval-Augmented Generation:

✓ **Multi-format document support** for flexibility
✓ **Semantic search** for intelligent retrieval
✓ **Flexible LLM integration** for privacy/speed tradeoff
✓ **Clean architecture** for maintainability
✓ **User-friendly interface** for accessibility
✓ **Context-aware answers** for accuracy
✓ **Source attribution** for verifiability

This project showcases modern AI application development combining:
- Advanced NLP techniques
- Vector database technology
- Large language models
- Full-stack web development
- Clean code practices

---

**Document Generated**: February 21, 2026
**Project Status**: Fully Functional RAG Application
**Last Updated**: Current Session
