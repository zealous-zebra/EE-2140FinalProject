# File: shazamify/ui/main_window.py
# Purpose: The main application window shell.

from PyQt6.QtWidgets import QMainWindow, QTabWidget

# Import the separated tab widgets
from .widgets.recognition_tab import RecognitionTab
from .widgets.analysis_tab import AnalysisTab

class ShazamifyApp(QMainWindow):
    """The main application window, which holds all other UI components."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shazamify Pi")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("QMainWindow { background: #1a1a2e; }")

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #16213e; color: #fff; padding: 12px 25px; }
            QTabBar::tab:selected { background: #0f3460; }
        """)
        self.setCentralWidget(self.tabs)

        # Instantiate and add the tabs
        self.recognition_tab = RecognitionTab()
        self.analysis_tab = AnalysisTab()

        self.tabs.addTab(self.recognition_tab, "Shazamify")
        self.tabs.addTab(self.analysis_tab, "Audio Analysis")

    def resizeEvent(self, event):
        """Passes the resize event to tabs that need it (e.g., for album art)."""
        super().resizeEvent(event)
        self.recognition_tab.handle_resize()