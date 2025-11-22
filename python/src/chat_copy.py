from src.chunker import chunk_text
from src.embedder import embed_text, model
from src.vector_store import create_index, search_index, save_index, load_index
from src.pdf_extractor import extract_text
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, OLLAMA_MODEL, OLLAMA_URL
try:
    from src.config import VISION_MODEL, VISION_MODEL_FALLBACK, AUTO_FALLBACK
except ImportError:
    VISION_MODEL = "llava-phi3"
    VISION_MODEL_FALLBACK = "moondream"
    AUTO_FALLBACK = True
import numpy as np
import os
import requests
import json
from PyPDF2 import PdfReader
import fitz  # PyMuPDF for image extraction
from PIL import Image
import io
import base64
import re

# Global variables
CHUNKS = []
INDEX = None
PDF_INFO = {}
PDF_IMAGES = []  # Store extracted images
CURRENT_VISION_MODEL = None  # Track which vision model is active

# -----------------------------
# Extract images from PDF
# -----------------------------
def extract_images_from_pdf(pdf_path, output_dir="data/extracted_images"):
    """
    Extract all images from PDF and save them to output directory
    Returns list of image paths with metadata
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    
    try:
        pdf_document = fitz.open(pdf_path)
        image_count = 0
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                # Get image dimensions
                try:
                    with Image.open(image_path) as pil_img:
                        width, height = pil_img.size
                except:
                    width, height = "?", "?"
                
                image_paths.append({
                    "path": image_path,
                    "page": page_num + 1,
                    "filename": image_filename,
                    "format": image_ext,
                    "width": width,
                    "height": height,
                    "index": image_count + 1
                })
                image_count += 1
        
        pdf_document.close()
        print(f"✓ Extracted {image_count} images from PDF")
        return image_paths
        
    except Exception as e:
        print(f"Error extracting images: {e}")
        return []

# -----------------------------
# Analyze image with Ollama vision model
# -----------------------------
def analyze_image_with_ollama(image_path, question=None):
    """
    Analyze an image using Ollama's vision model
    """
    global CURRENT_VISION_MODEL
    
    if question is None:
        question = "Describe this image in detail. What does it show?"
    
    try:
        # Read and encode image
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Try primary vision model
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": VISION_MODEL,
                    "prompt": question,
                    "images": [image_data],
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                CURRENT_VISION_MODEL = VISION_MODEL
                result = response.json()
                return result.get("response", "No response from vision model")
            else:
                raise Exception(f"Vision model returned status {response.status_code}")
                
        except Exception as primary_error:
            # Try fallback model if auto-fallback is enabled
            if AUTO_FALLBACK:
                print(f"⚠️ Primary model failed, trying {VISION_MODEL_FALLBACK}...")
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": VISION_MODEL_FALLBACK,
                        "prompt": question,
                        "images": [image_data],
                        "stream": False
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    CURRENT_VISION_MODEL = VISION_MODEL_FALLBACK
                    result = response.json()
                    return result.get("response", "No response from fallback vision model")
                else:
                    raise Exception(f"Fallback model also failed: {response.status_code}")
            else:
                raise primary_error
                
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Make sure 'ollama serve' is running."
    except Exception as e:
        return f"Error analyzing image: {str(e)}\nMake sure vision model '{VISION_MODEL}' is installed: ollama pull {VISION_MODEL}"

# -----------------------------
# Model management functions
# -----------------------------
def list_available_models():
    """
    List all available Ollama models
    """
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            print("\n📦 Available Models:")
            print("\n🔤 Text Models:")
            for model in models:
                name = model.get("name", "")
                if "llava" not in name.lower() and "moondream" not in name.lower():
                    size = model.get("size", 0) / (1024**3)  # Convert to GB
                    print(f"  • {name} ({size:.1f}GB)")
            
            print("\n📷 Vision Models:")
            for model in models:
                name = model.get("name", "")
                if "llava" in name.lower() or "moondream" in name.lower():
                    size = model.get("size", 0) / (1024**3)
                    print(f"  • {name} ({size:.1f}GB)")
            
            return True
        else:
            print("Could not fetch models from Ollama")
            return False
    except Exception as e:
        print(f"Error listing models: {e}")
        return False


def show_current_config():
    """
    Display current model configuration
    """
    print("\n⚙️ Current Configuration:")
    print(f"  📝 Text Model: {OLLAMA_MODEL}")
    print(f"  🖼️ Vision Model: {VISION_MODEL}")
    print(f"  🔄 Fallback Model: {VISION_MODEL_FALLBACK}")
    print(f"  🤖 Auto-Fallback: {'Enabled' if AUTO_FALLBACK else 'Disabled'}")
    if CURRENT_VISION_MODEL:
        print(f"  ✅ Last Used Vision Model: {CURRENT_VISION_MODEL}")


def switch_vision_model(model_name):
    """
    Switch the active vision model
    """
    global VISION_MODEL
    
    # Check if model exists
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if model is available
            if not any(model_name in name for name in model_names):
                print(f"❌ Model '{model_name}' not found.")
                print(f"💡 Download it with: ollama pull {model_name}")
                return False
            
            VISION_MODEL = model_name
            print(f"✅ Switched to vision model: {model_name}")
            return True
        else:
            print("Could not verify model availability")
            return False
    except Exception as e:
        print(f"Error switching model: {e}")
        return False


# -----------------------------
# Display image info
# -----------------------------
def display_images_info(page_filter=None):
    """
    Display information about extracted images
    """
    if not PDF_IMAGES:
        print("\nNo images found in this PDF.")
        return
    
    filtered_images = PDF_IMAGES
    if page_filter:
        filtered_images = [img for img in PDF_IMAGES if img['page'] == page_filter]
        if not filtered_images:
            print(f"\nNo images found on page {page_filter}.")
            return
    
    print(f"\n📷 Found {len(filtered_images)} image(s):")
    for img_info in filtered_images:
        print(f"  {img_info['index']}. {img_info['filename']} - Page {img_info['page']}")
        print(f"     Format: {img_info['format']} | Size: {img_info['width']}x{img_info['height']}px")
        print(f"     Path: {img_info['path']}")


# -----------------------------
# Open and optionally analyze image
# -----------------------------
def open_image(image_index, analyze=False):
    """
    Open image by index and optionally analyze it
    """
    if not PDF_IMAGES:
        print("No images available.")
        return None
    
    if image_index < 1 or image_index > len(PDF_IMAGES):
        print(f"Invalid image index. Please choose between 1 and {len(PDF_IMAGES)}")
        return None
    
    img_info = PDF_IMAGES[image_index - 1]
    try:
        img = Image.open(img_info['path'])
        img.show()
        print(f"✓ Opened: {img_info['filename']} (Page {img_info['page']})")
        
        if analyze:
            print("\n🔍 Analyzing image content...")
            description = analyze_image_with_ollama(img_info['path'])
            print(f"\n📊 Image Analysis:\n{description}")
            return description
        
        return img_info
        
    except Exception as e:
        print(f"Error opening image: {e}")
        return None


# -----------------------------
# Get images by page
# -----------------------------
def get_images_by_page(page_num):
    """
    Get all images from a specific page
    """
    return [img for img in PDF_IMAGES if img['page'] == page_num]


# -----------------------------
# Search images by topic
# -----------------------------
def search_images_by_topic(topic):
    """
    Search for images related to a topic by analyzing their content
    """
    if not PDF_IMAGES:
        return []
    
    print(f"\n🔍 Searching for images related to: {topic}")
    relevant_images = []
    
    for img_info in PDF_IMAGES:
        # Analyze each image with the topic as context
        question = f"Does this image relate to {topic}? Answer yes or no, then briefly explain why."
        analysis = analyze_image_with_ollama(img_info['path'], question)
        
        # Check if the response indicates relevance
        if "yes" in analysis.lower()[:50]:  # Check beginning of response
            relevant_images.append({
                "info": img_info,
                "analysis": analysis
            })
    
    return relevant_images


# -----------------------------
# Ollama query
# -----------------------------
def ollama_query(prompt, model_name=OLLAMA_MODEL):
    """
    Sends prompt to local Ollama LLaMA3 endpoint via /v1/completions
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 300
    }

    try:
        response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            res_json = response.json()
            print("\n[OLLAMA RAW RESPONSE]:", json.dumps(res_json, indent=2))

            if "choices" in res_json and len(res_json["choices"]) > 0:
                return res_json["choices"][0].get("text", "[No completion returned]")
            else:
                return "[No completion returned]"
        else:
            return f"Ollama error {response.status_code}: {response.text}"

    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Make sure 'ollama serve' is running."


