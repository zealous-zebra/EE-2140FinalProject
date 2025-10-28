# File: src/main.py

# We import the function that starts our GUI
from src.user_interface.app import start_gui

def run_application():
    """
    The main function to orchestrate the application's workflow.
    For now, it just launches the GUI.
    """
    print("Starting music recognition application...")
    start_gui()


if __name__ == '__main__':
    # This block allows the script to be run directly.
    run_application()
