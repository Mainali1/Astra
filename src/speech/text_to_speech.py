"""
Text-to-Speech Module for Astra Voice Assistant
Uses Piper TTS for natural voice generation
"""

import subprocess
import tempfile
import os
import logging
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import json
import wave
import pyaudio
import numpy as np
from ..config import config

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Text-to-speech using Piper TTS"""
    
    def __init__(self):
        self.config = config
        self.voice_path = Path("Voice/en_US-amy-medium.onnx")
        self.voice_config_path = Path("Voice/en_US-amy-medium.onnx.json")
        self.audio = None
        self.stream = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        
        # Audio configuration
        self.sample_rate = 22050  # Piper default
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Voice settings
        self.voice = self.config.tts_voice
        self.speed = self.config.tts_speed
        self.pitch = self.config.tts_pitch
        
        # Callbacks
        self.on_speech_started = None
        self.on_speech_ended = None
        self.on_error = None
        
        # Initialize components
        self._initialize_audio()
        self._start_speech_thread()
    
    def _initialize_audio(self):
        """Initialize PyAudio for output"""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("PyAudio initialized for TTS")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio for TTS: {e}")
            raise
    
    def _start_speech_thread(self):
        """Start the speech processing thread"""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        logger.info("Speech processing thread started")
    
    def _speech_worker(self):
        """Worker thread for processing speech queue"""
        while True:
            try:
                # Get next speech item from queue
                speech_item = self.speech_queue.get()
                if speech_item is None:  # Shutdown signal
                    break
                
                text, callback = speech_item
                self._speak_text(text, callback)
                
            except Exception as e:
                logger.error(f"Error in speech worker: {e}")
                if self.on_error:
                    self.on_error(str(e))
    
    def speak(self, text: str, callback: Callable = None):
        """Add text to speech queue"""
        if not text.strip():
            return
        
        self.speech_queue.put((text, callback))
        logger.debug(f"Added to speech queue: '{text[:50]}...'")
    
    def speak_immediate(self, text: str, callback: Callable = None):
        """Speak text immediately (blocking)"""
        if not text.strip():
            return
        
        self._speak_text(text, callback)
    
    def _speak_text(self, text: str, callback: Callable = None):
        """Convert text to speech and play it"""
        try:
            # Notify speech started
            if self.on_speech_started:
                self.on_speech_started(text)
            
            self.is_speaking = True
            
            # Generate speech using Piper
            audio_data = self._generate_speech(text)
            
            if audio_data:
                # Play the audio
                self._play_audio(audio_data)
            
            # Notify speech ended
            if self.on_speech_ended:
                self.on_speech_ended(text)
            
            if callback:
                callback()
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            if self.on_error:
                self.on_error(str(e))
        finally:
            self.is_speaking = False
    
    def _generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech audio using Piper TTS"""
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_output = temp_file.name
            
            # Prepare Piper command
            cmd = [
                "piper",
                "--model", str(self.voice_path),
                "--config", str(self.voice_config_path),
                "--output_file", temp_output,
                "--output_raw"
            ]
            
            # Add voice settings
            if self.speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / self.speed)])
            
            if self.pitch != 1.0:
                cmd.extend(["--noise_scale", str(self.pitch)])
            
            # Run Piper
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
                logger.error(f"Piper TTS error: {stderr}")
                return None
            
            # Read generated audio
            with open(temp_output, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_output)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def _play_audio(self, audio_data: bytes):
        """Play audio data through speakers"""
        try:
            # Convert audio data to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            
            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_array), chunk_size):
                chunk = audio_array[i:i + chunk_size]
                if len(chunk) < chunk_size:
                    # Pad last chunk if necessary
                    chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')
                
                self.stream.write(chunk.tobytes())
            
            # Close stream
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            if self.stream:
                self.stream.close()
                self.stream = None
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.is_speaking and self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.is_speaking = False
            logger.info("Speech stopped")
    
    def clear_queue(self):
        """Clear the speech queue"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        logger.info("Speech queue cleared")
    
    def set_voice_settings(self, speed: float = None, pitch: float = None):
        """Update voice settings"""
        if speed is not None:
            self.speed = max(0.5, min(2.0, speed))  # Clamp between 0.5 and 2.0
        if pitch is not None:
            self.pitch = max(0.5, min(2.0, pitch))  # Clamp between 0.5 and 2.0
        
        logger.info(f"Voice settings updated: speed={self.speed}, pitch={self.pitch}")
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available Piper voices"""
        voices = {}
        voice_dir = Path("Voice")
        
        if voice_dir.exists():
            for voice_file in voice_dir.glob("*.onnx"):
                voice_name = voice_file.stem
                config_file = voice_file.with_suffix(".onnx.json")
                if config_file.exists():
                    voices[voice_name] = str(voice_file)
        
        return voices
    
    def set_voice(self, voice_name: str):
        """Set the voice to use"""
        voices = self.get_available_voices()
        if voice_name in voices:
            self.voice_path = Path(voices[voice_name])
            self.voice_config_path = self.voice_path.with_suffix(".onnx.json")
            self.voice = voice_name
            logger.info(f"Voice set to: {voice_name}")
        else:
            logger.warning(f"Voice not found: {voice_name}")
    
    def speak_file(self, file_path: str, callback: Callable = None):
        """Speak text from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.speak(text, callback)
        except Exception as e:
            logger.error(f"Error reading file for speech: {e}")
    
    def get_speech_status(self) -> Dict[str, Any]:
        """Get current speech status"""
        return {
            "is_speaking": self.is_speaking,
            "queue_size": self.speech_queue.qsize(),
            "voice": self.voice,
            "speed": self.speed,
            "pitch": self.pitch
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_speaking()
        self.clear_queue()
        
        # Send shutdown signal to speech thread
        self.speech_queue.put(None)
        
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        logger.info("Text-to-speech cleaned up")

# Global TTS instance
tts = TextToSpeech() 