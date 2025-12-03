from PyQt6.QtCore import QObject, QThread

from .services.spotify_client import SpotifyClient
from .services.recognition_client import RecognitionClient
from .audio.recorder import Recorder
from .audio.analyzer import (
    generate_time_domain,
    generate_magnitude_spectrum,
    generate_chromagram,
    generate_spectrogram,
    generate_mel_spectrogram,
    generate_tempogram
)

class Controller(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.spotify_client = SpotifyClient()
        self.recognition_client = RecognitionClient()
        self.thread = None
        self.recorder = None

        # Store the current audio data for on-demand plotting
        self.current_fs = None
        self.current_x = None

        # --- NEW VARIABLE ---
        self.recognition_duration = 7  # Recognize for 7 seconds

        self._connect_signals()

    def _connect_signals(self):
        self.view.recognition_tab.listen_button_pressed.connect(self.start_song_recognition)
        self.view.analysis_tab.record_button_pressed.connect(self.start_audio_analysis)
        # Connect the new signal for generating plots
        self.view.analysis_tab.generate_plot_requested.connect(self.generate_plot)

    # ... (start_song_recognition and on_recognition_clip_finished remain the same)

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

        # Process and display the audio analysis for the recorded clip
        self._process_and_display_analysis(fs, x)


        # The recorder saves the file, so we just need the path.
        audio_clip_path = "data/audio_recordings/clip.wav"

        # Call our updated recognition client, passing the duration
        song_title = self.recognition_client.identify_song(
            audio_clip_path,
            rec_duration=self.recognition_duration
        )

        if song_title:
            song_details = self.spotify_client.get_song_details(song_title)
            
            # Fetch recommendations if we have an artist ID
            if "artist_id" in song_details:
                recommendations = self.spotify_client.get_artist_albums(song_details["artist_id"])
                song_details.update(recommendations)
            
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

        self._process_and_display_analysis(fs, x)

    def _process_and_display_analysis(self, fs, x):
        """
        Stores the audio data and resets the UI for on-demand plotting.
        """
        self.current_fs = fs
        self.current_x = x
        
        # Tell the view that new data is available and reset the buttons
        self.view.analysis_tab.reset_plots_state()

    def generate_plot(self, plot_type):
        """
        Generates a specific plot on demand.
        """
        if self.current_x is None or self.current_fs is None:
            return

        path = None
        if plot_type == "time":
            path = generate_time_domain(self.current_x, self.current_fs)
        elif plot_type == "spectrum":
            path = generate_magnitude_spectrum(self.current_x, self.current_fs)
        elif plot_type == "chroma":
            path = generate_chromagram(self.current_x, self.current_fs)
        elif plot_type == "spectrogram":
            path = generate_spectrogram(self.current_x, self.current_fs)
        elif plot_type == "mel":
            path = generate_mel_spectrogram(self.current_x, self.current_fs)
        elif plot_type == "tempogram":
            path = generate_tempogram(self.current_x, self.current_fs)
        
        if path:
            self.view.analysis_tab.display_single_plot(plot_type, path)
