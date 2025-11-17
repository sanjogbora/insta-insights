"""
Instagram Downloader Module
Handles downloading Instagram reels using yt-dlp with browser cookie support.
"""

import yt_dlp
import os
import time
import re
from typing import Optional, Callable, List, Tuple
from pathlib import Path


class InstagramDownloader:
    """Handles downloading Instagram reels using yt-dlp with browser cookies."""

    def __init__(self, output_folder: str = "./downloads", selected_browser: str = "auto"):
        """
        Initialize the Instagram downloader.

        Args:
            output_folder: Folder to save downloaded reels
            selected_browser: Browser to use for cookies ('auto', 'chrome', 'firefox', 'edge', 'safari')
        """
        self.output_folder = output_folder
        self.username = None  # For compatibility
        self.selected_browser = selected_browser
        self.browser_in_use = None

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def setup_instaloader(self, session_file: Optional[str] = None, auto_load_session: bool = True):
        """
        Dummy method for backward compatibility with GUI.

        Args:
            session_file: Ignored (kept for compatibility)
            auto_load_session: Ignored (kept for compatibility)
        """
        print("✓ Using yt-dlp with browser session support!")

    def set_browser(self, browser: str):
        """
        Set which browser to use for cookie extraction.

        Args:
            browser: 'auto', 'chrome', 'firefox', 'edge', or 'safari'
        """
        self.selected_browser = browser
        self.browser_in_use = None

    def login(self, username: str, password: str, two_factor_callback: Optional[Callable[[], str]] = None) -> bool:
        """
        Login method for backward compatibility.
        yt-dlp uses browser cookies, no manual login needed!

        Args:
            username: Ignored
            password: Ignored
            two_factor_callback: Ignored

        Returns:
            Always returns True
        """
        print("ℹ️  Using browser session - no manual login needed")
        return True

    def is_logged_in(self) -> bool:
        """
        Check login status.

        Returns:
            True if browser cookies are being used
        """
        return self.browser_in_use is not None

    @staticmethod
    def extract_shortcode_from_url(url: str) -> Optional[str]:
        """
        Extract the shortcode (reel ID) from Instagram URL.

        Args:
            url: Instagram URL

        Returns:
            Shortcode if found, None otherwise
        """
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
        Download a single Instagram reel using yt-dlp with browser cookies.

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

        # Check if already downloaded
        if os.path.exists(output_path):
            if progress_callback:
                progress_callback(f"Already downloaded: {shortcode}")
            return True, output_path, None

        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'retries': max_retries,
            'fragment_retries': max_retries,
            'ignoreerrors': False,
            'nocheckcertificate': True,
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

        # Try to load cookies
        cookies_loaded = False

        # PRIORITY 1: Check for manual cookie file (bypasses Windows DPAPI encryption)
        cookie_file_path = Path(__file__).parent.parent / 'instagram_cookies.txt'
        if cookie_file_path.exists():
            try:
                ydl_opts['cookiefile'] = str(cookie_file_path)
                cookies_loaded = True
                self.browser_in_use = "manual_cookies"
                if progress_callback:
                    progress_callback("✓ Using manual cookie file (instagram_cookies.txt)")
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️  Manual cookie file found but error: {str(e)[:100]}")

        # PRIORITY 2: Try browser cookies (only if manual cookie file not found)
        if not cookies_loaded:
            if self.selected_browser == "auto":
                # Try browsers in order: Firefox → Edge → Safari → Chrome
                browsers_to_try = ['firefox', 'edge', 'safari', 'chrome']
            else:
                # Use user-selected browser
                browsers_to_try = [self.selected_browser]

            for browser in browsers_to_try:
                try:
                    # Test if cookies can be loaded
                    test_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'cookiesfrombrowser': (browser,),
                        'extract_flat': True
                    }
                    with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                        pass  # Just test if it works

                    # Success! Use this browser
                    ydl_opts['cookiesfrombrowser'] = (browser,)
                    cookies_loaded = True
                    self.browser_in_use = browser
                    if progress_callback:
                        progress_callback(f"✓ Using {browser.title()} session")
                    break

                except Exception as e:
                    error_str = str(e)
                    if 'could not copy' in error_str.lower() and browser == 'chrome':
                        if progress_callback and self.selected_browser == browser:
                            progress_callback(f"⚠️  {browser.title()} is running - close it or select another browser")
                    continue

        if not cookies_loaded:
            if progress_callback:
                if self.selected_browser != "auto":
                    progress_callback(f"⚠️  Could not load {self.selected_browser.title()} session")
                    progress_callback(f"ℹ️  Make sure you're logged into Instagram in {self.selected_browser.title()}")
                    progress_callback("💡 OR: Export cookies manually (see export_cookies_instructions.md)")
                else:
                    progress_callback("⚠️  No browser sessions found")
                    progress_callback("💡 Solution: Export cookies manually (see export_cookies_instructions.md)")
                    progress_callback("ℹ️  Save as 'instagram_cookies.txt' in project folder")

        # Retry logic
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Check if file was downloaded
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    if progress_callback:
                        progress_callback(f"✓ Successfully downloaded: {shortcode}")
                    return True, output_path, None
                else:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(f"Retry {attempt + 1}/{max_retries}...")
                        time.sleep(retry_delay)
                    else:
                        return False, None, f"Video file not found after download"

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)

                # Log full error for debugging
                if progress_callback:
                    progress_callback(f"DEBUG: {error_msg}")

                if "403" in error_msg or "forbidden" in error_msg.lower():
                    if not cookies_loaded:
                        return False, None, "403 Forbidden - Please import your browser session first"
                    elif attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(f"Rate limited, waiting {retry_delay * 2}s... ({attempt + 2}/{max_retries})")
                        time.sleep(retry_delay * 2)
                    else:
                        return False, None, f"Instagram blocked request: {error_msg[:200]}"
                elif "private" in error_msg.lower():
                    return False, None, "This reel is private"
                elif "unavailable" in error_msg.lower() or "not available" in error_msg.lower():
                    return False, None, "Video unavailable or deleted"
                elif "login" in error_msg.lower() or "sign" in error_msg.lower():
                    return False, None, f"Login required: {error_msg[:200]}"
                else:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(f"Error: {error_msg[:100]}")
                            progress_callback(f"Retrying in {retry_delay}s... ({attempt + 2}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        return False, None, f"Download failed: {error_msg[:300]}"

            except Exception as e:
                error_msg = str(e)
                if progress_callback:
                    progress_callback(f"DEBUG: Unexpected error - {error_msg}")

                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"Retrying in {retry_delay}s... ({attempt + 2}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Error: {error_msg[:300]}"

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
            Dictionary with download results
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

            # Add delay between downloads
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

        Args:
            username: Ignored
            session_path: Ignored
        """
        pass


# Standalone function for simple use
def download_instagram_reel(url: str, output_folder: str = "./downloads", browser: str = "auto") -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Simple function to download a single reel.

    Args:
        url: Instagram URL
        output_folder: Where to save the video
        browser: Which browser to use for cookies

    Returns:
        Tuple of (success, video_path, error_message)
    """
    downloader = InstagramDownloader(output_folder, browser)
    return downloader.download_reel(url)
