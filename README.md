# Project Shazamify

## Table of Contents
1. [Project Description](#project-description)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Software and Setup](#software-and-setup)
5. [Project Structure](#project-structure)
6. [How to Run](#how-to-run)
7. [Team Members](#team-members)

---

### Project Description

Shazamify is a desktop application designed for real-time music recognition and analysis. It features a rich user interface that can listen to a song playing nearby, identify it, and provide detailed information and visualizations related to the music.

This project combines software development (Python) and API integration to create a visually stunning and practical music companion.

### Features

*   **Song Recognition:** Utilizes a microphone to record audio and identify the song title and artist.
*   **Spotify Integration:** Connects to the Spotify API to fetch related artist information, albums, and other metadata.
*   **Audio Visualization:** Performs a Fast Fourier Transform (FFT) on the recorded audio to generate and display a real-time frequency spectrum plot.
*   **Graphical User Interface:** A user-friendly graphical interface designed for easy interaction.

### System Requirements

*   Python 3.x
*   Microphone (Built-in or USB)
*   Internet Connection (for API access)

### Software and Setup

This project is built with Python. Follow these steps to set up the development environment.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/zealous-zebra/EE-2140FinalProject.git
    cd EE-2140FinalProject
    ```

2.  **Create a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Install all the required Python libraries using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys:**
    This project requires API keys for the Spotify API.
    *   Create a file named `.env` in the root project directory.
    *   Add your credentials to this file in the following format:
        ```
        SPOTIPY_CLIENT_ID='YourSpotifyClientID'
        SPOTIPY_CLIENT_SECRET='YourSpotifyClientSecret'
        SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
        ```
    *   **Important:** The `.env` file is included in `.gitignore` and should **never** be committed to version control.

### Project Structure

```
EE-2140FinalProject/
├── data/                 # For audio recordings and plots
├── docs/                 # Project documentation
├── src/                  # Main source code
│   ├── main.py           # Main application entry point
│   ├── audio_processing/ # Audio recognition and visualization
│   ├── spotify_api/      # Spotify API client
│   └── user_interface/   # GUI code
├── tests/                # Unit tests
├── .gitignore
├── README.md
└── requirements.txt
```

### How to Run

To run the main application, execute the `main.py` script from the root directory:

```bash
python shazamify/main.py
```

### Team Members
*   Omar Pleitez
*   Ben Ikanovic
*   Nathanael Lee 
