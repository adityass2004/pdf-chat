from src.chunker import chunk_text
from src.embedder import embed_text, model
from src.vector_store import create_index, search_index, save_index, load_index
from src.pdf_extractor import extract_text
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, OLLAMA_MODEL, OLLAMA_URL
from src.image_handler import ImageHandler
from src.query_parser import parse_image_query
from src.model_manager import ModelManager
from src.utils import setup_logging
import requests
import json
import os
from PyPDF2 import PdfReader

logger = setup_logging()

class PDFChat:
    def __init__(self):
        self.chunks = []
        self.index = None
        self.pdf_info = {}
        self.image_handler = ImageHandler()
        self.model_manager = ModelManager()

    def ollama_query(self, prompt, model_name=OLLAMA_MODEL):
        """
        Sends prompt to local Ollama LLaMA3 endpoint via /v1/completions.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        try:
            response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                res_json = response.json()
                logger.debug(f"Ollama raw response: {json.dumps(res_json, indent=2)}")

                if "choices" in res_json and len(res_json["choices"]) > 0:
                    return res_json["choices"][0].get("text", "[No completion returned]")
                else:
                    return "[No completion returned]"
            else:
                return f"Ollama error {response.status_code}: {response.text}"

        except requests.exceptions.ConnectionError:
            return "Cannot connect to Ollama. Make sure 'ollama serve' is running."

    def build_index(self, pdf_path):
        """
        Build FAISS index for the PDF.
        """
        # Extract metadata
        file_stats = os.stat(pdf_path)
        reader = PdfReader(pdf_path)
        self.pdf_info = {
            "file_name": os.path.basename(pdf_path),
            "page_count": len(reader.pages),
            "file_size_kb": round(file_stats.st_size / 1024, 2),
            "format": "PDF Document",
        }

        # Extract images
        self.image_handler.extract_images_from_pdf(pdf_path)

        # Extract text
        text = extract_text(pdf_path)
        if not text or not text.strip():
            logger.warning("No text detected in this PDF. Skipping text embedding.")
            self.chunks, self.index = [], None
            save_index(None)
            return

        # Continue normally if text exists
        self.chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        embeddings = embed_text(self.chunks)
        self.index = create_index(embeddings)
        save_index(self.index)

        logger.info(f"Index created with {len(self.chunks)} chunks for {self.pdf_info['file_name']}.")

    def load_existing_index(self):
        """
        Load existing FAISS index.
        """
        self.index = load_index()
        if self.index is None:
            logger.warning("No existing index found. Building new index is required.")
        else:
            logger.info("FAISS index loaded successfully.")

    def build_enhanced_prompt(self, query, context, pdf_meta_context):
        """
        Build an enhanced prompt for better PDF-aware responses.
        """
        prompt = f"""You are an intelligent PDF analysis assistant with deep understanding of document content.

DOCUMENT INFORMATION:
{pdf_meta_context}

YOUR ROLE:
- Provide accurate, detailed answers based ONLY on the document content provided
- Use the context below to answer questions precisely
- If information is not in the context, clearly state "This information is not available in the provided document"
- Cite specific details from the context when answering
- Provide clear, well-structured responses
- If asked about page numbers or specific sections, reference them if available in context

CONTEXT FROM DOCUMENT:
{context}

IMPORTANT GUIDELINES:
1. Answer based ONLY on the context provided above
2. Be specific and reference exact information from the context
3. If the context doesn't contain enough information, say so clearly
4. Don't make assumptions beyond what's in the document
5. Structure your answer clearly with relevant details
6. If multiple pieces of information are relevant, organize them logically

USER QUESTION: {query}

ANSWER (based on the document context):"""
        
        return prompt

    def build_generic_prompt(self, query, pdf_meta_context):
        """
        Build a prompt for general conversation or document metadata queries.
        """
        prompt = f"""You are a helpful AI assistant for PDF document analysis.

DOCUMENT INFORMATION:
{pdf_meta_context}

USER QUERY: {query}

INSTRUCTIONS:
- If asked about the document itself (filename, pages, size), use the document information above
- For general greetings or conversation, respond naturally and friendly
- If asked about document content but no specific context is available, inform the user you need more specific questions to search the document
- Be concise and helpful

