# File: src/user_interface/app.py

import sys
import requests
from pathlib import Path
from functools import partial  # To connect buttons with arguments
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget,
)
from PyQt6.QtCore import Qt, QThread  # QThread is essential for threading
from PyQt6.QtGui import QPixmap, QFont, QColor

from src.spotify_api.client import SpotifyClient
# Import the new Recorder class for threaded recording
from src.audio_processing.recognition import Recorder
from src.audio_processing.visualization import save_plots


class ShazamifyApp(QMainWindow):
    """
    The main application window for shazamify Pi.

    This class constructs and manages the entire graphical user interface,
    including all its tabs, widgets, and connections to the backend logic
    for song recognition and audio analysis.
    """

    def __init__(self):
        """
        Initializes the main application window.

        This constructor sets up the window's properties, initializes state variables
        for threading and Spotify, loads default assets, creates the main tab widget,
        and calls the setup methods for each tab to build the UI.
        """
        super().__init__()
        self.setWindowTitle("shazamify Pi")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
            }
        """)

        # --- State and Threading Variables ---
        self.thread = None
        self.recorder = None
        self.selected_duration = 3.0  # Default recording duration
        self.original_pixmap = None

        # --- Initialize Backend Clients ---
        try:
            self.spotify_client = SpotifyClient()
        except ValueError as e:
            print(f"Configuration Error: {e}")
            self.spotify_client = None

        # --- Load Assets ---
        image_path = Path(__file__).parent.parent / "assets" / "default_album_art.png"
        self.default_pixmap = QPixmap(str(image_path))

        # --- Setup Main UI Structure (Tabs) ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #16213e; color: rgba(255, 255, 255, 0.7);
                padding: 12px 25px; font-size: 16px; font-weight: bold;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
            }
            QTabBar::tab:selected { background: #0f3460; color: white; }
            QTabBar::tab:hover { background: #1e3a6e; }
        """)
        self.setCentralWidget(self.tabs)

        self.shazam_tab = QWidget()
        self.analysis_tab = QWidget()
        self.tabs.addTab(self.shazam_tab, " shazamify")
        self.tabs.addTab(self.analysis_tab, " Audio Analysis")

        # --- Build the UI for each tab ---
        self.setup_shazam_tab()
        self.setup_analysis_tab()

    def setup_shazam_tab(self):
        """
        Constructs the user interface for the "shazamify" tab.

        This method creates all the widgets for song recognition, including the
        album art display, song/artist/album info labels, and the "Listen" button.
        It lays them out and connects the button to its functionality.
        """
        main_layout = QHBoxLayout(self.shazam_tab)
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(30, 30, 30, 30)
        self.album_art_label = QLabel()
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art_label.setFixedSize(400, 400)
        self.set_album_art_pixmap(self.default_pixmap)
        shadow_effect = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=10, color=QColor(0, 0, 0, 100))
        self.album_art_label.setGraphicsEffect(shadow_effect)
        main_layout.addWidget(self.album_art_label, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        self.song_label = QLabel("Waiting for music...")
        self.song_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.song_label.setStyleSheet("color: #ffffff; background: transparent; padding: 10px; letter-spacing: 1px;")
        self.artist_label = QLabel("Ready to listen")
        self.artist_label.setFont(QFont("Arial", 22, QFont.Weight.Medium))
        self.artist_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; padding: 8px;")
        self.album_label = QLabel("")
        self.album_label.setFont(QFont("Arial", 18))
        self.album_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.7); background: transparent; padding: 5px; font-style: italic;")
        self.listen_button = QPushButton("🎧 Listen")
        self.listen_button.setStyleSheet("""
            QPushButton { font-size: 24px; font-weight: bold; padding: 18px 40px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e94560, stop:1 #ff6b6b); color: white; border: none; border-radius: 30px; letter-spacing: 2px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b6b, stop:1 #ffd93d); }
            QPushButton:pressed { padding: 20px 38px 16px 42px; }
        """)
        self.listen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.listen_button.clicked.connect(self.recognize_song)
        button_shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=5, color=QColor(233, 69, 96, 120))
        self.listen_button.setGraphicsEffect(button_shadow)

        right_layout.addStretch(1)
        right_layout.addWidget(self.song_label)
        right_layout.addWidget(self.artist_label)
        right_layout.addWidget(self.album_label)
        right_layout.addStretch(2)
        right_layout.addWidget(self.listen_button, alignment=Qt.AlignmentFlag.AlignCenter)
        right_layout.addStretch(1)
        main_layout.addLayout(right_layout, 1)

    def setup_analysis_tab(self):
        """
        Constructs the user interface for the "Audio Analysis" tab.

        This method creates widgets for recording and visualizing audio, including
        a description, duration selection buttons (3s, 5s, 10s), the "Record"
        button, and placeholders for the generated plots.
        """
        main_layout = QVBoxLayout(self.analysis_tab)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        description = QLabel("Record and visualize any audio from your microphone.")
        description.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        description.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 10px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        self.duration_buttons = {}
        for duration in [3.0, 5.0, 10.0]:
            btn = QPushButton(f"{int(duration)}s")
            btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            btn.setCheckable(True)
            btn.clicked.connect(partial(self.set_duration, duration))
            duration_layout.addWidget(btn)
            self.duration_buttons[duration] = btn
        self.update_duration_buttons_style()

        self.record_button = QPushButton("🎤 Record Audio")
        self.record_button.setStyleSheet("""
            QPushButton { font-size: 22px; font-weight: bold; padding: 16px 35px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e90ff, stop:1 #56ab2f); color: white; border: none; border-radius: 28px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #56ab2f, stop:1 #a8e063); }
            QPushButton:pressed { padding: 18px 33px 14px 37px; }
        """)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.clicked.connect(self.start_recording_thread)
        button_shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=5, color=QColor(30, 144, 255, 100))
        self.record_button.setGraphicsEffect(button_shadow)

        plots_layout = QHBoxLayout()
        plots_layout.setSpacing(20)
        self.time_plot_label = QLabel("📊 Time Domain Plot")
        self.freq_plot_label = QLabel("📈 Magnitude Spectrum Plot")
        for plot_label in [self.time_plot_label, self.freq_plot_label]:
            plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            plot_label.setFont(QFont("Arial", 16))
            plot_label.setStyleSheet("""
                QLabel { border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 15px; background: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.7); }
            """)
        plots_layout.addWidget(self.time_plot_label)
        plots_layout.addWidget(self.freq_plot_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch();
        button_layout.addWidget(self.record_button);
        button_layout.addStretch()

        main_layout.addWidget(description, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(duration_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(plots_layout, 1)

    def set_duration(self, duration):
        """
        Slot to handle clicks on the duration selection buttons.

        Args:
            duration (float): The duration in seconds selected by the user.

        This method updates the application's state to store the new duration
        and calls a helper function to update the button styles for visual feedback.
        """
        self.selected_duration = duration
        print(f"Recording duration set to {self.selected_duration} seconds.")
        self.update_duration_buttons_style()

    def update_duration_buttons_style(self):
        """
        Helper function to style the active duration button.

        This iterates through the duration buttons, ensuring only the currently
        selected one has the "checked" style, making the UI intuitive.
        """
        base_style = """
            QPushButton { background-color: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 15px; padding: 10px 20px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
            QPushButton:checked { background-color: #1e90ff; border: 1px solid #1e90ff; }
        """
        for duration, btn in self.duration_buttons.items():
            btn.setStyleSheet(base_style)
            btn.setChecked(duration == self.selected_duration)

    def start_recording_thread(self):
        """
        Initializes and starts the background audio recording process.

        This method creates a QThread and a Recorder worker object. It moves the
        worker to the thread and connects the worker's signals (progress, finished)
        to slots in the main GUI. This prevents the GUI from freezing during
        the audio recording process.
        """
        self.record_button.setEnabled(False)
        self.thread = QThread()
        self.recorder = Recorder(seconds=self.selected_duration)
        self.recorder.moveToThread(self.thread)

        self.thread.started.connect(self.recorder.run)
        self.recorder.progress.connect(self.update_record_progress)
        self.recorder.finished.connect(self.on_recording_finished)

        self.recorder.finished.connect(self.thread.quit)
        self.recorder.finished.connect(self.recorder.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_record_progress(self, sec):
        """
        Slot to update the record button's text with a live countdown.

        Args:
            sec (int): The current second of recording, received from the worker.
        """
        self.record_button.setText(f"🔴 Recording... {sec}/{int(self.selected_duration)}s")

    def on_recording_finished(self, data):
        """
        Slot that handles the results after the recording worker is finished.

        Args:
            data (tuple): A tuple containing (sample_rate, audio_data_array).

        This method receives the recorded audio data, calls the backend function
        to generate and save plots, loads those plots as images, displays them
        in the UI, and re-enables the record button.
        """
        fs, x = data
        if x.size == 0:
            print("Recording failed, not generating plots.")
            self.record_button.setText("🎤 Record Audio");
            self.record_button.setEnabled(True)
            return

        self.record_button.setText("⚙️ Generating Plots...")
        QApplication.processEvents()

        plot_paths = save_plots(x, fs)
        time_pixmap = QPixmap(plot_paths["time_png"])
        freq_pixmap = QPixmap(plot_paths["spectrum_png"])

        self.time_plot_label.setPixmap(
            time_pixmap.scaled(self.time_plot_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation))
        self.freq_plot_label.setPixmap(
            freq_pixmap.scaled(self.freq_plot_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation))
        self.time_plot_label.setStyleSheet("border: none;");
        self.freq_plot_label.setStyleSheet("border: none;")

        self.record_button.setText("🎤 Record Audio")
        self.record_button.setEnabled(True)

    def recognize_song(self):
        """
        Slot for the 'Listen' button. Fetches song data from Spotify.

        This method uses a hardcoded song title as a placeholder for the actual
        audio recognition logic. It calls the Spotify client, gets song details,
        and updates the UI on the "shazamify" tab with the results.
        """
        if not self.spotify_client: self.song_label.setText("Error: Spotify client not initialized."); return
        self.song_label.setText("🎵 Listening...");
        self.artist_label.setText("Analyzing audio...");
        self.album_label.setText("")
        self.listen_button.setEnabled(False);
        self.listen_button.setText("⏳ Processing...")
        QApplication.processEvents()
        recognized_song_title = "Daft Punk - Around the World"
        song_details = self.spotify_client.get_song_details(recognized_song_title)
        if "error" in song_details:
            self.song_label.setText(f"❌ {song_details['error']}");
            self.artist_label.setText("Please try again.");
            self.album_label.setText("")
            self.set_album_art_pixmap(self.default_pixmap)
        else:
            self.song_label.setText(f"{song_details['song_name']}");
            self.artist_label.setText(f"by {song_details['artist(s)']}");
            self.album_label.setText(f"{song_details['album_name']}")
            self.update_album_art(song_details['album_art_url'])
        self.listen_button.setEnabled(True);
        self.listen_button.setText("🎧 Listen")

    def update_album_art(self, url):
        """
        Downloads an image from a URL and displays it as the album art.

        Args:
            url (str): The URL of the album art image.
        """
        try:
            response = requests.get(url, stream=True);
            response.raise_for_status()
            pixmap = QPixmap();
            pixmap.loadFromData(response.content)
            self.set_album_art_pixmap(pixmap)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}");
            self.set_album_art_pixmap(self.default_pixmap)

    def set_album_art_pixmap(self, pixmap):
        """
        Scales and sets a QPixmap on the album art label.

        Args:
            pixmap (QPixmap): The image to be displayed.

        This helper function ensures that any image (downloaded or default) is
        properly scaled to fit the display label while maintaining aspect ratio.
        """
        self.original_pixmap = pixmap
        scaled_pixmap = pixmap.scaled(self.album_art_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.album_art_label.setPixmap(scaled_pixmap)
        self.album_art_label.setStyleSheet("""
            QLabel { border: 3px solid rgba(255, 255, 255, 0.2); border-radius: 20px; background: transparent; padding: 10px; }
        """)

    def resizeEvent(self, event):
        """
        Handles the window resize event to rescale the album art.

        This ensures the album art image quality is maintained and fits correctly
        even if the user resizes the application window.
        """
        super().resizeEvent(event)
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.set_album_art_pixmap(self.original_pixmap)


def start_gui():
    """
    The main entry point function for launching the GUI.

    This function creates the QApplication instance, instantiates the main
    ShazamifyApp window, shows it, and starts the application's event loop,
    waiting for user interaction.
    """
    app = QApplication(sys.argv)
    window = ShazamifyApp()
    window.show()
    sys.exit(app.exec())

