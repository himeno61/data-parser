# Data Parser with Vector Database

A Flask application for file upload, processing, and vector-based document search using ChromaDB.

## Features

- **File Upload**: Upload text files for processing
- **Vector Database**: Automatic embedding and storage of file contents using ChromaDB
- **Semantic Search**: Search documents using natural language queries
- **Document Management**: List, retrieve, and delete documents
- **Background Processing**: Asynchronous file processing with logging
- **Docker Support**: Easy deployment with Docker Compose

## API Endpoints

### File Operations

- `POST /upload` - Upload a file for processing
- `GET /health` - Health check endpoint

### Vector Database Operations

- `POST /search` - Search documents with semantic similarity
- `GET /documents` - List all documents
- `GET /documents/<id>` - Get specific document by ID
- `DELETE /documents/<id>` - Delete a document
- `GET /db-info` - Get database information

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Build and run with Docker Compose:
   ```bash
   docker compose up web
   ```
3. Access the application at `http://localhost:8000`

### Manual Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```bash
   FLASK_ENV=development flask run --port=5000
   ```

## Usage Examples

### Upload a File

```bash
curl -X POST -F "file=@document.txt" http://localhost:8000/upload
```

### Search Documents

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "n_results": 5}'
```

### List Documents

```bash
curl http://localhost:8000/documents
```

### Get Database Info

```bash
curl http://localhost:8000/db-info
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test the vector database functionality:

```bash
python test_vector_example.py
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development` or `production`
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Vector Database

- ChromaDB data is persisted in `./chroma_db` directory
- Uses sentence-transformers for text embeddings
- Automatic collection creation and management

## Dependencies

- **Flask**: Web framework
- **ChromaDB**: Vector database for document embeddings
- **sentence-transformers**: Text embedding model
- **pytest**: Testing framework
- **gunicorn**: Production WSGI server

## Architecture

```
data-parser/
├── app.py              # Flask application
├── upload_worker.py    # Background file processing
├── vector_db.py        # Vector database operations
├── logger_config.py    # Logging configuration
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Docker configuration
├── Dockerfile         # Docker image definition
└── tests/             # Test suite
    ├── test_upload.py     # Upload functionality tests
    └── test_vector_db.py  # Vector database tests
```

## Logging

The application uses structured logging with:

- Console output for development
- File logging to `logs/app.log`
- Different log levels for different components

## Docker Volumes

- `chroma_data`: Persistent storage for vector database
- Code volume mounting for development mode
