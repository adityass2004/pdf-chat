# 📄 PDF Chat Bot Server

A full-stack PDF extraction and chat system built with Node.js and Python. Upload PDFs, extract text and images, and perform intelligent queries on your documents.

## 🌟 Features

- **PDF Upload & Extraction** - Extract text and images from PDF files
- **Session Management** - Unique session IDs for each uploaded document
- **Smart Queries** - Multiple query actions for flexible data retrieval
- **Image Storage** - Organized image extraction per page
- **Search Functionality** - Search within PDF content
- **RESTful API** - Clean and documented endpoints

## 🏗️ Project Structure
Comming soon ..... Stay tuned !!!
<!-- ```
D:.
├── pdf_chat_node/              # Node.js Server
│   ├── src/
│   │   ├── extract_pdf_text_and_images.js
│   │   └── temp_images/
│   ├── output/
│   │   └── sessions/           # Session data storage
│   │       └── [session-id]/
│   │           ├── data.json   # Extracted metadata
│   │           └── images/     # Extracted images by page
│   │               ├── page_1/
│   │               ├── page_2/
│   │               └── ...
│   ├── server.js               # Main server file
│   ├── package.json
│   └── .env
│
└── python/                     # Python Processing
    ├── src/
    │   └── __pycache__/
    ├── data/
    │   ├── extracted_images/
    │   └── logs/
    ├── embeddings/
    └── logs/
``` -->

<!-- ## 🚀 Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Installation

#### 1. Clone the repository
```bash
git clone <your-repo-url>
cd pdf_chat_node
```

#### 2. Install Node.js dependencies
```bash
npm install
```

Required packages:
- `express` - Web framework
- `express-fileupload` - File upload handling
- `pdf-parse` or similar PDF extraction library

#### 3. Setup Python environment (optional)
```bash
cd ../python
pip install -r requirements.txt
```

#### 4. Start the server
```bash
cd ../pdf_chat_node
npm start
```

Server will run on `http://localhost:5000`

## 📡 API Endpoints

### 1️⃣ POST `/extract`
Upload and extract PDF content

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `pdf` (file)

**Response:**
```json
{
  "session_id": "uuid",
  "name": "document_name",
  "pages": 9,
  "images": 15,
  "texts": 234,
  "tables": 0,
  "pages_data": {
    "page_1": {
      "texts": ["..."],
      "images": [...]
    }
  },
  "extracted_at": "2024-01-01T00:00:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/extract \
  -F "pdf=@document.pdf"
```

---

### 2️⃣ POST `/query`
Perform smart queries on extracted data

**Actions Available:**

#### `get_pages` - Get page range
```json
{
  "session_id": "uuid",
  "action": "get_pages",
  "from": 1,
  "to": 5
}
```

#### `page` - Get single page
```json
{
  "session_id": "uuid",
  "action": "page",
  "page": 3
}
```

#### `full_text` - Get all text
```json
{
  "session_id": "uuid",
  "action": "full_text"
}
```

#### `images` - Get all images
```json
{
  "session_id": "uuid",
  "action": "images"
}
```

#### `image_text` - Get image descriptions
```json
{
  "session_id": "uuid",
  "action": "image_text"
}
```

#### `search` - Search in PDF
```json
{
  "session_id": "uuid",
  "action": "search",
  "query": "search term"
}
```

#### `summary` - Get document summary
```json
{
  "session_id": "uuid",
  "action": "summary"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "action": "search",
    "query": "invoice"
  }'
```

---

### 3️⃣ GET `/session/:sessionId/image/:imageKey`
Retrieve extracted images

**Parameters:**
- `sessionId` - Session UUID
- `imageKey` - Format: `{pageNum}_{imageIndex}`

**Example:**
```bash
curl http://localhost:5000/session/uuid/image/1_0 \
  --output image.png
```

---

### 4️⃣ DELETE `/session/:sessionId`
Delete session and all associated files

**Example:**
```bash
curl -X DELETE http://localhost:5000/session/your-session-id
```

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully",
  "session_id": "uuid"
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:
```env
PORT=5000
OUTPUT_DIR=./output/sessions
MAX_FILE_SIZE=50mb
```

## 📝 Usage Example

### Complete Workflow
```javascript
// 1. Upload PDF
const formData = new FormData();
formData.append('pdf', pdfFile);

const extractResponse = await fetch('http://localhost:5000/extract', {
  method: 'POST',
  body: formData
});

const { session_id } = await extractResponse.json();

// 2. Search content
const searchResponse = await fetch('http://localhost:5000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    action: 'search',
    query: 'invoice'
  })
});

const searchResults = await searchResponse.json();

// 3. Get full text
const textResponse = await fetch('http://localhost:5000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    action: 'full_text'
  })
});

const { text } = await textResponse.json();

// 4. Cleanup
await fetch(`http://localhost:5000/session/${session_id}`, {
  method: 'DELETE'
});
``` 
## 🐍 Python Integration (Coming Soon)

The Python module will handle:
- Advanced text processing
- Embeddings generation
- AI-powered chat functionality
- Vector database integration

## 🛠️ Development

### Running in Development Mode
```bash
npm run dev
```

### Testing
```bash
npm test
```

## 📊 Response Examples

### Extraction Response
```json
{
  "session_id": "2875d3ed-b3ed-4c43-be8b-a2289df01689",
  "name": "sample_document",
  "pages": 9,
  "images": 15,
  "texts": 234,
  "tables": 0,
  "pages_data": {
    "page_1": {
      "texts": [
        "Introduction to PDF Processing",
        "This document covers..."
      ],
      "images": [
        {
          "filename": "image_0.png",
          "url": "/session/2875d3ed.../image/1_0",
          "description": "Diagram showing workflow"
        }
      ]
    }
  },
  "extracted_at": "2024-12-03T10:30:00.000Z"
}
```

### Search Response
```json
{
  "session_id": "2875d3ed-b3ed-4c43-be8b-a2289df01689",
  "action": "search",
  "query": "invoice",
  "total_results": 3,
  "results": [
    {
      "page": 2,
      "text_index": 5,
      "text": "Invoice #12345 dated March 15, 2024"
    },
    {
      "page": 4,
      "text_index": 12,
      "text": "Total invoice amount: $1,250.00"
    }
  ]
}
``` -->
<!-- 
## 🔒 Security Considerations

- File upload size limits enforced
- Only PDF files accepted
- Session-based isolation
- Automatic cleanup capabilities
- Input validation on all endpoints

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Express.js community
- PDF parsing libraries
- Contributors and testers

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [Link to docs]

## 🗺️ Roadmap

- [ ] Add table extraction
- [ ] Implement vector embeddings
- [ ] Add chat functionality
- [ ] Support for multiple file formats
- [ ] Real-time collaboration
- [ ] Advanced search with AI
- [ ] Export functionality

--- -->

### Creating with using Node.js and Python