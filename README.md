# 📄 PDF Chat Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**AI-Powered PDF Analysis with RAG, Vision Models & Smart Auto-Formatting**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [Tech Stack](#-tech-stack)

</div>

---

## 🌟 Features

### 🤖 **Dual AI Models**
- **Text Analysis**: LLaMA 3.2, Mistral, Phi3, Gemma support
- **Vision Analysis**: LLaVA-Phi3, Moondream for image understanding
- **Auto-Fallback**: Automatic model switching for VRAM management

### 📊 **Advanced RAG System**
- FAISS vector database for semantic search
- Sentence transformers for embeddings
- Context-aware responses with TOP-K retrieval
- Chunking with configurable overlap

### 🎨 **Beautiful Interface**
- Live streaming responses (ChatGPT-style)
- **Smart Auto-Formatting**: Automatically formats responses as lists or paragraphs based on content
- Syntax-highlighted code blocks
- Styled image grids with expandable details
- Gradient info boxes and professional formatting
- Dark theme code blocks with proper alignment

### 🖼️ **Image Processing**
- Automatic image extraction from PDFs
- Page-wise image indexing
- Vision AI analysis with LLaVA/Moondream
- Beautiful grid display with metadata

### ⚡ **Performance**
- Optimized for RTX 3050 4GB VRAM
- Efficient memory management
- Fast vector search with FAISS
- Model caching and reuse

---

## 📸 Demo

### 💻 Desktop Interface

<div align="center">

