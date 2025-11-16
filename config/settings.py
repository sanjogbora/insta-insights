"""
Configuration settings for Instagram Reel Transcriber.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Default paths
DEFAULT_DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, "downloads")
DEFAULT_OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")

# Excel settings
DEFAULT_EXCEL_COLUMN = "Instagram URL"
DEFAULT_TRANSCRIPTION_COLUMN = "Transcription"
DEFAULT_STATUS_COLUMN = "Status"

# Whisper settings
DEFAULT_WHISPER_MODEL = "base"
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]

# Model descriptions for UI
WHISPER_MODEL_DESCRIPTIONS = {
    "tiny": "Fastest, least accurate (good for testing)",
    "base": "Balanced - Recommended for most use cases",
    "small": "Better accuracy, slower processing",
    "medium": "High accuracy, requires more resources",
    "large": "Best accuracy, very slow, requires GPU"
}

# Download settings
DOWNLOAD_DELAY_SECONDS = 3  # Delay between downloads to avoid rate limiting
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# Instagram settings
SESSION_FILE_PATH = os.path.join(PROJECT_ROOT, "config", "instagram_session.json")
ENABLE_LOGIN = False  # Set to True to enable Instagram login by default

# Processing settings
BATCH_SIZE = 10  # Number of items to process in one batch (for progress updates)
ENABLE_TIMESTAMPS = False  # Whether to include timestamps in transcriptions
AUTO_DETECT_LANGUAGE = True  # Auto-detect language instead of specifying

# GUI settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 750
THEME = "dark"  # "dark" or "light"
COLOR_THEME = "blue"  # CustomTkinter color theme

# Logging settings
ENABLE_LOGGING = True
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "app.log")
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Performance settings
USE_GPU = True  # Use GPU if available for Whisper
NUM_THREADS = 4  # Number of threads for parallel processing (future feature)

# File settings
SUPPORTED_VIDEO_FORMATS = [".mp4", ".mov", ".avi", ".mkv"]
SUPPORTED_EXCEL_FORMATS = [".xlsx", ".xls"]

# Error handling
CONTINUE_ON_ERROR = True  # Continue processing even if some items fail
SAVE_ERROR_LOG = True  # Save failed items to a separate file
ERROR_LOG_PATH = os.path.join(PROJECT_ROOT, "output", "failed_items.txt")

# Feature flags
ENABLE_PAUSE_RESUME = False  # Enable pause/resume functionality (future feature)
ENABLE_SESSION_PERSISTENCE = True  # Save progress and allow resume
ENABLE_EXPORT_FAILED = True  # Allow exporting failed items to retry later


def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        DEFAULT_DOWNLOAD_FOLDER,
        DEFAULT_OUTPUT_FOLDER,
        os.path.dirname(LOG_FILE),
        os.path.dirname(SESSION_FILE_PATH)
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_config() -> dict:
    """
    Get all configuration as a dictionary.

    Returns:
        Dictionary containing all configuration settings
    """
    return {
        'paths': {
            'download_folder': DEFAULT_DOWNLOAD_FOLDER,
            'output_folder': DEFAULT_OUTPUT_FOLDER,
            'session_file': SESSION_FILE_PATH,
            'log_file': LOG_FILE,
            'error_log': ERROR_LOG_PATH
        },
        'excel': {
            'url_column': DEFAULT_EXCEL_COLUMN,
            'transcription_column': DEFAULT_TRANSCRIPTION_COLUMN,
            'status_column': DEFAULT_STATUS_COLUMN,
            'supported_formats': SUPPORTED_EXCEL_FORMATS
        },
        'whisper': {
            'default_model': DEFAULT_WHISPER_MODEL,
            'available_models': WHISPER_MODELS,
            'model_descriptions': WHISPER_MODEL_DESCRIPTIONS,
            'use_gpu': USE_GPU,
            'auto_detect_language': AUTO_DETECT_LANGUAGE,
            'enable_timestamps': ENABLE_TIMESTAMPS
        },
        'download': {
            'delay_seconds': DOWNLOAD_DELAY_SECONDS,
            'max_retries': MAX_RETRIES,
            'retry_delay': RETRY_DELAY_SECONDS,
            'supported_formats': SUPPORTED_VIDEO_FORMATS
        },
        'gui': {
            'window_width': WINDOW_WIDTH,
            'window_height': WINDOW_HEIGHT,
            'theme': THEME,
            'color_theme': COLOR_THEME
        },
        'processing': {
            'batch_size': BATCH_SIZE,
            'continue_on_error': CONTINUE_ON_ERROR,
            'save_error_log': SAVE_ERROR_LOG
        },
        'features': {
            'enable_login': ENABLE_LOGIN,
            'enable_logging': ENABLE_LOGGING,
            'enable_pause_resume': ENABLE_PAUSE_RESUME,
            'enable_session_persistence': ENABLE_SESSION_PERSISTENCE,
            'enable_export_failed': ENABLE_EXPORT_FAILED
        }
    }


# Initialize directories when settings are imported
create_directories()
