import logging
import json
import os

def setup_logging(log_file="logs/chat.log"):
    """
    Set up logging to a file with timestamps.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)

def save_metadata(data, file_path):
    """
    Save data (e.g., image metadata) to a JSON file.
    """
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        logger = logging.getLogger(__name__)
        logger.info(f"Metadata saved to {file_path}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving metadata: {e}")

def load_metadata(file_path):
    """
    Load data from a JSON file, or return empty dict if not found.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading metadata: {e}")
    return {}