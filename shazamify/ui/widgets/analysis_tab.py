# File: shazamify/ui/widgets/analysis_tab.py

from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QApplication, QScrollArea, QFrame, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

class ResizableImageLabel(QLabel):
    """A QLabel that scales its pixmap while maintaining aspect ratio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setMinimumSize(600, 400) # Increased size for better visibility
        self._pixmap = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        super().setPixmap(self.scaled_pixmap())

    def scaled_pixmap(self):
        if self._pixmap and not self._pixmap.isNull():
            return self._pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
        return self._pixmap

    def resizeEvent(self, event):
        if self._pixmap:
            super().setPixmap(self.scaled_pixmap())
        super().resizeEvent(event)

class PlotWidget(QWidget):
    # ... (PlotWidget implementation remains mostly the same, just context for the file)
    """A widget that holds a plot and a 'Generate' button."""
    generate_requested = pyqtSignal(str)  # Emits the plot type

    def __init__(self, title, plot_type):
        super().__init__()
        self.plot_type = plot_type
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget to switch between button and image
        self.stack = QStackedWidget()
        
        # Page 1: Button
        self.btn_widget = QWidget()
        btn_layout = QVBoxLayout(self.btn_widget)
        self.generate_btn = QPushButton(f"Generate {title}")
        self.generate_btn.setStyleSheet("""
            QPushButton { background-color: #444; color: white; padding: 10px; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #666; }
        """)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Page 2: Image Label
        self.image_label = ResizableImageLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.image_label.setScaledContents(True) # Removed to prevent stretching
        self.image_label.setStyleSheet("border: 2px solid #444; background: #16213e;")
        
        self.stack.addWidget(self.btn_widget)
        self.stack.addWidget(self.image_label)
        
        self.layout.addWidget(QLabel(title))
        self.layout.addWidget(self.stack)
        
        # Initially disabled until data is available
        self.generate_btn.setEnabled(False)

    def _on_generate_clicked(self):
        self.generate_btn.setText("Generating...")
        self.generate_btn.setEnabled(False)
        self.generate_requested.emit(self.plot_type)

    def show_plot(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.stack.setCurrentIndex(1)
        self.generate_btn.setText(f"Regenerate")
        self.generate_btn.setEnabled(True)

    def reset(self):
        self.stack.setCurrentIndex(0)
        self.generate_btn.setText("Generate")
        self.generate_btn.setEnabled(True)
        self.image_label.clear()

    def set_enabled(self, enabled):
        self.generate_btn.setEnabled(enabled)


class AnalysisTab(QWidget):
    """UI for the audio recording and visualization feature."""
    record_button_pressed = pyqtSignal(float)
    generate_plot_requested = pyqtSignal(str) # plot_type

    def __init__(self):
        super().__init__()
        self.selected_duration = 3.0
        self.setup_ui()
        self.set_duration(self.selected_duration)

    def setup_ui(self):
        # Main layout for the tab
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Content Widget inside Scroll Area
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        description = QLabel("Record and visualize audio from your microphone.")
        description.setFont(QFont("Arial", 20)); description.setStyleSheet("color: #fff;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Duration Buttons
        duration_layout = QHBoxLayout(); duration_layout.setSpacing(15)
        self.duration_buttons = {}
        for duration in [3.0, 5.0, 10.0]:
            btn = QPushButton(f"{int(duration)}s"); btn.setFont(QFont("Arial", 14)); btn.setCheckable(True)
            btn.clicked.connect(partial(self.set_duration, duration)); duration_layout.addWidget(btn)
            self.duration_buttons[duration] = btn

        # Record Button
        self.record_button = QPushButton("🎤 Record Audio")
        self.record_button.setStyleSheet("""
            QPushButton { font-size: 22px; padding: 16px 35px; background-color: #1e90ff; color: white; border-radius: 28px; }
            QPushButton:hover { background-color: #56ab2f; }
        """)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.clicked.connect(lambda: self.record_button_pressed.emit(self.selected_duration))

        # --- PLOTS LIST (Single Column) ---
        plots_layout = QVBoxLayout()
        plots_layout.setSpacing(30)
        
        self.plot_widgets = {}
        plot_defs = [
            ("Time Domain", "time"),
            ("Magnitude Spectrum", "spectrum"),
            ("Chromagram", "chroma"),
            ("Spectrogram", "spectrogram"),
            ("Log-Mel Spectrogram", "mel"),
            ("Fourier Tempogram", "tempogram")
        ]

        for title, p_type in plot_defs:
            widget = PlotWidget(title, p_type)
            widget.generate_requested.connect(self.generate_plot_requested.emit)
            plots_layout.addWidget(widget)
            self.plot_widgets[p_type] = widget

        button_layout = QHBoxLayout(); button_layout.addStretch(); button_layout.addWidget(self.record_button); button_layout.addStretch()
        
        main_layout.addWidget(description, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(duration_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(plots_layout)
        
        # Add content widget to scroll area
        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

    # --- PUBLIC SLOTS FOR CONTROLLER ---
    def set_status_recording(self, sec, total_duration):
        self.record_button.setEnabled(False)
        self.record_button.setText(f"🔴 Recording... {sec}/{int(total_duration)}s")
        # Disable generation buttons during recording
        for widget in self.plot_widgets.values():
            widget.set_enabled(False)

    def reset_plots_state(self):
        """Called when new audio data is available."""
        self.record_button.setText("🎤 Record Audio"); self.record_button.setEnabled(True)
        for widget in self.plot_widgets.values():
            widget.reset()

    def display_single_plot(self, plot_type, image_path):
        if plot_type in self.plot_widgets:
            self.plot_widgets[plot_type].show_plot(image_path)

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