# File: shazamify/services/recognition_client.py

import os
import json
import pathlib
from dotenv import load_dotenv


from acrcloud.recognizer import ACRCloudRecognizer


class RecognitionClient:
    """
    Handles sending audio data to the ACRCloud service and returning the result.
    """

    def __init__(self):
        """Initializes the ACRCloud recognizer with credentials from the .env file."""
        try:
            project_root = pathlib.Path(__file__).parent.parent.parent
            env_path = project_root / '.env'
            load_dotenv(env_path)

            config = {
                'host': os.getenv("ACR_HOST"),
                'access_key': os.getenv("ACR_KEY"),
                'access_secret': os.getenv("ACR_SECRET"),
                'timeout': 10  # seconds
            }

            if not all(config.values()):
                raise ValueError("ACRCloud API credentials not found in .env file.")


            self.recognizer = ACRCloudRecognizer(config)
            print("ACRCloud Recognition Client initialized successfully.")

        except Exception as e:
            print(f"Error initializing ACRCloud client: {e}")
            self.recognizer = None

    def identify_song(self, audio_file_path: str, rec_duration: int = 10) -> str | None:
        """
        Identifies a song from a local audio file.
        (This method's logic does not need to change).
        """
        if not self.recognizer:
            print("Recognition client not initialized.")
            return None

        try:
            print(f"Sending '{audio_file_path}' to ACRCloud for recognition...")

            # This call is still correct. The method is part of the recognizer object.
            result_string = self.recognizer.recognize_by_file(
                audio_file_path,
                start_seconds=0,
                rec_length=rec_duration
            )

            result_json = json.loads(result_string)

            if result_json.get('status', {}).get('code') == 0:
                music_info = result_json['metadata']['music'][0]
                title = music_info.get('title', 'Unknown Title')
                artists = music_info.get('artists', [])
                artist_names = ', '.join([artist.get('name', '') for artist in artists])

                print(f"Successfully identified: {artist_names} - {title}")
                return f"{artist_names} - {title}"
            else:
                error_message = result_json.get('status', {}).get('msg', 'Unknown error')
                print(f"No result found from ACRCloud: {error_message}")
                return None

        except Exception as e:
            print(f"An error occurred during song recognition: {e}")
            return None