"""
Astra AI Assistant - Music Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import pygame.mixer
import mutagen
from src.config import Config

logger = logging.getLogger(__name__)


class MusicPlayer:
    """Handles music playback functionality."""

    def __init__(self):
        """Initialize the music player."""
        pygame.mixer.init()
        self.current_file: Optional[str] = None
        self.is_playing = False
        self.volume = 1.0  # Range 0.0 to 1.0
        self.supported_formats: Set[str] = {".mp3", ".wav", ".ogg"}

    def play(self, file_path: str) -> bool:
        """Play an audio file."""
        try:
            if not Path(file_path).exists():
                return False

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.current_file = file_path
            self.is_playing = True
            return True

        except Exception as e:
            logger.error(f"Error playing music: {str(e)}")
            return False

    def pause(self):
        """Pause playback."""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def resume(self):
        """Resume playback."""
        if not self.is_playing and self.current_file:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_file = None

    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def get_metadata(self, file_path: str) -> Dict[str, str]:
        """Get audio file metadata."""
        try:
            audio = mutagen.File(file_path)
            if audio:
                metadata = {}
                # Handle different metadata formats
                if hasattr(audio, "tags"):
                    tags = audio.tags
                    if hasattr(tags, "getall"):  # ID3 tags
                        metadata["title"] = str(tags.getall("TIT2")[0]) if tags.getall("TIT2") else ""
                        metadata["artist"] = str(tags.getall("TPE1")[0]) if tags.getall("TPE1") else ""
                        metadata["album"] = str(tags.getall("TALB")[0]) if tags.getall("TALB") else ""
                    else:  # Other tag formats
                        metadata["title"] = str(tags.get("title", [""])[0])
                        metadata["artist"] = str(tags.get("artist", [""])[0])
                        metadata["album"] = str(tags.get("album", [""])[0])
                return metadata
            return {}
        except Exception as e:
            logger.error(f"Error reading metadata: {str(e)}")
            return {}

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        pygame.mixer.quit()


class MusicFeature:
    """Music feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the music feature."""
        self.config = config
        self.player = MusicPlayer()
        self.music_dir = Path(config.DATA_DIR) / "music"
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.playlist: List[str] = []
        self.current_index = -1

    def scan_music_directory(self) -> List[Dict[str, Any]]:
        """Scan music directory for audio files."""
        music_files = []
        for ext in self.player.supported_formats:
            music_files.extend(self.music_dir.glob(f"*{ext}"))

        results = []
        for file_path in music_files:
            metadata = self.player.get_metadata(str(file_path))
            results.append(
                {
                    "path": str(file_path),
                    "filename": file_path.name,
                    "title": metadata.get("title", file_path.stem),
                    "artist": metadata.get("artist", "Unknown"),
                    "album": metadata.get("album", "Unknown"),
                }
            )

        return sorted(results, key=lambda x: x["title"].lower())

    def _format_song_info(self, song: Dict[str, Any]) -> str:
        """Format song information for display."""
        return f"Title: {song['title']}\n" f"Artist: {song['artist']}\n" f"Album: {song['album']}"

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle music-related intents."""
        try:
            action = intent.get("action", "")
            params = intent.get("parameters", {})

            if action == "play_music":
                # Play specific song or first in directory
                query = params.get("song", "").lower()

                # Scan music directory
                available_songs = self.scan_music_directory()
                if not available_songs:
                    return "No music files found in the music directory."

                if query:
                    # Search for specific song
                    matches = [
                        song
                        for song in available_songs
                        if query in song["title"].lower()
                        or query in song["artist"].lower()
                        or query in song["album"].lower()
                    ]

                    if not matches:
                        return f"No songs found matching '{query}'."

                    song = matches[0]
                else:
                    # Play first available song
                    song = available_songs[0]

                if self.player.play(song["path"]):
                    return f"Now playing:\n{self._format_song_info(song)}"
                return "Sorry, I couldn't play that song."

            elif action == "pause_music":
                # Pause playback
                self.player.pause()
                return "Music paused."

            elif action == "resume_music":
                # Resume playback
                self.player.resume()
                return "Music resumed."

            elif action == "stop_music":
                # Stop playback
                self.player.stop()
                return "Music stopped."

            elif action == "set_volume":
                # Set volume
                volume = float(params.get("volume", 1.0))
                self.player.set_volume(volume)
                return f"Volume set to {int(volume * 100)}%"

            elif action == "list_music":
                # List available music
                songs = self.scan_music_directory()
                if not songs:
                    return "No music files found in the music directory."

                response = "Available music:\n\n"
                for i, song in enumerate(songs, 1):
                    response += f"{i}. {song['title']} - {song['artist']}\n"
                return response

            else:
                return "I'm not sure what you want to do with the music player."

        except Exception as e:
            logger.error(f"Error handling music request: {str(e)}")
            return "I'm sorry, but I encountered an error with the music player."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Music feature is always available for local playback

    async def cleanup(self):
        """Clean up resources."""
        self.player.cleanup()
