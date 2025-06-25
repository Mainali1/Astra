"""
Music Player Feature for Astra Voice Assistant
Provides music playback using free APIs and local file support
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os
import subprocess
import platform
import hashlib

# Feature information
FEATURE_INFO = {
    'name': 'music',
    'description': 'Play music from local files and streaming services using free APIs',
    'category': 'entertainment',
    'keywords': ['music', 'play', 'song', 'artist', 'album', 'playlist', 'spotify', 'youtube'],
    'examples': [
        'Play some music',
        'Play Bohemian Rhapsody',
        'Play music by Queen',
        'Play my playlist',
        'Stop the music',
        'Pause music',
        'Next song',
        'Previous song'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class MusicPlayer:
    """Music player with multiple API integrations and local file support"""
    
    def __init__(self):
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', '')
        self.cache_file = Path("data/music_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
        # Music directories
        self.music_dirs = [
            Path.home() / "Music",
            Path.home() / "Downloads" / "Music",
            Path.cwd() / "music"
        ]
        
        # Supported audio formats
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']
        
        # Current playback state
        self.current_track = None
        self.is_playing = False
        self.volume = 50
        self.playlist = []
        self.current_index = 0
        
        # Load cache
        self.cache = self._load_cache()
        
        # Initialize platform-specific player
        self._init_player()
    
    def _init_player(self):
        """Initialize platform-specific audio player"""
        system = platform.system().lower()
        
        if system == 'windows':
            self.player_cmd = 'start'
            self.player_args = ['/min', 'wmplayer']
        elif system == 'darwin':  # macOS
            self.player_cmd = 'afplay'
            self.player_args = []
        else:  # Linux
            self.player_cmd = 'mpv'
            self.player_args = ['--no-video', '--volume=50']
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load music cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Remove expired entries
                    current_time = datetime.now()
                    expired_keys = []
                    for key, data in cache.items():
                        if 'timestamp' in data:
                            cache_time = datetime.fromisoformat(data['timestamp'])
                            if current_time - cache_time > self.cache_duration:
                                expired_keys.append(key)
                    
                    for key in expired_keys:
                        del cache[key]
                    
                    return cache
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save music cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving music cache: {e}")
    
    def _get_cached_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Get search results from cache"""
        cache_key = f"search_{hashlib.md5(query.encode()).hexdigest()}"
        if cache_key in self.cache:
            data = self.cache[cache_key]
            if 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.cache_duration:
                    return data.get('results')
        return None
    
    def _cache_search(self, query: str, results: Dict[str, Any]):
        """Cache search results"""
        cache_key = f"search_{hashlib.md5(query.encode()).hexdigest()}"
        self.cache[cache_key] = {
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _search_local_files(self, query: str) -> List[Dict[str, Any]]:
        """Search for music files in local directories"""
        results = []
        query_lower = query.lower()
        
        for music_dir in self.music_dirs:
            if not music_dir.exists():
                continue
            
            for file_path in music_dir.rglob('*'):
                if file_path.suffix.lower() in self.supported_formats:
                    filename = file_path.stem.lower()
                    if query_lower in filename:
                        results.append({
                            'title': file_path.stem,
                            'artist': 'Unknown',
                            'album': 'Unknown',
                            'duration': 0,
                            'url': str(file_path),
                            'source': 'local',
                            'type': 'file'
                        })
        
        return results[:10]  # Limit to 10 results
    
    def _search_spotify(self, query: str) -> List[Dict[str, Any]]:
        """Search for music on Spotify"""
        if not self.spotify_client_id or not self.spotify_client_secret:
            return []
        
        try:
            # Get access token
            token_url = "https://accounts.spotify.com/api/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.spotify_client_id,
                'client_secret': self.spotify_client_secret
            }
            
            token_response = requests.post(token_url, data=token_data, timeout=10)
            token_response.raise_for_status()
            token_info = token_response.json()
            access_token = token_info['access_token']
            
            # Search for tracks
            search_url = "https://api.spotify.com/v1/search"
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'q': query,
                'type': 'track',
                'limit': 10
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])
            
            results = []
            for track in tracks:
                results.append({
                    'title': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,  # Convert to seconds
                    'url': track['external_urls']['spotify'],
                    'source': 'spotify',
                    'type': 'stream',
                    'spotify_id': track['id']
                })
            
            return results
            
        except requests.RequestException as e:
            print(f"Spotify API error: {e}")
            return []
    
    def _search_youtube(self, query: str) -> List[Dict[str, Any]]:
        """Search for music on YouTube"""
        if not self.youtube_api_key:
            return []
        
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'key': self.youtube_api_key,
                'q': f"{query} music",
                'part': 'snippet',
                'type': 'video',
                'maxResults': 10,
                'videoCategoryId': '10'  # Music category
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = data.get('items', [])
            
            results = []
            for video in videos:
                snippet = video['snippet']
                results.append({
                    'title': snippet['title'],
                    'artist': snippet['channelTitle'],
                    'album': 'YouTube',
                    'duration': 0,
                    'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    'source': 'youtube',
                    'type': 'stream',
                    'youtube_id': video['id']['videoId']
                })
            
            return results
            
        except requests.RequestException as e:
            print(f"YouTube API error: {e}")
            return []
    
    def search_music(self, query: str) -> Dict[str, Any]:
        """Search for music across all sources"""
        if not query.strip():
            return {
                'success': False,
                'error': 'No search query provided'
            }
        
        # Check cache first
        cached_results = self._get_cached_search(query)
        if cached_results:
            return {
                'success': True,
                'results': cached_results,
                'source': 'cache'
            }
        
        # Search all sources
        local_results = self._search_local_files(query)
        spotify_results = self._search_spotify(query)
        youtube_results = self._search_youtube(query)
        
        # Combine and sort results
        all_results = local_results + spotify_results + youtube_results
        
        # Cache results
        self._cache_search(query, all_results)
        
        return {
            'success': True,
            'results': all_results,
            'source': 'api',
            'local_count': len(local_results),
            'spotify_count': len(spotify_results),
            'youtube_count': len(youtube_results)
        }
    
    def play_track(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """Play a specific track"""
        try:
            if track_info['type'] == 'file':
                # Play local file
                file_path = track_info['url']
                if platform.system().lower() == 'windows':
                    subprocess.Popen(['start', file_path], shell=True)
                elif platform.system().lower() == 'darwin':
                    subprocess.Popen(['afplay', file_path])
                else:
                    subprocess.Popen(['mpv', '--no-video', file_path])
                
                self.current_track = track_info
                self.is_playing = True
                
                return {
                    'success': True,
                    'message': f"Playing {track_info['title']} by {track_info['artist']}",
                    'track': track_info
                }
            
            elif track_info['type'] == 'stream':
                # For streaming, we'll return the URL for the client to handle
                return {
                    'success': True,
                    'message': f"Streaming {track_info['title']} by {track_info['artist']}",
                    'track': track_info,
                    'stream_url': track_info['url']
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error playing track: {str(e)}"
            }
    
    def play_music(self, query: str) -> Dict[str, Any]:
        """Play music based on query"""
        # Search for music
        search_result = self.search_music(query)
        
        if not search_result.get('success'):
            return search_result
        
        results = search_result.get('results', [])
        if not results:
            return {
                'success': False,
                'error': f"No music found for '{query}'"
            }
        
        # Play the first result
        return self.play_track(results[0])
    
    def stop_music(self) -> Dict[str, Any]:
        """Stop current music playback"""
        try:
            # Kill any running music processes
            if platform.system().lower() == 'windows':
                subprocess.run(['taskkill', '/f', '/im', 'wmplayer.exe'], 
                             capture_output=True, shell=True)
            elif platform.system().lower() == 'darwin':
                subprocess.run(['pkill', 'afplay'], capture_output=True)
            else:
                subprocess.run(['pkill', 'mpv'], capture_output=True)
            
            self.is_playing = False
            self.current_track = None
            
            return {
                'success': True,
                'message': 'Music stopped'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error stopping music: {str(e)}"
            }
    
    def pause_music(self) -> Dict[str, Any]:
        """Pause current music playback"""
        # For simplicity, we'll just stop the music
        # In a full implementation, you'd want to pause/resume functionality
        return self.stop_music()
    
    def get_playlist(self) -> Dict[str, Any]:
        """Get current playlist"""
        return {
            'success': True,
            'playlist': self.playlist,
            'current_index': self.current_index,
            'is_playing': self.is_playing
        }
    
    def create_playlist(self, name: str, tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new playlist"""
        playlist = {
            'name': name,
            'tracks': tracks,
            'created_at': datetime.now().isoformat(),
            'duration': sum(track.get('duration', 0) for track in tracks)
        }
        
        # Save playlist to file
        playlist_file = Path(f"data/playlists/{name}.json")
        playlist_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(playlist_file, 'w', encoding='utf-8') as f:
                json.dump(playlist, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'message': f"Playlist '{name}' created with {len(tracks)} tracks",
                'playlist': playlist
            }
            
        except IOError as e:
            return {
                'success': False,
                'error': f"Error saving playlist: {str(e)}"
            }

def handle_music_command(text: str) -> Dict[str, Any]:
    """Handle music-related voice commands"""
    player = MusicPlayer()
    
    text_lower = text.lower()
    
    # Stop/pause commands
    if any(word in text_lower for word in ['stop', 'pause', 'halt']):
        return player.stop_music()
    
    # Play commands
    elif any(word in text_lower for word in ['play', 'start', 'begin']):
        # Extract what to play
        if 'music' in text_lower:
            # Generic music request
            return player.play_music('popular music')
        else:
            # Extract specific song/artist
            # Remove common words
            query = text_lower.replace('play', '').replace('start', '').replace('begin', '').strip()
            if query:
                return player.play_music(query)
            else:
                return player.play_music('popular music')
    
    # Search commands
    elif any(word in text_lower for word in ['search', 'find', 'look for']):
        query = text_lower.replace('search', '').replace('find', '').replace('look for', '').strip()
        if query:
            return player.search_music(query)
        else:
            return {
                'success': False,
                'error': 'Please specify what music to search for'
            }
    
    # Playlist commands
    elif 'playlist' in text_lower:
        return player.get_playlist()
    
    else:
        # Default to playing music
        return player.play_music('popular music')

# Export feature information
FEATURE_EXPORTS = {
    'handle_music_command': handle_music_command,
    'MusicPlayer': MusicPlayer,
    'FEATURE_INFO': FEATURE_INFO
} 