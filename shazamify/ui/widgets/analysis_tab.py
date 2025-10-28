# File: shazamify/ui/widgets/analysis_tab.py

from functools import partial
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor

class AnalysisTab(QWidget):
    """UI for the audio recording and visualization feature."""
    record_button_pressed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.selected_duration = 3.0
        self.setup_ui()
        self.set_duration(self.selected_duration)

    def setup_ui(self):
        # This is the old setup_analysis_tab method
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(30, 30, 30, 30); main_layout.setSpacing(20)
        description = QLabel("Record and visualize audio from your microphone.")
        description.setFont(QFont("Arial", 20)); description.setStyleSheet("color: #fff;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        duration_layout = QHBoxLayout(); duration_layout.setSpacing(15)
        self.duration_buttons = {}
        for duration in [3.0, 5.0, 10.0]:
            btn = QPushButton(f"{int(duration)}s"); btn.setFont(QFont("Arial", 14)); btn.setCheckable(True)
            btn.clicked.connect(partial(self.set_duration, duration)); duration_layout.addWidget(btn)
            self.duration_buttons[duration] = btn

        self.record_button = QPushButton("🎤 Record Audio")
        self.record_button.setStyleSheet("""
            QPushButton { font-size: 22px; padding: 16px 35px; background-color: #1e90ff; color: white; border-radius: 28px; }
            QPushButton:hover { background-color: #56ab2f; }
        """)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.clicked.connect(lambda: self.record_button_pressed.emit(self.selected_duration))

        plots_layout = QHBoxLayout(); plots_layout.setSpacing(20)
        self.time_plot_label = QLabel("📊 Time Domain Plot")
        self.freq_plot_label = QLabel("📈 Magnitude Spectrum Plot")
        for label in [self.time_plot_label, self.freq_plot_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter); label.setFont(QFont("Arial", 16))
            label.setStyleSheet("border: 2px dashed #333; border-radius: 15px; color: #aaa;")
        plots_layout.addWidget(self.time_plot_label); plots_layout.addWidget(self.freq_plot_label)

        button_layout = QHBoxLayout(); button_layout.addStretch(); button_layout.addWidget(self.record_button); button_layout.addStretch()
        main_layout.addWidget(description, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(duration_layout); main_layout.addLayout(button_layout); main_layout.addLayout(plots_layout, 1)

    # --- PUBLIC SLOTS FOR CONTROLLER ---
    def set_status_recording(self, sec, total_duration):
        self.record_button.setEnabled(False)
        self.record_button.setText(f"🔴 Recording... {sec}/{int(total_duration)}s")

    def set_status_generating_plots(self):
        self.record_button.setText("⚙️ Generating Plots...")
        QApplication.processEvents()

    def display_plots(self, plot_paths):
        time_pixmap = QPixmap(plot_paths["time_png"])
        freq_pixmap = QPixmap(plot_paths["spectrum_png"])
        self.time_plot_label.setPixmap(time_pixmap.scaled(self.time_plot_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.freq_plot_label.setPixmap(freq_pixmap.scaled(self.freq_plot_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.time_plot_label.setStyleSheet("border: none;"); self.freq_plot_label.setStyleSheet("border: none;")
        self.record_button.setText("🎤 Record Audio"); self.record_button.setEnabled(True)

    def recording_failed(self):
        self.record_button.setText("🎤 Record Audio"); self.record_button.setEnabled(True)

    # --- HELPER METHODS ---
    def set_duration(self, duration):
        self.selected_duration = duration
        self.update_duration_buttons_style()

    def update_duration_buttons_style(self):
        base_style = """
            QPushButton { background-color: #555; color: white; border-radius: 15px; padding: 10px 20px; }
            QPushButton:hover { background-color: #777; }
            QPushButton:checked { background-color: #1e90ff; }
        """
        for d, btn in self.duration_buttons.items():
            btn.setStyleSheet(base_style); btn.setChecked(d == self.selected_duration)