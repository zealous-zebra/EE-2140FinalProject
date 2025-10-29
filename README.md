# Project Shazamify Pi

## Table of Contents
1. [Project Description](#project-description)
2. [Features](#features)
3. [Hardware Requirements](#hardware-requirements)
4. [Software and Setup](#software-and-setup)
5. [Project Structure](#project-structure)
6. [How to Run](#how-to-run)
7. [Team Members](#team-members)

---

### Project Description

Shazamify Pi is a custom-built, Raspberry Pi 5-powered device designed for real-time music recognition and analysis. Housed in a custom-designed chassis, it features a high-resolution touchscreen display for a rich user interface. The device can listen to a song playing nearby, identify it, and provide detailed information and visualizations related to the music.

This project combines hardware design (CAD), software development (Python), and API integration to create a visually stunning and practical music companion.

### Features

*   **Song Recognition:** Utilizes a microphone to record audio and identify the song title and artist.
*   **Spotify Integration:** Connects to the Spotify API to fetch related artist information, albums, and other metadata.
*   **Audio Visualization:** Performs a Fast Fourier Transform (FFT) on the recorded audio to generate and display a real-time frequency spectrum plot.
*   **Touchscreen GUI:** A user-friendly graphical interface designed for a touchscreen LCD.
*   **Custom Chassis:** A unique enclosure designed with CAD software and built using laser-cut plexiglass and 3D-printed components.

### Hardware Requirements

*   Raspberry Pi 5 (8GB Recommended)
*   Official Raspberry Pi 27W USB-C Power Supply
*   Raspberry Pi Active Cooler
*   32GB+ High-Speed MicroSD Card (A2 Rated)
*   10.1-inch Touchscreen LCD Display
*   USB Microphone

### Software and Setup

This project is built with Python. Follow these steps to set up the development environment.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/your-project-name.git
    cd your-project-name
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
your-project-name/
├── cad/                  # CAD files for the chassis
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