# -----------------------------
# Build FAISS index
# -----------------------------
def build_index(pdf_path):
    global CHUNKS, INDEX, PDF_INFO, PDF_IMAGES

    # Extract metadata
    file_stats = os.stat(pdf_path)
    reader = PdfReader(pdf_path)
    PDF_INFO = {
        "file_name": os.path.basename(pdf_path),
        "page_count": len(reader.pages),
        "file_size_kb": round(file_stats.st_size / 1024, 2),
        "format": "PDF Document",
    }

    # Extract images (always safe)
    PDF_IMAGES = extract_images_from_pdf(pdf_path)

    # Extract text
    text = extract_text(pdf_path)
    if not text or not text.strip():
        print("⚠️ No text detected in this PDF. Skipping text embedding.")
        CHUNKS, INDEX = [], None
        save_index(None)
        return

    # Continue normally if text exists
    CHUNKS = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    embeddings = embed_text(CHUNKS)
    INDEX = create_index(embeddings)
    save_index(INDEX)

    print(f"✅ Index created with {len(CHUNKS)} chunks for {PDF_INFO['file_name']}.")


# -----------------------------
# Load existing FAISS index
# -----------------------------
def load_existing_index():
    global INDEX
    INDEX = load_index()
    if INDEX is None:
        print("No existing index found. Building new index is required.")
    else:
        print("FAISS index loaded successfully.")


