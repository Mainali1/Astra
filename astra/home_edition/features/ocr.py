import requests
import os
from typing import Optional, Dict, Any

from astra.core.config import settings

OCRSPACE_API_URL = "https://api.ocr.space/parse/image"

def ocr_image(image_path: str, language: str = 'eng') -> Optional[Dict[str, Any]]:
    """
    Performs OCR on an image using the OCR.Space API.

    Args:
        image_path: The absolute path to the image file.
        language: The language of the text in the image (e.g., 'eng' for English).

    Returns:
        A dictionary containing the OCR result, or None if an error occurs.
    """
    api_key = settings.ocrspace_api_key # Assuming ocrspace_api_key is used for OCR.Space
    if not api_key:
        return {"error": "OCR.Space API key is not configured. Please set OCRSPACE_API_KEY in your .env file."}

    if not os.path.isabs(image_path):
        return {"error": "Image path must be absolute."}

    if not os.path.exists(image_path):
        return {"error": f"Image file not found at {image_path}"}

    # OCR.Space free tier limit is 1MB
    if os.path.getsize(image_path) > 1 * 1024 * 1024:
        return {"error": "Image file size exceeds 1MB limit for free tier."}

    headers = {
        "apikey": api_key,
    }

    with open(image_path, 'rb') as f:
        files = {'filename': f}
        data = {
            'language': language,
            'isOverlayRequired': 'true'
        }
        try:
            response = requests.post(OCRSPACE_API_URL, headers=headers, files=files, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            # Log the exception here in a real application
            print(f"Error during OCR: {e}")
            return {"error": f"Failed to perform OCR: {e}"}