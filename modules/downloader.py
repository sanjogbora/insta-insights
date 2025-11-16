"""
Instagram Downloader Module
Handles downloading Instagram reels using instaloader.
"""

import instaloader
import os
import time
import re
from typing import Optional, Callable, List, Tuple
from pathlib import Path


class InstagramDownloader:
    """Handles downloading Instagram reels using instaloader."""

    def __init__(self, output_folder: str = "./downloads"):
        """
        Initialize the Instagram downloader.

        Args:
            output_folder: Folder to save downloaded reels
        """
        self.output_folder = output_folder
        self.loader = None
        self.is_logged_in = False
        self.session_file = None

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def setup_instaloader(self, session_file: Optional[str] = None):
        """
        Initialize instaloader instance.

        Args:
            session_file: Optional path to session file for authenticated downloads
        """
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern=""
        )

        self.session_file = session_file

        # Load session if available
        if session_file and os.path.exists(session_file):
            try:
                # Session files are typically saved with username
                # This is a simplified version - actual implementation may vary
                self.loader.load_session_from_file(session_file)
                self.is_logged_in = True
            except Exception as e:
                print(f"Warning: Could not load session file: {e}")

    def login(self, username: str, password: str) -> bool:
        """
        Login to Instagram.

        Args:
            username: Instagram username
            password: Instagram password

        Returns:
            True if login successful, False otherwise
        """
        if self.loader is None:
            self.setup_instaloader()

        try:
            self.loader.login(username, password)
            self.is_logged_in = True
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def save_session(self, username: str, session_path: str):
        """
        Save session for future use.

        Args:
            username: Instagram username
            session_path: Path to save session file
        """
        if self.loader and self.is_logged_in:
            try:
                self.loader.save_session_to_file(session_path)
            except Exception as e:
                print(f"Failed to save session: {e}")

    @staticmethod
    def extract_shortcode_from_url(url: str) -> Optional[str]:
        """
        Extract the shortcode (reel ID) from Instagram URL.

        Args:
            url: Instagram URL

        Returns:
            Shortcode if found, None otherwise

        Examples:
            https://www.instagram.com/reel/ABC123/ -> ABC123
            https://instagram.com/p/ABC123/ -> ABC123
        """
        # Pattern to match Instagram reel/post URLs
        patterns = [
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/tv/([A-Za-z0-9_-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def download_reel(
        self,
        url: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download a single Instagram reel.

        Args:
            url: Instagram reel URL
            progress_callback: Optional callback function for progress updates
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Tuple of (success: bool, video_path: str or None, error_message: str or None)
        """
        if self.loader is None:
            self.setup_instaloader()

        shortcode = self.extract_shortcode_from_url(url)
        if not shortcode:
            return False, None, f"Invalid Instagram URL: {url}"

        if progress_callback:
            progress_callback(f"Downloading reel: {shortcode}")

        # Retry logic
        for attempt in range(max_retries):
            try:
                # Get post from shortcode
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)

                # Create a custom folder name for this download
                download_folder = os.path.join(self.output_folder, shortcode)

                # Download the post
                self.loader.download_post(post, target=download_folder)

                # Find the downloaded video file
                video_path = self._find_video_file(download_folder)

                if video_path:
                    if progress_callback:
                        progress_callback(f"Successfully downloaded: {shortcode}")
                    return True, video_path, None
                else:
                    return False, None, f"Video file not found after download: {shortcode}"

            except instaloader.exceptions.LoginRequiredException:
                return False, None, "Login required to download this content"

            except instaloader.exceptions.PrivateProfileNotFollowedException:
                return False, None, "Private profile - cannot download"

            except instaloader.exceptions.PostChangedException:
                return False, None, "Post has been deleted or is unavailable"

            except instaloader.exceptions.ConnectionException as e:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(
                            f"Connection error, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})"
                        )
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Connection error after {max_retries} attempts: {str(e)}"

            except Exception as e:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(
                            f"Error occurred, retrying... (attempt {attempt + 1}/{max_retries})"
                        )
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Error downloading reel: {str(e)}"

        return False, None, "Download failed after all retries"

    def _find_video_file(self, folder: str) -> Optional[str]:
        """
        Find the video file in the download folder.

        Args:
            folder: Folder to search

        Returns:
            Path to video file if found, None otherwise
        """
        if not os.path.exists(folder):
            return None

        # Look for video files (.mp4 is most common)
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    return file_path

        return None

    def batch_download(
        self,
        urls: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        delay_between_downloads: int = 3
    ) -> dict:
        """
        Download multiple Instagram reels.

        Args:
            urls: List of Instagram URLs
            progress_callback: Optional callback (current, total, message)
            delay_between_downloads: Delay between downloads in seconds

        Returns:
            Dictionary with download results:
            {
                'successful': [(url, video_path), ...],
                'failed': [(url, error_message), ...],
                'total': int,
                'success_count': int,
                'fail_count': int
            }
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(urls),
            'success_count': 0,
            'fail_count': 0
        }

        for idx, url in enumerate(urls, 1):
            if progress_callback:
                progress_callback(idx, len(urls), f"Processing {idx}/{len(urls)}: {url}")

            # Download the reel
            success, video_path, error = self.download_reel(
                url,
                progress_callback=lambda msg: progress_callback(idx, len(urls), msg) if progress_callback else None
            )

            if success:
                results['successful'].append((url, video_path))
                results['success_count'] += 1
            else:
                results['failed'].append((url, error))
                results['fail_count'] += 1

            # Add delay between downloads to avoid rate limiting
            if idx < len(urls):
                time.sleep(delay_between_downloads)

        return results

    def cleanup_downloads(self):
        """Remove all downloaded files."""
        if os.path.exists(self.output_folder):
            import shutil
            shutil.rmtree(self.output_folder)
            os.makedirs(self.output_folder, exist_ok=True)


# Standalone function for simple use
def download_instagram_reel(url: str, output_folder: str = "./downloads") -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Simple function to download a single reel without using the class.

    Args:
        url: Instagram URL
        output_folder: Where to save the video

    Returns:
        Tuple of (success, video_path, error_message)
    """
    downloader = InstagramDownloader(output_folder)
    return downloader.download_reel(url)
