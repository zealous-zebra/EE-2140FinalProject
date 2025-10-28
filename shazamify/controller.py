from PyQt6.QtCore import QObject, QThread

from .services.spotify_client import SpotifyClient
from .services.recognition_client import RecognitionClient
from .audio.recorder import Recorder
from .audio.analyzer import generate_and_save_plots

class Controller(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.spotify_client = SpotifyClient()
        self.recognition_client = RecognitionClient()
        self.thread = None
        self.recorder = None

        # --- NEW VARIABLE ---
        self.recognition_duration = 7  # Recognize for 7 seconds

        self._connect_signals()

    def _connect_signals(self):
        self.view.recognition_tab.listen_button_pressed.connect(self.start_song_recognition)
        self.view.analysis_tab.record_button_pressed.connect(self.start_audio_analysis)

    def start_song_recognition(self):
        """
        Starts the entire song recognition workflow: Record -> Identify -> Display.
        """
        self.view.recognition_tab.set_status_listening()

        # --- THIS IS THE NEW RECORDING LOGIC ---
        self.thread = QThread()
        # Use the new duration variable
        self.recorder = Recorder(seconds=self.recognition_duration)
        self.recorder.moveToThread(self.thread)

        # When recording finishes, call a new handler method
        self.recorder.finished.connect(self.on_recognition_clip_finished)

        # Standard thread cleanup
        self.recorder.finished.connect(self.thread.quit)
        self.recorder.finished.connect(self.recorder.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start recording
        self.thread.started.connect(self.recorder.run)
        self.thread.start()

    def on_recognition_clip_finished(self, data):
        """
        This method is called ONLY when the recording for song recognition is done.
        """
        fs, x = data
        if x.size == 0:
            error_details = {"error": "Recording failed."}
            self.view.recognition_tab.update_with_song_details(error_details)
            return

        # The recorder saves the file, so we just need the path.
        audio_clip_path = "data/audio_recordings/clip.wav"

        # Call our updated recognition client, passing the duration
        song_title = self.recognition_client.identify_song(
            audio_clip_path,
            rec_duration=self.recognition_duration
        )

        if song_title:
            song_details = self.spotify_client.get_song_details(song_title)
            self.view.recognition_tab.update_with_song_details(song_details)
        else:
            error_details = {"error": "Could not identify song."}
            self.view.recognition_tab.update_with_song_details(error_details)

    def start_audio_analysis(self, duration):
        """Starts a background thread for recording and analysis."""
        self.thread = QThread()
        self.recorder = Recorder(seconds=duration)
        self.recorder.moveToThread(self.thread)

        self.thread.started.connect(self.recorder.run)
        self.recorder.progress.connect(
            lambda sec: self.view.analysis_tab.set_status_recording(sec, duration)
        )
        self.recorder.finished.connect(self.on_recording_finished)

        # Cleanup connections
        self.recorder.finished.connect(self.thread.quit)
        self.recorder.finished.connect(self.recorder.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_recording_finished(self, data):
        """Handles the audio data once recording is complete."""
        fs, x = data
        if x.size == 0:
            self.view.analysis_tab.recording_failed()
            return

        self.view.analysis_tab.set_status_generating_plots()
        plot_paths = generate_and_save_plots(x, fs)
        self.view.analysis_tab.display_plots(plot_paths)



