import os
import base64
import requests
from PIL import Image
import fitz
from src.config import VISION_MODEL, VISION_MODEL_FALLBACK, AUTO_FALLBACK
from src.utils import setup_logging, save_metadata, load_metadata

logger = setup_logging()

class ImageHandler:
    def __init__(self, metadata_file="data/extracted_images/metadata.json"):
        self.metadata_file = metadata_file
        self.images = self.load_images()

    def extract_images_from_pdf(self, pdf_path, output_dir="data/extracted_images"):
        """
        Extract all images from PDF and save them to output directory.
        Returns list of image paths with metadata.
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
            logger.info(f"Extracted {image_count} images from PDF")
            self.images = image_paths
            self.save_images()
            return image_paths
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return []

    def analyze_image_with_ollama(self, image_path, question=None):
        """
        Analyze an image using Ollama's vision model.
        """
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
                    result = response.json()
                    return result.get("response", "No response from vision model")
                else:
                    raise Exception(f"Vision model returned status {response.status_code}")
                    
            except Exception as primary_error:
                # Try fallback model if auto-fallback is enabled
                if AUTO_FALLBACK:
                    logger.warning(f"Primary model failed, trying {VISION_MODEL_FALLBACK}...")
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

    def save_images(self):
        """
        Save image metadata to JSON.
        """
        save_metadata(self.images, self.metadata_file)

    def load_images(self):
        """
        Load image metadata from JSON.
        """
        return load_metadata(self.metadata_file)

    def display_images_info(self, page_filter=None):
        """
        Display information about extracted images.
        """
        if not self.images:
            logger.info("No images found in this PDF.")
            return
        
        filtered_images = self.images
        if page_filter:
            filtered_images = [img for img in self.images if img['page'] == page_filter]
            if not filtered_images:
                logger.info(f"No images found on page {page_filter}.")
                return
        
        logger.info(f"Found {len(filtered_images)} image(s):")
        for img_info in filtered_images:
            logger.info(f"  {img_info['index']}. {img_info['filename']} - Page {img_info['page']}")
            logger.info(f"     Format: {img_info['format']} | Size: {img_info['width']}x{img_info['height']}px")
            logger.info(f"     Path: {img_info['path']}")

    def open_image(self, image_index, analyze=False):
        """
        Open image by index and optionally analyze it.
        """
        if not self.images:
            logger.error("No images available.")
            return None
        
        if image_index < 1 or image_index > len(self.images):
            logger.error(f"Invalid image index. Please choose between 1 and {len(self.images)}")
            return None
        
        img_info = self.images[image_index - 1]
        try:
            img = Image.open(img_info['path'])
            img.show()
            logger.info(f"Opened: {img_info['filename']} (Page {img_info['page']})")
            
            if analyze:
                logger.info("Analyzing image content...")
                description = self.analyze_image_with_ollama(img_info['path'])
                logger.info(f"Image Analysis:\n{description}")
                return description
            
            return img_info
            
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            return None

    def get_images_by_page(self, page_num):
        """
        Get all images from a specific page.
        """
        return [img for img in self.images if img['page'] == page_num]

    def search_images_by_topic(self, topic):
        """
        Search for images related to a topic by analyzing their content.
        """
        if not self.images:
            return []
        
        logger.info(f"Searching for images related to: {topic}")
        relevant_images = []
        
        for img_info in self.images:
            # Analyze each image with the topic as context
            question = f"Does this image relate to {topic}? Answer yes or no, then briefly explain why."
            analysis = self.analyze_image_with_ollama(img_info['path'], question)
            
            # Check if the response indicates relevance
            if "yes" in analysis.lower()[:50]:  # Check beginning of response
                relevant_images.append({
                    "info": img_info,
                    "analysis": analysis
                })
        
        return relevant_images