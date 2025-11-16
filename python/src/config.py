# src/config.py

# ========================================
# TEXT PROCESSING
# ========================================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# ========================================
# TEXT MODEL (for conversations & Q&A)
# ========================================
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/v1/completions"

# ========================================
# VISION MODEL (for image analysis)
# ========================================
# Primary vision model
VISION_MODEL = "llava-phi3"  # Best for RTX 3050 4GB

# Fallback vision model (if primary fails due to VRAM)
VISION_MODEL_FALLBACK = "moondream"

# Vision model options and their VRAM requirements
AVAILABLE_VISION_MODELS = {
    "llava-phi3": {
        "vram": "~2.5GB",
        "quality": "High",
        "speed": "Fast",
        "recommended_for": "RTX 3050 4GB"
    },
    "moondream": {
        "vram": "~1.7GB", 
        "quality": "Good",
        "speed": "Very Fast",
        "recommended_for": "Low VRAM or backup"
    },
    "llava:7b": {
        "vram": "~3.5GB",
        "quality": "Very High", 
        "speed": "Medium",
        "recommended_for": "If other apps closed"
    }
}

# ========================================
# MODEL SWITCHING
# ========================================
AUTO_FALLBACK = True  # Automatically switch to fallback if primary fails