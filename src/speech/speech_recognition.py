"""
Speech Recognition Module for Astra Voice Assistant
Uses Vosk for offline speech-to-text processing
"""

import pyaudio
import wave
import numpy as np
import logging
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import json
import webrtcvad
from vosk import Model, KaldiRecognizer
from ..config import config

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """Speech recognition using Vosk for offline processing"""
    
    def __init__(self):
        self.config = config
        self.model_path = Path("Voice/vosk-model-small-en-us-0.15")
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.is_processing = False
        
        # Audio configuration
        self.sample_rate = self.config.sample_rate
        self.chunk_size = self.config.chunk_size
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # VAD (Voice Activity Detection)
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        self.vad_frame_duration = 30  # ms
        
        # Audio buffers
        self.audio_buffer = queue.Queue()
        self.speech_buffer = []
        self.silence_frames = 0
        self.speech_frames = 0
        
        # Callbacks
        self.on_speech_detected = None
        self.on_speech_ended = None
        self.on_wake_word_detected = None
        self.on_error = None
        
        # Wake word detection
        self.wake_word = self.config.wake_word.lower()
        self.wake_word_confidence = 0.7
        
        # Initialize components
        self._initialize_model()
        self._initialize_audio()
    
    def _initialize_model(self):
        """Initialize Vosk model"""
        try:
            if self.model_path.exists():
                logger.info(f"Loading Vosk model from {self.model_path}")
                self.model = Model(str(self.model_path))
                self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
                logger.info("Vosk model loaded successfully")
            else:
                logger.error(f"Vosk model not found at {self.model_path}")
                raise FileNotFoundError(f"Vosk model not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Vosk model: {e}")
            raise
    
    def _initialize_audio(self):
        """Initialize PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("PyAudio initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            raise
    
    def start_listening(self, 
                       on_speech_detected: Callable = None,
                       on_speech_ended: Callable = None,
                       on_wake_word_detected: Callable = None,
                       on_error: Callable = None):
        """Start listening for speech input"""
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        # Set callbacks
        self.on_speech_detected = on_speech_detected
        self.on_speech_ended = on_speech_ended
        self.on_wake_word_detected = on_wake_word_detected
        self.on_error = on_error
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_listening = True
            self.stream.start_stream()
            logger.info("Started listening for speech input")
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            if self.on_error:
                self.on_error(str(e))
    
    def stop_listening(self):
        """Stop listening for speech input"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        logger.info("Stopped listening for speech input")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback for processing incoming audio data"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Check for voice activity
            is_speech = self._detect_voice_activity(audio_data)
            
            if is_speech:
                self.speech_frames += 1
                self.silence_frames = 0
                self.speech_buffer.extend(audio_data)
                
                # Notify speech detected
                if self.on_speech_detected and self.speech_frames == 1:
                    self.on_speech_detected()
            else:
                self.silence_frames += 1
                
                # Check if speech has ended
                if (self.speech_frames > 0 and 
                    self.silence_frames > self.sample_rate * 0.5):  # 0.5 seconds of silence
                    self._process_speech_buffer()
            
            return (in_data, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
            if self.on_error:
                self.on_error(str(e))
            return (in_data, pyaudio.paContinue)
    
    def _detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect voice activity in audio data"""
        try:
            # Convert to bytes for VAD
            audio_bytes = audio_data.tobytes()
            
            # Check if frame is speech
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            return is_speech
            
        except Exception as e:
            logger.error(f"Error in voice activity detection: {e}")
            return False
    
    def _process_speech_buffer(self):
        """Process the accumulated speech buffer"""
        if not self.speech_buffer or self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            # Convert speech buffer to bytes
            audio_bytes = np.array(self.speech_buffer, dtype=np.int16).tobytes()
            
            # Process with Vosk
            if self.recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                confidence = result.get("confidence", 0.0)
                
                if text:
                    logger.info(f"Recognized: '{text}' (confidence: {confidence:.2f})")
                    
                    # Check for wake word
                    if self._is_wake_word(text, confidence):
                        if self.on_wake_word_detected:
                            self.on_wake_word_detected(text)
                    else:
                        # Process as regular speech
                        if self.on_speech_ended:
                            self.on_speech_ended(text, confidence)
            
            # Clear speech buffer
            self.speech_buffer = []
            self.speech_frames = 0
            self.silence_frames = 0
            
        except Exception as e:
            logger.error(f"Error processing speech buffer: {e}")
            if self.on_error:
                self.on_error(str(e))
        finally:
            self.is_processing = False
    
    def _is_wake_word(self, text: str, confidence: float) -> bool:
        """Check if the recognized text contains the wake word"""
        text_lower = text.lower()
        
        # Check for exact wake word match
        if self.wake_word in text_lower and confidence >= self.wake_word_confidence:
            return True
        
        # Check for variations
        wake_word_variations = [
            self.wake_word,
            f"hey {self.wake_word}",
            f"hello {self.wake_word}",
            f"hi {self.wake_word}",
            f"{self.wake_word}?",
            f"{self.wake_word}!"
        ]
        
        for variation in wake_word_variations:
            if variation in text_lower and confidence >= self.wake_word_confidence:
                return True
        
        return False
    
    def recognize_audio_file(self, audio_file_path: str) -> Optional[str]:
        """Recognize speech from an audio file"""
        try:
            with wave.open(audio_file_path, 'rb') as wf:
                # Read audio data
                audio_data = wf.readframes(wf.getnframes())
                
                # Process with Vosk
                if self.recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.recognizer.Result())
                    return result.get("text", "").strip()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error recognizing audio file: {e}")
            return None
    
    def get_audio_devices(self) -> Dict[int, str]:
        """Get available audio input devices"""
        devices = {}
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices[i] = device_info['name']
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
        return devices
    
    def set_audio_device(self, device_index: int):
        """Set the audio input device"""
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            if device_info['maxInputChannels'] > 0:
                # Reinitialize stream with new device
                if self.stream:
                    self.stop_listening()
                
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._audio_callback
                )
                
                if self.is_listening:
                    self.stream.start_stream()
                
                logger.info(f"Set audio device to: {device_info['name']}")
            else:
                logger.error(f"Device {device_index} is not an input device")
        except Exception as e:
            logger.error(f"Error setting audio device: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        logger.info("Speech recognizer cleaned up")

# Global speech recognizer instance
speech_recognizer = SpeechRecognizer() 