YOUR RESPONSE:"""
        
        return prompt

    def get_answer(self, query):
        """
        Mix general AI conversation + PDF-aware context + intelligent image handling.
        """
        query_lower = query.lower().strip()
        
        # Check for image-related queries
        if any(word in query_lower for word in ["image", "picture", "photo", "diagram", "figure"]):
            action, page_num, topic = parse_image_query(query)
            
            if action == "show_page_images":
                images = self.image_handler.get_images_by_page(page_num)
                if images:
                    logger.info(f"Images on page {page_num}:")
                    for img in images:
                        logger.info(f"  {img['index']}. {img['filename']} ({img['format']}, {img['width']}x{img['height']}px)")
                    return f"Found {len(images)} image(s) on page {page_num}. Use 'open image <number>' to view or 'analyze image <number>' to get details."
                else:
                    return f"No images found on page {page_num}."
            
            elif action == "show_all_images":
                self.image_handler.display_images_info()
                return f"Displayed information for {len(self.image_handler.images)} images."
            
            elif action == "search_topic":
                results = self.image_handler.search_images_by_topic(topic)
                if results:
                    logger.info(f"Found {len(results)} relevant image(s):")
                    for i, result in enumerate(results, 1):
                        img_info = result['info']
                        logger.info(f"\n{i}. Image {img_info['index']}: {img_info['filename']} (Page {img_info['page']})")
                        logger.info(f"   Analysis: {result['analysis'][:200]}...")
                    return f"Found {len(results)} images related to '{topic}'."
                else:
                    return f"No images found related to '{topic}'."
            
            elif action == "open_and_analyze":
                self.image_handler.open_image(page_num, analyze=True)
                return ""
            
            elif action == "analyze_page":
                images = self.image_handler.get_images_by_page(page_num)
                if images:
                    logger.info(f"Analyzing {len(images)} image(s) on page {page_num}...")
                    for img in images:
                        logger.info(f"\n--- Image {img['index']}: {img['filename']} ---")
                        description = self.image_handler.analyze_image_with_ollama(img['path'])
                        logger.info(description)
                else:
                    return f"No images found on page {page_num}."
                return ""
        
        # Build PDF metadata context
        pdf_meta_context = (
            f"Document Name: '{self.pdf_info.get('file_name', 'Unknown')}'\n"
            f"Format: {self.pdf_info.get('format', 'PDF file')}\n"
            f"Total Pages: {self.pdf_info.get('page_count', '?')}\n"
            f"File Size: {self.pdf_info.get('file_size_kb', '?')} KB\n"
        )
        
        if len(self.image_handler.images) > 0:
            pdf_meta_context += f"Images in Document: {len(self.image_handler.images)}\n"

        # Check if it's a generic query or document-specific query
        generic_keywords = ["hello", "hi", "hey", "thanks", "thank you", "goodbye", "bye"]
        metadata_keywords = ["how many pages", "file size", "document name", "filename", "pdf name"]
        
        is_generic = any(query_lower.startswith(word) for word in generic_keywords)
        is_metadata_query = any(keyword in query_lower for keyword in metadata_keywords)

        # Handle queries based on type
        if is_generic:
            # Simple greeting or conversation
            prompt = self.build_generic_prompt(query, pdf_meta_context)
            return self.ollama_query(prompt)
        
        elif is_metadata_query:
            # Query about document metadata
            prompt = self.build_generic_prompt(query, pdf_meta_context)
            return self.ollama_query(prompt)
        
        elif self.index is None or not self.chunks:
            # No content available
            return f"This PDF appears to have no text content available for analysis. {pdf_meta_context}\nPlease ask about document metadata or upload a text-based PDF."
        
        else:
            # Content-based query - use RAG
            query_embedding = model.encode([query])[0]
            top_indices = search_index(self.index, query_embedding, TOP_K)
            
            # Get relevant context chunks
            context_chunks = [self.chunks[i] for i in top_indices]
            context = "\n\n".join([f"[Excerpt {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)])
            
            # Build enhanced prompt
            prompt = self.build_enhanced_prompt(query, context, pdf_meta_context)
            
            return self.ollama_query(prompt)

    def start_chat(self):
        """
        CLI Chat interface.
        """
        pdf_path = ""
        while not pdf_path or not os.path.exists(pdf_path):
            pdf_path = input("Enter path to PDF file: ").strip()
            if not pdf_path:
                logger.warning("You must enter a PDF path.")
            elif not os.path.exists(pdf_path):
                logger.error(f"File not found: {pdf_path}. Please enter a valid path.")

        # Build or load index
        if not os.path.exists("embeddings/index.faiss"):
            self.build_index(pdf_path)
        else:
            self.load_existing_index()
            text = extract_text(pdf_path)

            if not text or not text.strip():
                logger.warning("No text detected. Switching to image-only mode.")
                self.chunks, self.index = [], None
            else:
                self.chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

            # Gather metadata
            file_stats = os.stat(pdf_path)
            reader = PdfReader(pdf_path)
            self.pdf_info = {
                "file_name": os.path.basename(pdf_path),
                "page_count": len(reader.pages),
                "file_size_kb": round(file_stats.st_size / 1024, 2),
                "format": "PDF Document",
            }

            # Extract images
            self.image_handler.extract_images_from_pdf(pdf_path)

        logger.info(f"Loaded PDF: {self.pdf_info['file_name']} ({self.pdf_info['page_count']} pages, {self.pdf_info['file_size_kb']} KB)")
        if self.image_handler.images:
            logger.info(f"Found {len(self.image_handler.images)} images")
        else:
            logger.info("No images found in this PDF.")

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

            answer = self.get_answer(query)
            if answer:
                print("\n💡 Answer:", answer)


if __name__ == "__main__":
    chat = PDFChat()
    chat.start_chat()