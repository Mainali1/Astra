import time
import threading
from typing import Dict, Optional

class Timer:
    """
    A robust timer class that supports multiple concurrent timers.
    """
    _timers: Dict[str, threading.Timer] = {}
    _timer_callbacks: Dict[str, callable] = {}

    def start_timer(self, name: str, duration_seconds: int, callback: callable) -> str:
        """
        Starts a new timer.

        Args:
            name: A unique name for the timer.
            duration_seconds: The duration of the timer in seconds.
            callback: A callable function to execute when the timer finishes.

        Returns:
            A message indicating the status of the timer.
        """
        if name in self._timers and self._timers[name].is_alive():
            return f"Error: Timer '{name}' is already running."

        if duration_seconds <= 0:
            return "Error: Timer duration must be positive."

        def timer_finished():
            del self._timers[name]
            del self._timer_callbacks[name]
            callback(name) # Execute the callback function

        timer_thread = threading.Timer(duration_seconds, timer_finished)
        self._timers[name] = timer_thread
        self._timer_callbacks[name] = callback
        timer_thread.start()
        return f"Timer '{name}' started for {duration_seconds} seconds."

    def stop_timer(self, name: str) -> str:
        """
        Stops a running timer.

        Args:
            name: The name of the timer to stop.

        Returns:
            A message indicating the status of the timer.
        """
        if name in self._timers and self._timers[name].is_alive():
            self._timers[name].cancel()
            del self._timers[name]
            del self._timer_callbacks[name]
            return f"Timer '{name}' stopped."
        return f"Error: Timer '{name}' is not running."

    def get_timer_status(self, name: str) -> str:
        """
        Gets the status of a timer.

        Args:
            name: The name of the timer.

        Returns:
            A message indicating the timer's status.
        """
        if name in self._timers:
            if self._timers[name].is_alive():
                return f"Timer '{name}' is running."
            else:
                return f"Timer '{name}' has finished."
        return f"Timer '{name}' not found."

    def list_active_timers(self) -> list[str]:
        """
        Lists all active timers.

        Returns:
            A list of names of active timers.
        """
        active_timers = [name for name, timer_thread in self._timers.items() if timer_thread.is_alive()]
        return active_timers

timer_manager = Timer()