"""
Home Edition Features Module

All personal productivity tools and day-to-day life features for Home Edition.
Each feature is in its own module for modularity and easy enable/disable.
"""

from .calculator import CalculatorFeature
from .timer import TimerFeature
from .reminder import ReminderFeature
from .notes import NotesFeature
from .weather import WeatherFeature
from .currency import CurrencyFeature
from .web_search import WebSearchFeature
from .dictionary import DictionaryFeature
from .file_manager import FileManagerFeature
from .system_monitor import SystemMonitorFeature
from .ocr import OCRFeature
from .news import NewsFeature
from .translator import TranslatorFeature
from .image_generator import ImageGeneratorFeature
from .text_to_speech import TextToSpeechFeature
from .speech_to_text import SpeechToTextFeature
from .password_generator import PasswordGeneratorFeature
from .url_shortener import URLShortenerFeature
from .qr_code import QRCodeFeature
from .email_validator import EmailValidatorFeature

__all__ = [
    'CalculatorFeature',
    'TimerFeature', 
    'ReminderFeature',
    'NotesFeature',
    'WeatherFeature',
    'CurrencyFeature',
    'WebSearchFeature',
    'DictionaryFeature',
    'FileManagerFeature',
    'SystemMonitorFeature',
    'OCRFeature',
    'NewsFeature',
    'TranslatorFeature',
    'ImageGeneratorFeature',
    'TextToSpeechFeature',
    'SpeechToTextFeature',
    'PasswordGeneratorFeature',
    'URLShortenerFeature',
    'QRCodeFeature',
    'EmailValidatorFeature'
] 