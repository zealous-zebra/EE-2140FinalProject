# File: shazamify/services/spotify_client.py
# Purpose: Client to interact with the Spotify Web API.

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import pathlib

class SpotifyClient:
    """Handles authentication and data fetching from the Spotify API."""
    def __init__(self):
        project_root = pathlib.Path(__file__).parent.parent.parent
        env_path = project_root / '.env'
        load_dotenv(env_path)

        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Spotify API credentials not found in .env file.")

        try:
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"Error initializing Spotify client: {e}")
            self.sp = None

    def get_song_details(self, song_title: str) -> dict:
        if not self.sp: return {"error": "Spotify client not initialized."}
        try:
            result = self.sp.search(q=song_title, type='track', limit=1)
            if not result['tracks']['items']:
                return {"error": f"No results found for '{song_title}'."}

            track = result['tracks']['items'][0]
            artist = track['artists'][0]
            return {
                "song_name": track['name'],
                "artist(s)": ', '.join([a['name'] for a in track['artists']]),
                "artist_id": artist['id'],
                "album_name": track['album']['name'],
                "album_art_url": track['album']['images'][0]['url'] if track['album']['images'] else ''
            }
        except Exception as e:
            return {"error": f"An API error occurred: {e}"}

    def get_artist_albums(self, artist_id: str) -> dict:
        """Fetches top albums for the given artist."""
        if not self.sp: return {}
        
        top_albums = []

        try:
            # Get artist albums (avoiding singles/compilations if possible, or just taking top)
            albums = self.sp.artist_albums(artist_id, album_type='album', limit=3)
            top_albums = [a['name'] for a in albums['items']]
        except Exception as e:
            pass

        return {
            "top_albums": top_albums
        }