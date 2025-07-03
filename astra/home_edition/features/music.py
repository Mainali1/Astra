import pygame
import os

# Initialize the pygame mixer
pygame.mixer.init()

def play_music(file_path: str) -> str:
    """
    Plays a music file using pygame.

    Args:
        file_path: The absolute path to the music file.

    Returns:
        A message indicating the status of the music playback.
    """
    if not os.path.isabs(file_path):
        return "Error: Please provide an absolute file path."

    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        return f"Playing: {os.path.basename(file_path)}"
    except pygame.error as e:
        return f"Error playing music: {e}"

def stop_music() -> str:
    """
    Stops the currently playing music.
    """
    pygame.mixer.music.stop()
    return "Music stopped."

def pause_music() -> str:
    """
    Pauses the currently playing music.
    """
    pygame.mixer.music.pause()
    return "Music paused."

def unpause_music() -> str:
    """
    Unpauses the currently playing music.
    """
    pygame.mixer.music.unpause()
    return "Music unpaused."