# -----------------------------
# Parse natural image queries
# -----------------------------
def parse_image_query(query):
    """
    Parse natural language image queries
    Returns: (action, page_num, topic)
    """
    query_lower = query.lower()
    
    # Extract page number
    page_match = re.search(r'page\s+(\d+)', query_lower)
    page_num = int(page_match.group(1)) if page_match else None
    
    # Detect action type
    if any(word in query_lower for word in ["show", "display", "see", "view", "list"]):
        if page_num:
            return ("show_page_images", page_num, None)
        elif any(word in query_lower for word in ["all", "every", "list"]):
            return ("show_all_images", None, None)
        else:
            # Check for topic
            topic_indicators = ["about", "related to", "of", "with", "regarding"]
            for indicator in topic_indicators:
                if indicator in query_lower:
                    topic = query_lower.split(indicator, 1)[1].strip()
                    return ("search_topic", None, topic)
    
    if any(word in query_lower for word in ["open", "analyze", "describe"]):
        # Try to find image number
        num_match = re.search(r'(?:image|img|picture|photo)\s+(\d+)', query_lower)
        if num_match:
            img_num = int(num_match.group(1))
            return ("open_and_analyze", img_num, None)
        elif page_num:
            return ("analyze_page", page_num, None)
    
    return (None, None, None)


