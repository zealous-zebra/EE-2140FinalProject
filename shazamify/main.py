# File: shazamify/main.py
# Purpose: The main entry point for the Shazamify Pi application.

import sys
from PyQt6.QtWidgets import QApplication

from shazamify.ui.main_window import ShazamifyApp
from shazamify.controller import Controller


def run_application():
    """Initializes and runs the PyQt6 application."""
    app = QApplication(sys.argv)

    # 1. Create the view (the main window)
    window = ShazamifyApp()

    # 2. Create the controller and pass the view to it
    # The controller will handle all the logic and connect signals.
    controller = Controller(window)

    # 3. Show the main window and start the application loop
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_application()