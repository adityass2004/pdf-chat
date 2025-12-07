import streamlit as st
import os
import sys
import time
import re

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chat_copy import PDFChat
from src.config import (
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K,
    OLLAMA_MODEL, VISION_MODEL, VISION_MODEL_FALLBACK,
    AVAILABLE_VISION_MODELS, AUTO_FALLBACK
)
from PyPDF2 import PdfReader
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better formatting
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    
    /* Enhanced code block styling */
    .stCodeBlock {
        background-color: #1e1e1e !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border: 1px solid #333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Inline code styling */
    code {
        background-color: #f5f5f5 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 0.9em !important;
        color: #d73a49 !important;
        border: 1px solid #e1e4e8 !important;
    }
    
    pre code {
        background-color: transparent !important;
        color: #f8f8f2 !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Image container styling */
    .image-container {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        background: #fafafa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 4px solid #0066cc;
        padding: 0.8rem 1.2rem;
        margin: 1rem 0;
        color: #555;
        background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 0 8px 8px 0;
        font-style: italic;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Lists with better spacing */
    .stMarkdown ul, .stMarkdown ol {
        padding-left: 2rem;
        margin: 1rem 0;
    }
    
    .stMarkdown li {
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    /* Tables */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    
    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #e0e0e0;
    }
    
    tbody tr:hover {
        background-color: #f5f5f5;
    }
    
    /* Headers */
    .stMarkdown h1 {
        color: #1a1a1a;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    .stMarkdown h2 {
        color: #2a2a2a;
        border-bottom: 2px solid #764ba2;
        padding-bottom: 0.4rem;
        margin: 1.3rem 0 0.8rem 0;
    }
    
    .stMarkdown h3 {
        color: #3a3a3a;
        margin: 1.2rem 0 0.6rem 0;
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Image captions */
    .stImage > div {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Point formatting */
    .point-container {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .point-number {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pdf_chat' not in st.session_state:
    st.session_state.pdf_chat = PDFChat()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_loaded' not in st.session_state:
    st.session_state.pdf_loaded = False
if 'current_pdf_path' not in st.session_state:
    st.session_state.current_pdf_path = None
if 'selected_text_model' not in st.session_state:
    st.session_state.selected_text_model = OLLAMA_MODEL
if 'selected_vision_model' not in st.session_state:
    st.session_state.selected_vision_model = VISION_MODEL
if 'auto_fallback_enabled' not in st.session_state:
    st.session_state.auto_fallback_enabled = AUTO_FALLBACK
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

def analyze_content_type(text):
    """Analyze the content to determine optimal formatting"""
    text_lower = text.lower()
    
    # Check for list indicators
    list_patterns = [
        r'^\d+[\.\)]\s',  # Numbered lists: 1. or 1)
        r'^[-•*]\s',  # Bullet points
        r'\n\d+[\.\)]\s',  # Numbered lists in middle
        r'\n[-•*]\s',  # Bullet points in middle
    ]
    
    # Count list-like structures
    list_count = sum(len(re.findall(pattern, text, re.MULTILINE)) for pattern in list_patterns)
    
    # Keywords that suggest list format
    list_keywords = ['steps', 'points', 'list', 'items', 'reasons', 'factors', 
                     'aspects', 'features', 'benefits', 'advantages', 'methods',
                     'types', 'categories', 'elements', 'components', 'ways']
    
    has_list_keywords = any(keyword in text_lower for keyword in list_keywords)
    
    # Keywords that suggest paragraph format
    para_keywords = ['explain', 'describe', 'summary', 'overview', 'introduction',
                     'conclusion', 'discussion', 'analysis', 'definition', 'concept',
                     'meaning', 'understanding']
    
    has_para_keywords = any(keyword in text_lower for keyword in para_keywords)
    
    # Detect enumeration in text
    has_enumeration = bool(re.search(r'(first|second|third|fourth|fifth|finally|lastly|next)', text_lower))
    
    return {
        'has_lists': list_count > 0,
        'list_count': list_count,
        'suggest_list': has_list_keywords or list_count > 2 or has_enumeration,
        'suggest_para': has_para_keywords and list_count < 2,
        'has_code': '```' in text or 'def ' in text or 'class ' in text
    }

def smart_format_response(text, query=""):
    """Automatically format response based on content analysis"""
    if not text:
        return text
    
    # Analyze both the response and query
    content_info = analyze_content_type(text)
    query_info = analyze_content_type(query)
    
    # Preserve code blocks
    code_blocks = []
    code_pattern = r'```[\s\S]*?```'
    
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    text = re.sub(code_pattern, save_code_block, text)
    
    # Smart formatting decision
    formatted_text = text
    
    # If content suggests list format
    if content_info['suggest_list'] or query_info['suggest_list']:
        formatted_text = format_as_structured_list(text)
    # If content is narrative/explanatory
    elif content_info['suggest_para'] or query_info['suggest_para']:
        formatted_text = format_as_paragraphs(text)
    # Default: Auto-detect and format
    else:
        formatted_text = auto_format_mixed_content(text)
    
    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        formatted_text = formatted_text.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return formatted_text

def format_as_structured_list(text):
    """Format text as a structured list with proper numbering"""
    lines = text.split('\n')
    formatted_lines = []
    point_number = 1
    in_list = False
    current_point = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_point:
                formatted_lines.append('\n'.join(current_point))
                current_point = []
                in_list = False
            formatted_lines.append('')
            continue
        
        # Detect list item
        list_match = re.match(r'^(\d+[\.\)]|[-•*])\s*(.+)$', line)
        
        if list_match:
            if current_point:
                formatted_lines.append('\n'.join(current_point))
                current_point = []
            
            content = list_match.group(2)
            current_point = [f"**{point_number}. {content}**"]
            point_number += 1
            in_list = True
        elif in_list and line:
            # Continuation of current point
            current_point.append(f"   {line}")
        else:
            if current_point:
                formatted_lines.append('\n'.join(current_point))
                current_point = []
                in_list = False
            formatted_lines.append(line)
    
    if current_point:
        formatted_lines.append('\n'.join(current_point))
    
    return '\n\n'.join([line for line in formatted_lines if line])

def format_as_paragraphs(text):
    """Format text as flowing paragraphs"""
    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    formatted_paras = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if it's a header
        if len(para) < 100 and not para.endswith('.') and not para.endswith(','):
            formatted_paras.append(f"### {para}")
        else:
            # Regular paragraph with proper spacing
            sentences = re.split(r'([.!?]+\s+)', para)
            cleaned = ''.join(sentences).strip()
            formatted_paras.append(cleaned)
    
    return '\n\n'.join(formatted_paras)

def auto_format_mixed_content(text):
    """Auto-format content with mixed lists and paragraphs"""
    lines = text.split('\n')
    formatted_lines = []
    current_section = []
    section_type = None  # 'list' or 'para'
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line - finalize current section
            if current_section:
                if section_type == 'list':
                    formatted_lines.append(format_list_section(current_section))
                else:
                    formatted_lines.append(' '.join(current_section))
                current_section = []
                section_type = None
            formatted_lines.append('')
            continue
        
        # Detect if line is a list item
        is_list_item = bool(re.match(r'^(\d+[\.\)]|[-•*])\s', line))
        
        if is_list_item:
            # Switch to list mode
            if section_type == 'para' and current_section:
                formatted_lines.append(' '.join(current_section))
                current_section = []
            section_type = 'list'
            current_section.append(line)
        else:
            # Paragraph mode
            if section_type == 'list' and current_section:
                formatted_lines.append(format_list_section(current_section))
                current_section = []
            section_type = 'para'
            current_section.append(line)
    
    # Finalize last section
    if current_section:
        if section_type == 'list':
            formatted_lines.append(format_list_section(current_section))
        else:
            formatted_lines.append(' '.join(current_section))
    
    return '\n\n'.join([line for line in formatted_lines if line])

def format_list_section(items):
    """Format a section of list items"""
    formatted_items = []
    for i, item in enumerate(items, 1):
        # Remove existing numbering
        item = re.sub(r'^(\d+[\.\)]|[-•*])\s*', '', item)
        formatted_items.append(f"**{i}.** {item}")
    return '\n\n'.join(formatted_items)

def detect_code_in_text(text):
    """Detect if text contains code patterns"""
    code_indicators = [
        'def ', 'class ', 'import ', 'from ',  # Python
        'function ', 'const ', 'let ', 'var ',  # JavaScript
        'public ', 'private ', 'void ',  # Java/C#
        '{', '}', '=>', '==', '!=',  # Common syntax
        '```'  # Markdown code blocks
    ]
    return any(indicator in text for indicator in code_indicators)

def stream_text(text, delay=0.015):
    """Stream text with smart pausing at section boundaries"""
    # Split by major sections
    sections = re.split(r'(\n\n+)', text)
    streamed_text = ""
    
    for section in sections:
        if section.strip():
            # Check if it's a code block
            if '```' in section:
                # Show code blocks instantly
                streamed_text += section
                yield streamed_text
            else:
                # Stream words with slight pause at punctuation
                words = section.split()
                for word in words:
                    streamed_text += word + " "
                    yield streamed_text
                    
                    # Longer pause at sentence ends
                    if word.endswith(('.', '!', '?', ':')):
                        time.sleep(delay * 2)
                    else:
                        time.sleep(delay)
        else:
            streamed_text += section
            yield streamed_text

def load_pdf(pdf_file):
    """Load and process the PDF file"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        pdf_path = os.path.join(data_dir, pdf_file.name)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_file.getvalue())
        
        st.session_state.current_pdf_path = pdf_path
        
        with st.spinner("🔄 Processing PDF... Extracting text and images..."):
            st.session_state.pdf_chat.build_index(pdf_path)
            st.session_state.pdf_loaded = True
            st.session_state.chat_history = []
        
        return True
    except Exception as e:
        st.error(f"❌ Error loading PDF: {str(e)}")
        return False

def display_pdf_info():
    """Display PDF information in sidebar"""
    if st.session_state.pdf_loaded and st.session_state.pdf_chat.pdf_info:
        info = st.session_state.pdf_chat.pdf_info
        st.sidebar.success("✅ PDF Loaded Successfully!")
        
        with st.sidebar.expander("📄 Document Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pages", info.get('page_count', 'N/A'))
            with col2:
                st.metric("Size (KB)", info.get('file_size_kb', 'N/A'))
            
            st.markdown(f"**Filename:** `{info.get('file_name', 'N/A')}`")
            
            if st.session_state.pdf_chat.chunks:
                st.info(f"📦 **{len(st.session_state.pdf_chat.chunks)}** text chunks indexed")
            
            if st.session_state.pdf_chat.image_handler.images:
                st.info(f"🖼️ **{len(st.session_state.pdf_chat.image_handler.images)}** images found")

def display_model_selector():
    """Display model selection interface in sidebar"""
    with st.sidebar.expander("🤖 AI Model Configuration", expanded=True):
        st.markdown("### 💬 Text Model")
        
        text_models = ["llama3.2", "llama3.1", "llama3", "llama2", "mistral", "phi3", "gemma"]
        
        selected_text = st.selectbox(
            "Select Text Model",
            options=text_models,
            index=text_models.index(st.session_state.selected_text_model) if st.session_state.selected_text_model in text_models else 0,
            help="Model used for text analysis and Q&A",
            label_visibility="collapsed"
        )
        
        if selected_text != st.session_state.selected_text_model:
            st.session_state.selected_text_model = selected_text
        
        st.markdown("### 👁️ Vision Model")
        
        vision_model_options = list(AVAILABLE_VISION_MODELS.keys())
        
        selected_vision = st.selectbox(
            "Select Vision Model",
            options=vision_model_options,
            index=vision_model_options.index(st.session_state.selected_vision_model) if st.session_state.selected_vision_model in vision_model_options else 0,
            help="Model used for image analysis",
            label_visibility="collapsed"
        )
        
        if selected_vision != st.session_state.selected_vision_model:
            st.session_state.selected_vision_model = selected_vision
        
        if selected_vision in AVAILABLE_VISION_MODELS:
            details = AVAILABLE_VISION_MODELS[selected_vision]
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"💾 {details['vram']}")
                st.caption(f"⚡ {details['speed']}")
            with col2:
                st.caption(f"✨ {details['quality']}")
        
        st.divider()
        
        auto_fallback = st.toggle(
            "🔄 Auto-Fallback",
            value=st.session_state.auto_fallback_enabled,
            help="Automatically switch to fallback model if primary fails"
        )
        
        st.session_state.auto_fallback_enabled = auto_fallback

def display_images_in_grid(images):
    """Display images in a beautiful grid with proper boxes"""
    st.markdown("---")
    st.markdown("### 🖼️ Images from Document")
    
    for i in range(0, len(images), 3):
        cols = st.columns(3)
        for j, img_info in enumerate(images[i:i+3]):
            with cols[j]:
                with st.container():
                    try:
                        if os.path.exists(img_info['path']):
                            image = Image.open(img_info['path'])
                            
                            st.markdown(f"""
                            <div style='border: 2px solid #e0e0e0; border-radius: 12px; padding: 1rem; 
                                        background: #fafafa; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.image(image, use_container_width=True)
                            
                            with st.expander(f"📊 Image {img_info['index']} Details"):
                                st.markdown(f"""
                                **Page:** `{img_info['page']}`  
                                **Format:** `{img_info['format']}`  
                                **Dimensions:** `{img_info['width']} × {img_info['height']} px`  
                                **File:** `{img_info['filename']}`
                                """)
                    except Exception as e:
                        st.error(f"❌ Could not load image: {str(e)}")

def display_chat_history():
    """Display chat messages with enhanced formatting"""
    for idx, message in enumerate(st.session_state.chat_history):
        if message['role'] == 'user':
            with st.chat_message("user", avatar="👤"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                # Smart format content
                formatted_content = smart_format_response(message['content'], 
                                                         message.get('query', ''))
                st.markdown(formatted_content)
                
                # Display images if present
                if 'images' in message and message['images'] and len(message['images']) > 0:
                    display_images_in_grid(message['images'])

def main():
    # Header
    st.title("📄 PDF Chat Assistant")
    st.markdown("✨ *AI-powered document analysis with smart formatting*")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document to start chatting",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            if st.button("🚀 Process PDF", type="primary", use_container_width=True):
                if load_pdf(uploaded_file):
                    st.rerun()
        
        st.divider()
        display_pdf_info()
        st.divider()
        display_model_selector()
        
        if st.session_state.pdf_loaded:
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("📤 New", use_container_width=True):
                    st.session_state.pdf_loaded = False
                    st.session_state.chat_history = []
                    st.session_state.pdf_chat = PDFChat()
                    st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ Help & Examples"):
            st.markdown("""
            #### 📝 Text Questions
            Ask about content, summaries, or specific topics
            
            #### 🖼️ Image Queries
            - `Show images from page 2`
            - `Show all images`
            - `Analyze image 1`
            
            #### 💡 Features
            - ✨ Smart auto-formatting (lists/paragraphs)
            - 📦 Code in formatted boxes
            - 🖼️ Images in styled grids
            - 📊 Tables and structured data
            - 🎯 Context-aware responses
            """)
        
        with st.expander("⚙️ System Status"):
            st.code(f"""
Text:  {st.session_state.selected_text_model}
Vision: {st.session_state.selected_vision_model}
Fallback: {'On' if st.session_state.auto_fallback_enabled else 'Off'}
PDF: {'Loaded' if st.session_state.pdf_loaded else 'None'}
Images: {len(st.session_state.pdf_chat.image_handler.images) if st.session_state.pdf_loaded else 0}
            """, language="yaml")
    
    # Main chat area
    if not st.session_state.pdf_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 **Upload a PDF file to begin**")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class='info-box'>
            <h3>📤 Upload</h3>
            <p>Select your PDF and click Process</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='success-box'>
            <h3>💬 Ask</h3>
            <p>Type your questions naturally</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='warning-box'>
            <h3>🎯 Results</h3>
            <p>Get smart, formatted answers</p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        display_chat_history()
        
        user_input = st.chat_input(
            "💭 Ask anything about your PDF...", 
            disabled=st.session_state.is_generating
        )
        
        if user_input and not st.session_state.is_generating:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'query': user_input
            })
            
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                
                try:
                    query_lower = user_input.lower()
                    
                    # Handle image queries
                    if any(word in query_lower for word in ["image", "picture", "photo", "diagram", "figure"]):
                        response = st.session_state.pdf_chat.get_answer(user_input)
                        
                        if "show" in query_lower or "display" in query_lower or "list" in query_lower:
                            images = []
                            
                            if "page" in query_lower:
                                try:
                                    page_num = int(''.join(filter(str.isdigit, user_input)))
                                    images = st.session_state.pdf_chat.image_handler.get_images_by_page(page_num)
                                except:
                                    pass
                            elif "all" in query_lower:
                                images = st.session_state.pdf_chat.image_handler.images
                            
                            formatted_response = smart_format_response(response, user_input)
                            message_placeholder.markdown(formatted_response)
                            
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': response,
                                'query': user_input,
                                'images': images if images else []
                            })
                            
                            if images:
                                display_images_in_grid(images)
                        else:
                            formatted_response = smart_format_response(response if response else "✓ Processed", user_input)
                            message_placeholder.markdown(formatted_response)
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': response if response else "✓ Processed",
                                'query': user_input
                            })
                    else:
                        # Text query with streaming
                        st.session_state.is_generating = True
                        response = st.session_state.pdf_chat.get_answer(user_input)
                        
                        full_response = ""
                        for chunk in stream_text(response, delay=0.01):
                            full_response = chunk
                            message_placeholder.markdown(chunk + "▌")
                        
                        formatted_response = smart_format_response(full_response, user_input)
                        message_placeholder.markdown(formatted_response)
                        st.session_state.is_generating = False
                        
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': full_response,
                            'query': user_input
                        })
                
                except Exception as e:
                    error_msg = f"❌ **Error:** {str(e)}"
                    message_placeholder.markdown(error_msg)
                    st.session_state.is_generating = False
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': error_msg,
                        'query': user_input
                    })
            
            st.rerun()

if __name__ == "__main__":
    main()