# -----------------------------
# Get Answer
# -----------------------------
def get_answer(query):
    """
    Mix general AI conversation + PDF-aware context + intelligent image handling
    """
    query_lower = query.lower().strip()
    
    # Check for image-related queries
    if any(word in query_lower for word in ["image", "picture", "photo", "diagram", "figure"]):
        action, page_num, topic = parse_image_query(query)
        
        if action == "show_page_images":
            images = get_images_by_page(page_num)
            if images:
                print(f"\n📷 Images on page {page_num}:")
                for img in images:
                    print(f"  {img['index']}. {img['filename']} ({img['format']}, {img['width']}x{img['height']}px)")
                return f"Found {len(images)} image(s) on page {page_num}. Use 'open image <number>' to view or 'analyze image <number>' to get details."
            else:
                return f"No images found on page {page_num}."
        
        elif action == "show_all_images":
            display_images_info()
            return f"Displayed information for {len(PDF_IMAGES)} images."
        
        elif action == "search_topic":
            results = search_images_by_topic(topic)
            if results:
                print(f"\n📷 Found {len(results)} relevant image(s):")
                for i, result in enumerate(results, 1):
                    img_info = result['info']
                    print(f"\n{i}. Image {img_info['index']}: {img_info['filename']} (Page {img_info['page']})")
                    print(f"   Analysis: {result['analysis'][:200]}...")
                return f"Found {len(results)} images related to '{topic}'."
            else:
                return f"No images found related to '{topic}'."
        
        elif action == "open_and_analyze":
            open_image(page_num, analyze=True)
            return ""
        
        elif action == "analyze_page":
            images = get_images_by_page(page_num)
            if images:
                print(f"\n📊 Analyzing {len(images)} image(s) on page {page_num}...")
                for img in images:
                    print(f"\n--- Image {img['index']}: {img['filename']} ---")
                    description = analyze_image_with_ollama(img['path'])
                    print(description)
                return ""
            else:
                return f"No images found on page {page_num}."
    
    # Standard text-based query handling
    generic_keywords = ["who", "what", "how", "when", "where", "why", "hello", "hi", "good", "hey"]
    is_generic = any(query_lower.startswith(word) for word in generic_keywords) and len(query_lower.split()) <= 4

    # Build context
    pdf_meta_context = (
        f"The current document is '{PDF_INFO.get('file_name', 'Unknown')}', "
        f"a {PDF_INFO.get('format', 'PDF file')} with {PDF_INFO.get('page_count', '?')} pages, "
        f"and a file size of about {PDF_INFO.get('file_size_kb', '?')} KB.\n"
    )
    
    if len(PDF_IMAGES) > 0:
        pdf_meta_context += f"This PDF contains {len(PDF_IMAGES)} images. "

    if is_generic or INDEX is None or not CHUNKS:
        prompt = f"You are an AI assistant chatting with a user. Be friendly and helpful.\n" \
                 f"PDF Info: {pdf_meta_context}\nUser: {query}"
    else:
        query_embedding = model.encode([query])[0]
        top_indices = search_index(INDEX, query_embedding, TOP_K)
        context = "\n".join([CHUNKS[i] for i in top_indices])
        prompt = (
            f"You are an AI assistant who has full knowledge about the given PDF document.\n"
            f"PDF Info: {pdf_meta_context}\n"
            f"Use this context to answer questions accurately.\n"
            f"Context: {context}\nUser Question: {query}"
        )

    return ollama_query(prompt)


# -----------------------------
# CLI Chat
# -----------------------------
def start_chat():
    global CHUNKS, INDEX, PDF_INFO, PDF_IMAGES

    pdf_path = ""
    while not pdf_path or not os.path.exists(pdf_path):
        pdf_path = input("Enter path to PDF file: ").strip()
        if not pdf_path:
            print("You must enter a PDF path.")
        elif not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}. Please enter a valid path.")

    # Build or load index
    if not os.path.exists("embeddings/index.faiss"):
        build_index(pdf_path)
    else:
        load_existing_index()
        text = extract_text(pdf_path)

        if not text or not text.strip():
            print("⚠️ No text detected. Switching to image-only mode.")
            CHUNKS, INDEX = [], None
        else:
            CHUNKS = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

        # Gather metadata
        file_stats = os.stat(pdf_path)
        reader = PdfReader(pdf_path)
        PDF_INFO = {
            "file_name": os.path.basename(pdf_path),
            "page_count": len(reader.pages),
            "file_size_kb": round(file_stats.st_size / 1024, 2),
            "format": "PDF Document",
        }

        # Extract images
        PDF_IMAGES = extract_images_from_pdf(pdf_path)

    print(f"\n📘 Loaded PDF: {PDF_INFO['file_name']} ({PDF_INFO['page_count']} pages, {PDF_INFO['file_size_kb']} KB)")
    if PDF_IMAGES:
        print(f"📷 Found {len(PDF_IMAGES)} images")
    else:
        print("❌ No images found in this PDF.")

    print("\n" + "=" * 70)
    print("PDF Chat Ready! You can ask questions naturally:")
    print("  • 'Show images from page 2'")
    print("  • 'Analyze image 1'")
    print("  • 'exit' - Quit")
    print("=" * 70)

    while True:
        query = input("\n💬 Your question: ").strip()

        if query.lower() == "exit":
            break
        if not query:
            print("Please type a question or command.")
            continue

        answer = get_answer(query)
        if answer:
            print("\n💡 Answer:", answer)


if __name__ == "__main__":
    start_chat()