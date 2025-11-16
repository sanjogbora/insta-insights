"""
Whisper Transcriber Module
Handles transcribing video files using OpenAI Whisper.
"""

import whisper
import os
from typing import Optional, Callable, List, Dict, Tuple
import torch


class WhisperTranscriber:
    """Handles video transcription using OpenAI Whisper."""

    # Available Whisper models
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper transcriber.

        Args:
            model_size: Whisper model size (tiny/base/small/medium/large)

        Raises:
            ValueError: If invalid model size is provided
        """
        if model_size not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model size: {model_size}. "
                f"Available models: {', '.join(self.AVAILABLE_MODELS)}"
            )

        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self, progress_callback: Optional[Callable[[str], None]] = None):
        """
        Load the Whisper model.

        Args:
            progress_callback: Optional callback for progress updates
        """
        if self.model is not None:
            return  # Model already loaded

        if progress_callback:
            progress_callback(f"Loading Whisper model '{self.model_size}' on {self.device}...")

        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            if progress_callback:
                progress_callback(f"Model '{self.model_size}' loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

    def transcribe_video(
        self,
        video_path: str,
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict], Optional[str]]:
        """
        Transcribe a single video file.

        Args:
            video_path: Path to the video file
            language: Optional language code (e.g., 'en', 'es'). If None, auto-detect
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, transcription_text, full_result, error_message)
            full_result contains segments, language detection, etc.
        """
        # Load model if not already loaded
        if self.model is None:
            self.load_model(progress_callback)

        if not os.path.exists(video_path):
            return False, None, None, f"Video file not found: {video_path}"

        if progress_callback:
            progress_callback(f"Transcribing: {os.path.basename(video_path)}")

        try:
            # Transcribe the video
            # Whisper can handle video files directly (extracts audio automatically)
            transcribe_options = {
                "fp16": self.device == "cuda",  # Use FP16 only on CUDA
                "verbose": False
            }

            if language:
                transcribe_options["language"] = language

            result = self.model.transcribe(video_path, **transcribe_options)

            # Extract the transcription text
            transcription_text = result["text"].strip()

            if progress_callback:
                progress_callback(f"Transcription complete: {os.path.basename(video_path)}")

            return True, transcription_text, result, None

        except Exception as e:
            error_msg = f"Transcription failed for {os.path.basename(video_path)}: {str(e)}"
            if progress_callback:
                progress_callback(error_msg)
            return False, None, None, error_msg

    def batch_transcribe(
        self,
        video_paths: List[str],
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        Transcribe multiple video files.

        Args:
            video_paths: List of paths to video files
            language: Optional language code for all videos
            progress_callback: Optional callback (current, total, message)

        Returns:
            Dictionary with transcription results:
            {
                'successful': [(video_path, transcription), ...],
                'failed': [(video_path, error_message), ...],
                'full_results': [(video_path, full_whisper_result), ...],
                'total': int,
                'success_count': int,
                'fail_count': int
            }
        """
        # Load model once for batch processing
        if self.model is None:
            self.load_model(
                progress_callback=lambda msg: progress_callback(0, len(video_paths), msg)
                if progress_callback else None
            )

        results = {
            'successful': [],
            'failed': [],
            'full_results': [],
            'total': len(video_paths),
            'success_count': 0,
            'fail_count': 0
        }

        for idx, video_path in enumerate(video_paths, 1):
            if progress_callback:
                progress_callback(
                    idx,
                    len(video_paths),
                    f"Transcribing {idx}/{len(video_paths)}: {os.path.basename(video_path)}"
                )

            # Transcribe the video
            success, transcription, full_result, error = self.transcribe_video(
                video_path,
                language=language,
                progress_callback=lambda msg: progress_callback(idx, len(video_paths), msg)
                if progress_callback else None
            )

            if success:
                results['successful'].append((video_path, transcription))
                results['full_results'].append((video_path, full_result))
                results['success_count'] += 1
            else:
                results['failed'].append((video_path, error))
                results['fail_count'] += 1

        return results

    def transcribe_with_timestamps(
        self,
        video_path: str,
        language: Optional[str] = None
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Transcribe video with timestamps for each segment.

        Args:
            video_path: Path to video file
            language: Optional language code

        Returns:
            Tuple of (success, segments, error_message)
            Each segment contains: {'start': float, 'end': float, 'text': str}
        """
        if self.model is None:
            self.load_model()

        if not os.path.exists(video_path):
            return False, None, f"Video file not found: {video_path}"

        try:
            transcribe_options = {
                "fp16": self.device == "cuda",
                "verbose": False
            }

            if language:
                transcribe_options["language"] = language

            result = self.model.transcribe(video_path, **transcribe_options)

            # Extract segments with timestamps
            segments = []
            for segment in result["segments"]:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })

            return True, segments, None

        except Exception as e:
            return False, None, f"Transcription failed: {str(e)}"

    def detect_language(self, video_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect the language of a video.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (success, language_code, error_message)
        """
        if self.model is None:
            self.load_model()

        if not os.path.exists(video_path):
            return False, None, f"Video file not found: {video_path}"

        try:
            # Load audio
            audio = whisper.load_audio(video_path)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)

            return True, detected_language, None

        except Exception as e:
            return False, None, f"Language detection failed: {str(e)}"

    def get_model_info(self) -> Dict:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            'model_size': self.model_size,
            'device': self.device,
            'is_loaded': self.model is not None,
            'available_models': self.AVAILABLE_MODELS
        }

    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Standalone functions for simple use cases
def transcribe_video_simple(
    video_path: str,
    model_size: str = "base",
    language: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Simple function to transcribe a video without using the class.

    Args:
        video_path: Path to video file
        model_size: Whisper model size
        language: Optional language code

    Returns:
        Tuple of (success, transcription, error_message)
    """
    transcriber = WhisperTranscriber(model_size)
    success, transcription, _, error = transcriber.transcribe_video(video_path, language)
    return success, transcription, error


def get_available_models() -> List[str]:
    """
    Get list of available Whisper models.

    Returns:
        List of model names
    """
    return WhisperTranscriber.AVAILABLE_MODELS
