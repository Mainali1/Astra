"""
Astra AI Assistant - Speech Recognition Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import json
import logging
import queue
import sounddevice as sd
import vosk
from typing import Optional
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Handles speech recognition using Vosk."""

    def __init__(self, config: Config):
        """Initialize the speech recognizer."""
        self.config = config
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False

        # Audio settings
        self.sample_rate = 16000
        self.block_size = 8000

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Vosk model."""
        try:
            model_path = Path(self.config.MODELS_DIR) / "vosk-model-small-en-us"

            if not model_path.exists():
                logger.info("Downloading Vosk model...")
                # TODO: Implement model download

            self.model = vosk.Model(str(model_path))
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            logger.info("Vosk model initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Vosk model: {str(e)}")
            raise

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input."""
        if status:
            logger.warning(f"Audio input status: {status}")
        if self.is_listening:
            self.audio_queue.put(bytes(indata))

    async def start_listening(self):
        """Start listening for audio input."""
        if self.is_listening:
            return

        self.is_listening = True

        try:
            # Start audio stream
            stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                dtype="int16",
                channels=1,
                callback=self._audio_callback,
            )

            with stream:
                logger.info("Started listening for audio input")
                while self.is_listening:
                    # Process audio data
                    if not self.audio_queue.empty():
                        data = self.audio_queue.get()
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            if result.get("text"):
                                yield result["text"]

        except Exception as e:
            logger.error(f"Error in audio processing: {str(e)}")
            self.is_listening = False

    async def stop_listening(self):
        """Stop listening for audio input."""
        self.is_listening = False
        logger.info("Stopped listening for audio input")

    async def transcribe_file(self, audio_file: Path) -> Optional[str]:
        """Transcribe an audio file."""
        try:
            # TODO: Implement file transcription
            pass
        except Exception as e:
            logger.error(f"Error transcribing file: {str(e)}")
            return None

    async def cleanup(self):
        """Clean up resources."""
        await self.stop_listening()
        self.model = None
        self.recognizer = None
