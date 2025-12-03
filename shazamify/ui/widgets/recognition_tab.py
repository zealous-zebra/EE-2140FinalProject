# File: shazamify/ui/widgets/recognition_tab.py

import requests
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor
from pathlib import Path

class RecognitionTab(QWidget):
    """UI for the main song recognition feature."""
    listen_button_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        image_path = Path(__file__).parent.parent.parent.parent / "assets" / "default_album_art.png"
        self.default_pixmap = QPixmap(str(image_path))
        self.original_pixmap = None
        self.setup_ui()

    def setup_ui(self):
        # This is the old setup_shazam_tab method
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(40); main_layout.setContentsMargins(30, 30, 30, 30)
        self.album_art_label = QLabel()
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art_label.setFixedSize(400, 400)
        self.set_album_art_pixmap(self.default_pixmap)
        shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=10, color=QColor(0,0,0,100))
        self.album_art_label.setGraphicsEffect(shadow)
        main_layout.addWidget(self.album_art_label, 1)

        right_layout = QVBoxLayout()
        self.song_label = QLabel("Waiting for music...")
        self.song_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.song_label.setStyleSheet("color: #ffffff;")
        self.artist_label = QLabel("Ready to listen")
        self.artist_label.setFont(QFont("Arial", 22))
        self.artist_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        self.album_label = QLabel("")
        self.album_label.setFont(QFont("Arial", 18))
        self.album_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-style: italic;")
        self.listen_button = QPushButton("🎧 Listen")
        self.listen_button.setStyleSheet("""
            QPushButton { font-size: 24px; padding: 18px 40px; background-color: #e94560; color: white; border-radius: 30px; }
            QPushButton:hover { background-color: #ff6b6b; }
        """)
        self.listen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.listen_button.clicked.connect(self.listen_button_pressed.emit)

        # --- RECOMMENDATIONS SECTION ---
        self.recommendations_layout = QVBoxLayout()
        self.recommendations_layout.setSpacing(5)
        
        self.top_albums_label = QLabel("")
        self.top_albums_label.setFont(QFont("Arial", 18))
        self.top_albums_label.setStyleSheet("color: #cccccc;")
        self.top_albums_label.setWordWrap(True)

        self.recommendations_layout.addWidget(self.top_albums_label)

        right_layout.addStretch(1)
        right_layout.addWidget(self.song_label); right_layout.addWidget(self.artist_label)
        right_layout.addWidget(self.album_label); right_layout.addStretch(1)
        right_layout.addLayout(self.recommendations_layout) # Add recommendations here
        right_layout.addStretch(1)
        right_layout.addWidget(self.listen_button, alignment=Qt.AlignmentFlag.AlignCenter)
        right_layout.addStretch(1)
        main_layout.addLayout(right_layout, 1)

    # --- PUBLIC SLOTS FOR CONTROLLER ---
    def set_status_listening(self):
        self.song_label.setText("🎵 Listening..."); self.artist_label.setText("Analyzing audio...")
        self.album_label.setText(""); self.listen_button.setEnabled(False)
        self.top_albums_label.setText("")
        self.listen_button.setText("⏳ Processing...")
        QApplication.processEvents()

    def update_with_song_details(self, details):
        if "error" in details:
            self.song_label.setText(f"❌ {details['error']}"); self.artist_label.setText("Please try again.")
            self.album_label.setText(""); self.set_album_art_pixmap(self.default_pixmap)
            self.top_albums_label.setText("")
        else:
            self.song_label.setText(details['song_name']); self.artist_label.setText(f"by {details['artist(s)']}")
            self.album_label.setText(details['album_name']); self.update_album_art(details['album_art_url'])
            
            # Update recommendations
            if "top_albums" in details and details["top_albums"]:
                albums_str = ", ".join(details["top_albums"])
                self.top_albums_label.setText(f"<b>More from this Artist:</b> {albums_str}")

        self.listen_button.setEnabled(True); self.listen_button.setText("🎧 Listen")

    # --- HELPER METHODS ---
    def update_album_art(self, url):
        try:
            response = requests.get(url, stream=True); response.raise_for_status()
            pixmap = QPixmap(); pixmap.loadFromData(response.content)
            self.set_album_art_pixmap(pixmap)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}"); self.set_album_art_pixmap(self.default_pixmap)

    def set_album_art_pixmap(self, pixmap):
        self.original_pixmap = pixmap
        scaled = pixmap.scaled(self.album_art_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.album_art_label.setPixmap(scaled)
        self.album_art_label.setStyleSheet("border: 3px solid rgba(255,255,255,0.2); border-radius: 20px;")

    def handle_resize(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.set_album_art_pixmap(self.original_pixmap)