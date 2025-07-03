from googletrans import Translator
from typing import Optional

def translate_text(text: str, dest_language: str = 'en', src_language: str = 'auto') -> Optional[str]:
    """
    Translates text from one language to another using Google Translate.

    Args:
        text: The text to translate.
        dest_language: The destination language code (e.g., 'en' for English, 'es' for Spanish).
        src_language: The source language code (e.g., 'fr' for French, 'auto' for auto-detect).

    Returns:
        The translated text, or None if an error occurs.
    """
    try:
        translator = Translator()
        translation = translator.translate(text, dest=dest_language, src=src_language)
        return translation.text
    except Exception as e:
        # Log the exception here in a real application
        print(f"Error during translation: {e}")
        return None