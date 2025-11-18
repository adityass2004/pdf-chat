import requests
from src.config import OLLAMA_MODEL,VISION_MODEL, VISION_MODEL_FALLBACK, AUTO_FALLBACK
from src.utils import setup_logging

logger = setup_logging()

class ModelManager:
    def __init__(self):
        self.current_vision_model = None

    def list_available_models(self):
        """
        List all available Ollama models.
        """
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                logger.info("\nAvailable Models:")
                logger.info("\nText Models:")
                for model in models:
                    name = model.get("name", "")
                    if "llava" not in name.lower() and "moondream" not in name.lower():
                        size = model.get("size", 0) / (1024**3)  # Convert to GB
                        logger.info(f"  • {name} ({size:.1f}GB)")
                
                logger.info("\nVision Models:")
                for model in models:
                    name = model.get("name", "")
                    if "llava" in name.lower() or "moondream" in name.lower():
                        size = model.get("size", 0) / (1024**3)
                        logger.info(f"  • {name} ({size:.1f}GB)")
                
                return True
            else:
                logger.error("Could not fetch models from Ollama")
                return False
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return False

    def show_current_config(self):
        """
        Display current model configuration.
        """
        logger.info("\nCurrent Configuration:")
        logger.info(f"  Text Model: {OLLAMA_MODEL}")
        logger.info(f"  Vision Model: {VISION_MODEL}")
        logger.info(f"  Fallback Model: {VISION_MODEL_FALLBACK}")
        logger.info(f"  Auto-Fallback: {'Enabled' if AUTO_FALLBACK else 'Disabled'}")
        if self.current_vision_model:
            logger.info(f"  Last Used Vision Model: {self.current_vision_model}")

    def switch_vision_model(self, model_name):
        """
        Switch the active vision model.
        """
        # Check if model exists
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check if model is available
                if not any(model_name in name for name in model_names):
                    logger.error(f"Model '{model_name}' not found.")
                    logger.info(f"Download it with: ollama pull {model_name}")
                    return False
                
                # Update config (assuming config.py allows dynamic changes)
                from src.config import VISION_MODEL
                VISION_MODEL = model_name  # Note: This modifies the imported var; consider making config a class
                logger.info(f"Switched to vision model: {model_name}")
                return True
            else:
                logger.error("Could not verify model availability")
                return False
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            return False