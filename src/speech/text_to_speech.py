"""
Astra AI Assistant - Text-to-Speech Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import sounddevice as sd
import soundfile as sf
from src.config import Config

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Handles text-to-speech using Piper."""
    
    def __init__(self, config: Config):
        """Initialize the TTS system."""
        self.config = config
        self.voice = config.TTS_VOICE
        self.model_path = Path(config.MODELS_DIR) / "piper"
        self.piper_path = "piper"  # Assumes piper is in PATH
        self.is_speaking = False
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Piper model."""
        try:
            model_dir = self.model_path
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if model exists
            model_file = model_dir / f"{self.voice}.onnx"
            if not model_file.exists():
                logger.info(f"Downloading Piper model for voice {self.voice}...")
                # TODO: Implement model download
                pass
                
            logger.info("Piper model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Piper model: {str(e)}")
            raise
    
    async def speak(self, text: str, wait: bool = True) -> bool:
        """Convert text to speech and play it."""
        if self.is_speaking:
            logger.warning("Already speaking, please wait")
            return False
            
        try:
            self.is_speaking = True
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using Piper
            cmd = [
                self.piper_path,
                "--model", str(self.model_path / f"{self.voice}.onnx"),
                "--output_file", temp_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send text to Piper
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                logger.error(f"Piper error: {stderr}")
                return False
            
            # Play the generated audio
            data, samplerate = sf.read(temp_path)
            sd.play(data, samplerate)
            
            if wait:
                sd.wait()
            
            # Clean up
            Path(temp_path).unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return False
            
        finally:
            self.is_speaking = False
    
    async def stop_speaking(self):
        """Stop current speech output."""
        if self.is_speaking:
            sd.stop()
            self.is_speaking = False
    
    async def cleanup(self):
        """Clean up resources."""
        await self.stop_speaking() 