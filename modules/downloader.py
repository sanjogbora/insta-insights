"""
Instagram Downloader Module
Handles downloading Instagram reels using yt-dlp (no authentication needed!).
"""

import yt_dlp
import os
import time
import re
from typing import Optional, Callable, List, Tuple
from pathlib import Path


class InstagramDownloader:
    """Handles downloading Instagram reels using yt-dlp."""

    def __init__(self, output_folder: str = "./downloads"):
        """
        Initialize the Instagram downloader.

        Args:
            output_folder: Folder to save downloaded reels
        """
        self.output_folder = output_folder
        self.username = None  # For compatibility with old interface

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def setup_instaloader(self, session_file: Optional[str] = None, auto_load_session: bool = True):
        """
        Dummy method for backward compatibility with GUI.
        yt-dlp doesn't need setup - it works out of the box!

        Args:
            session_file: Ignored (kept for compatibility)
            auto_load_session: Ignored (kept for compatibility)
        """
        print("✓ Using yt-dlp - no authentication required for public content!")

    def login(self, username: str, password: str, two_factor_callback: Optional[Callable[[], str]] = None) -> bool:
        """
        Login method for backward compatibility.
        yt-dlp doesn't need login for public Instagram reels!

        Args:
            username: Ignored
            password: Ignored
            two_factor_callback: Ignored

        Returns:
            Always returns True (no login needed)
        """
        print("ℹ️  yt-dlp doesn't require login for public Instagram content")
        print("✓ Ready to download public reels!")
        return True

    def is_logged_in(self) -> bool:
        """
        Check login status (always False for yt-dlp).

        Returns:
            False (yt-dlp doesn't use login)
        """
        return False

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
        Download a single Instagram reel using yt-dlp.

        Args:
            url: Instagram reel URL
            progress_callback: Optional callback function for progress updates
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Tuple of (success: bool, video_path: str or None, error_message: str or None)
        """
        shortcode = self.extract_shortcode_from_url(url)
        if not shortcode:
            return False, None, f"Invalid Instagram URL: {url}"

        if progress_callback:
            progress_callback(f"Downloading reel: {shortcode}")

        # Create output path
        output_path = os.path.join(self.output_folder, f"{shortcode}.mp4")

        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer mp4, fallback to best
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'retries': max_retries,
            'fragment_retries': max_retries,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            # Add more headers to look like a real browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }

        # Try to use browser cookies (like Chrome extensions do!) to avoid 403 errors
        # This requires being logged into Instagram in your browser
        cookies_loaded = False
        for browser in ['chrome', 'firefox', 'edge', 'safari']:
            try:
                # Test if cookies can be loaded
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'cookiesfrombrowser': (browser,)}) as test_ydl:
                    pass  # Just test if it works
                ydl_opts['cookiesfrombrowser'] = (browser,)
                cookies_loaded = True
                if progress_callback:
                    progress_callback(f"Using {browser.title()} cookies")
                break
            except:
                # Browser not found or cookies inaccessible, try next
                continue

        if not cookies_loaded and progress_callback:
            progress_callback("No browser cookies found - may encounter 403 errors")

        # Retry logic
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Check if file was downloaded
                if os.path.exists(output_path):
                    if progress_callback:
                        progress_callback(f"Successfully downloaded: {shortcode}")
                    return True, output_path, None
                else:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(
                                f"Download incomplete, retrying... (attempt {attempt + 1}/{max_retries})"
                            )
                        time.sleep(retry_delay)
                    else:
                        return False, None, f"Video file not found after download: {shortcode}"

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)

                # Check for specific errors
                if "private" in error_msg.lower():
                    return False, None, "This reel is private - cannot download"
                elif "not available" in error_msg.lower() or "removed" in error_msg.lower():
                    return False, None, "Reel has been deleted or is unavailable"
                elif "403" in error_msg or "forbidden" in error_msg.lower():
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(
                                f"Rate limited, retrying... (attempt {attempt + 1}/{max_retries})"
                            )
                        time.sleep(retry_delay * 2)  # Wait longer for rate limits
                    else:
                        return False, None, "Instagram blocked the request (403 Forbidden). Try again later."
                else:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(
                                f"Error occurred, retrying... (attempt {attempt + 1}/{max_retries})"
                            )
                        time.sleep(retry_delay)
                    else:
                        return False, None, f"Download failed: {error_msg}"

            except Exception as e:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(
                            f"Unexpected error, retrying... (attempt {attempt + 1}/{max_retries})"
                        )
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Error downloading reel: {str(e)}"

        return False, None, "Download failed after all retries"

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

    def save_session(self, username: str, session_path: str):
        """
        Dummy method for backward compatibility.
        yt-dlp doesn't use sessions.

        Args:
            username: Ignored
            session_path: Ignored
        """
        pass


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
