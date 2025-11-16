#!/usr/bin/env python3
"""
Instagram Reel Bulk Downloader & Transcriber
Main entry point for the application.

This application allows you to:
1. Load Instagram reel URLs from an Excel file
2. Bulk download the reels
3. Transcribe them using OpenAI Whisper
4. Save transcriptions back to Excel

Author: Claude Code
License: MIT
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app_gui import InstagramTranscriberApp
from config import settings


def main():
    """
    Main entry point for the Instagram Reel Transcriber application.
    Launches the GUI application.
    """
    print("=" * 60)
    print("Instagram Reel Bulk Downloader & Transcriber")
    print("=" * 60)
    print()
    print("Starting application...")
    print(f"Download folder: {settings.DEFAULT_DOWNLOAD_FOLDER}")
    print(f"Default Whisper model: {settings.DEFAULT_WHISPER_MODEL}")
    print()

    # Ensure required directories exist
    settings.create_directories()

    # Launch GUI
    try:
        app = InstagramTranscriberApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n\nApplication closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        print("\nPlease check that all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
