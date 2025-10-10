# File: src/user_interface/main.py

# This import works because we will run the script as a module from the root directory.
from src.spotify_api.client import SpotifyClient

def run_application():
    """
    The main function to orchestrate the application's workflow.
    """
    print("Starting music recognition application...")

    # --- This is a placeholder for your future audio recognition ---
    # In the final version, a function from `src/audio_processing/recognition.py`
    # would return this song title.
    recognized_song_title = "Kanye West- Flashing Lights"
    print(f"Recognized song (placeholder): '{recognized_song_title}'")
    # ---------------------------------------------------------------

    # Step 1: Initialize our Spotify client
    try:
        spotify_client = SpotifyClient()
    except ValueError as e:
        print(f"Error: {e}")
        return # Exit if credentials aren't found

    # Step 2: Use the client to get song details from the API
    print("Fetching song details from Spotify...")
    song_details = spotify_client.get_song_details(recognized_song_title)

    # Step 3: Display the results
    # For now, we print to the console. Later, this logic will be used
    # to display the information on your LCD screen.
    print("\n--- SONG INFORMATION ---")
    if "error" in song_details:
        print(f"Could not retrieve details: {song_details['error']}")
    else:
        print(f"  Song:   {song_details['song_name']}")
        print(f"  Artist: {song_details['artist(s)']}")
        print(f"  Album:  {song_details['album_name']}")
        print(f"  Cover:  {song_details['album_art_url']}")
    print("------------------------\n")


if __name__ == '__main__':
    # This block allows the script to be run directly.
    run_application()