![Main Interface](https://github.com/adityass2004/pdf-chat/blob/main/Screenshorts/screenshort_1_pc.png?raw=true)
*Main chat interface with smart-formatted responses and document analysis*


### 📱 Mobile Interface
---

<div align="center">

<table>
<tr>
<td align="center">
<img src="https://github.com/adityass2004/pdf-chat/blob/main/Screenshorts/screenshort_1_ph.png?raw=true" width="200" alt="Mobile Chat View"><br>
<i>Responsive mobile chat interface</i>
</td>

<td align="center">
<img src="https://github.com/adityass2004/pdf-chat/blob/main/Screenshorts/screenshort_2_ph.png?raw=true" width="200" alt="Mobile Sidebar"><br>
<i>Mobile-friendly sidebar with model configuration</i>
</td>
</tr>
</table>

</div>

---


## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- 4GB+ RAM (8GB recommended)
- GPU with 4GB+ VRAM (optional but recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/adityass2004/pdf-chat-assistant.git
cd pdf-chat-assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download AI Models

```bash
# Download text model
ollama pull llama3.2

# Download vision model (choose one)
ollama pull llava-phi3      # Recommended for RTX 3050
ollama pull moondream       # Lighter alternative
```

### Step 4: Run Application

```bash
python main.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
pdf-chat-assistant/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── data/                  # PDF storage
│   ├── extracted_images/  # Extracted images from PDFs
│   └── logs/             # Application logs
│
├── embeddings/           # FAISS vector indices
│   └── index.faiss      # Stored embeddings
│
├── src/                  # Source code
│   ├── __init__.py
│   ├── app.py           # Streamlit interface with smart formatting
│   ├── chat_copy.py     # Chat logic & prompts
│   ├── chunker.py       # Text chunking
│   ├── config.py        # Configuration
│   ├── embedder.py      # Embedding generation
│   ├── image_handler.py # Image processing
│   ├── model_manager.py # Model management
│   ├── pdf_extractor.py # PDF text extraction
│   ├── query_parser.py  # Query parsing
│   ├── utils.py         # Utilities
│   └── vector_store.py  # FAISS operations
│
└── screenshots/          # Demo screenshots
    ├── desktop-main.png
    ├── desktop-features.png
    ├── mobile-chat.png
    └── mobile-sidebar.png
```

---

## 🎯 Usage

### Basic Workflow

1. **Upload PDF**: Click "Choose a PDF file" in the sidebar
2. **Process**: Click "🚀 Process PDF" to index the document
3. **Ask Questions**: Type your questions in the chat input
4. **Get Answers**: Receive AI-powered responses with smart auto-formatting

### Example Queries

#### 📝 Text Questions
```
What is the main topic of this document?
Summarize the key points from page 5
List all the conclusions mentioned
Explain the methodology used
Give me the steps to implement this
```

#### 🖼️ Image Queries
```
Show images from page 2
Show all images
Analyze image 1
Find images about diagrams
What does the image on page 3 show?
```

#### 💻 Code Queries
```
Show me any code examples in the document
Explain the algorithm on page 10
Extract the Python code from this PDF
List the functions mentioned in this code
```

### 🎨 Smart Formatting Examples

The assistant automatically formats responses based on content:

**Lists** - Used for:
- Questions with keywords: "list", "steps", "points", "reasons"
- Responses containing multiple items
- Sequential information

**Paragraphs** - Used for:
- Questions with keywords: "explain", "describe", "summary"
- Narrative or explanatory content
- Definitions and concepts

**Mixed Format** - Intelligently combines both when needed

---

## ⚙️ Configuration

### Model Configuration

Edit `src/config.py` to customize:

```python
# Text Model (for Q&A)
OLLAMA_MODEL = "llama3.2"

# Vision Model (for images)
VISION_MODEL = "llava-phi3"
VISION_MODEL_FALLBACK = "moondream"

# Processing Settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# Auto-Fallback
AUTO_FALLBACK = True
```

### Available Models

#### Text Models
- `llama3.2` (Default - Best quality)
- `llama3.1` (Larger context)
- `mistral` (Fast and efficient)
- `phi3` (Lightweight)
- `gemma` (Google's model)

#### Vision Models
| Model | VRAM | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| llava-phi3 | ~2.5GB | High | Fast | RTX 3050 4GB |
| moondream | ~1.7GB | Good | Very Fast | Low VRAM |
| llava:7b | ~3.5GB | Very High | Medium | High-end GPUs |

---

## 🛠️ Tech Stack

### Core Technologies
- **[Streamlit](https://streamlit.io/)** - Web interface
- **[Ollama](https://ollama.ai/)** - Local LLM inference
- **[LangChain](https://langchain.com/)** - LLM orchestration
- **[FAISS](https://github.com/facebookresearch/faiss)** - Vector database
- **[Sentence Transformers](https://www.sbert.net/)** - Text embeddings

### AI Models
- **LLaMA 3.2** - Text generation
- **LLaVA-Phi3** - Vision understanding
- **Moondream** - Lightweight vision model

### Libraries
```
streamlit>=1.28.0
PyPDF2>=3.0.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
Pillow>=10.0.0
requests>=2.31.0
```

---

## 🎨 Features Showcase

### 1. Smart Auto-Formatting 🆕
The assistant intelligently analyzes your question and the response to automatically format the answer:
- **Lists**: For steps, points, items, reasons, types, methods
- **Paragraphs**: For explanations, descriptions, summaries, overviews
- **Mixed**: Seamlessly combines both formats when needed

### 2. Live Streaming Responses
Responses appear word-by-word like ChatGPT, creating an engaging user experience.

### 3. Code Syntax Highlighting
```python
def process_pdf(file_path):
    """Extract and analyze PDF content"""
    text = extract_text(file_path)
    chunks = chunk_text(text)
    embeddings = create_embeddings(chunks)
    return embeddings
```

### 4. Beautiful Image Grids
Images are displayed in 3-column grids with:
- Styled borders and shadows
- Page number indicators
- Expandable metadata (format, dimensions)
- Responsive layout

### 5. Formatted Text Elements
- **Headers** with colored underlines
- *Blockquotes* with gradient backgrounds
- Lists with proper spacing and numbering
- Tables with hover effects
- Info boxes with gradients

---

## 🔧 Troubleshooting

### Ollama Connection Error
```bash
# Make sure Ollama is running
ollama serve

# Verify models are downloaded
ollama list
```

### VRAM Out of Memory
1. Enable **Auto-Fallback** in the sidebar
2. Switch to a lighter model (moondream)
3. Close other GPU applications
4. Reduce `max_tokens` in `config.py`

### PDF Processing Fails
- Ensure PDF has extractable text (not scanned images)
- Check file size (< 50MB recommended)
- Verify PDF is not password-protected

### Slow Response Times
- Use a smaller model (phi3, mistral)
- Reduce `CHUNK_SIZE` in config
- Lower `TOP_K` for faster retrieval

---

## 📊 Performance Benchmarks

### Processing Times (RTX 3050 4GB)

| Task | Time | Model |
|------|------|-------|
| PDF Indexing (10 pages) | ~5s | - |
| Text Query | ~2-3s | llama3.2 |
| Image Analysis | ~3-4s | llava-phi3 |
| Image Extraction | ~1s | - |
| Smart Formatting | <0.1s | - |

### Resource Usage

| Component | RAM | VRAM |
|-----------|-----|------|
| Base App | ~500MB | - |
| Text Model (llama3.2) | ~2GB | ~2GB |
| Vision Model (llava-phi3) | ~1GB | ~2.5GB |
| **Total** | **~3.5GB** | **~4.5GB** |

---

## 🆕 Latest Updates

### Version 2.0 - Smart Formatting Release
- ✨ **Smart Auto-Formatting**: Automatic list/paragraph detection
- 🎯 **Context-Aware**: Analyzes questions for optimal formatting
- 📊 **Enhanced Lists**: Bold numbered points with proper indentation
- 📝 **Better Paragraphs**: Clean flowing text with headers
- 🔄 **Mixed Content**: Seamlessly combines lists and paragraphs

### Version 1.0 - Initial Release
- 🤖 Dual AI model support
- 📊 RAG with FAISS
- 🖼️ Image extraction and analysis
- 🎨 Beautiful Streamlit interface

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contribution
- [ ] Add support for more file formats (DOCX, TXT)
- [ ] Implement conversation history export
- [ ] Add multi-language support
- [ ] Create Docker container
- [ ] Add API endpoint
- [ ] Implement OCR for scanned PDFs

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Meta AI](https://ai.meta.com/) for LLaMA models
- [Streamlit](https://streamlit.io/) for the amazing framework
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector search
- [Sentence Transformers](https://www.sbert.net/) for embeddings

---

## 📧 Contact

**Aditya Sagar Sharma** - [@adityass2004](https://github.com/adityass2004)

Project Link: [https://github.com/adityass2004/pdf-chat-assistant](https://github.com/adityass2004/pdf-chat-assistant)

---

## 🌟 Features Roadmap

- [x] Smart auto-formatting
- [x] Live streaming responses
- [x] Image extraction and analysis
- [x] Multiple AI models
- [ ] Multi-document chat
- [ ] Conversation export
- [ ] OCR support
- [ ] API endpoints
- [ ] Docker deployment

---

<div align="center">

### ⭐ Star this repo if you find it helpful!

Made with ❤️ by [Aditya Sagar Sharma](https://github.com/adityass2004)

**[⬆ Back to Top](#-pdf-chat-assistant)**

</div>