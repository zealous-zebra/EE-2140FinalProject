# File: src/spotify_api/spotify_client.py

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


class SpotifyClient:
    """
    A client to interact with the Spotify Web API.
    Handles authentication and data fetching.
    """

    def __init__(self):
        """
        Initializes the Spotify client by loading credentials and authenticating.
        """
        # Load credentials from the .env file located in the project root
        # Get the absolute path to the project root (two levels up from this file)
        import pathlib
        project_root = pathlib.Path(__file__).parent.parent.parent
        env_path = project_root / '.env'
        load_dotenv(env_path)

        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            # Using a custom exception would be even better, but this is clear.
            raise ValueError(
                "Spotify API credentials (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET) not found in .env file.")

        try:
            # Set up the Spotipy client with our credentials
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("Spotify Client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Spotify client: {e}")
            self.sp = None

    def get_song_details(self, song_title: str) -> dict:
        """
        Searches for a song on Spotify and returns a dictionary of its details.

        Args:
            song_title: The name of the song to search for (e.g., "Artist - Song Name").

        Returns:
            A dictionary containing the song's details or an error message.
        """
        if not self.sp:
            return {"error": "Spotify client not initialized."}

        try:
            # Perform the search for the given song title
            result = self.sp.search(q=song_title, type='track', limit=1)

            # Handle the case where no song is found
            if not result['tracks']['items']:
                return {"error": f"No results found for '{song_title}'."}

            # Extract the first track from the search results
            track = result['tracks']['items'][0]

            # Extract the specific data needed
            song_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            album_name = track['album']['name']
            album_art_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No image available'

            # Package the information into a clean dictionary
            song_details = {
                "song_name": song_name,
                "artist(s)": artists,
                "album_name": album_name,
                "album_art_url": album_art_url
            }

            return song_details
        except Exception as e:
            return {"error": f"An API error occurred: {e}"}