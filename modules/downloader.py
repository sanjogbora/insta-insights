"""
Instagram Downloader Module
Handles downloading Instagram reels using Playwright browser automation with network interception.
"""

import os
import time
import re
import requests
from typing import Optional, Callable, List, Tuple
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class InstagramDownloader:
    """Handles downloading Instagram reels using Playwright with network interception."""

    def __init__(self, output_folder: str = "./downloads", selected_browser: str = "auto"):
        """
        Initialize the Instagram downloader.

        Args:
            output_folder: Folder to save downloaded reels
            selected_browser: Not used (kept for compatibility)
        """
        self.output_folder = output_folder
        self.username = None  # For compatibility
        self.selected_browser = selected_browser
        self.browser_in_use = "playwright"

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def setup_instaloader(self, session_file: Optional[str] = None, auto_load_session: bool = True):
        """
        Dummy method for backward compatibility with GUI.

        Args:
            session_file: Ignored (kept for compatibility)
            auto_load_session: Ignored (kept for compatibility)
        """
        print("✓ Using Playwright browser automation - no authentication needed!")

    def set_browser(self, browser: str):
        """
        Set which browser to use (not used for Playwright).

        Args:
            browser: Ignored (kept for compatibility)
        """
        pass

    def login(self, username: str, password: str, two_factor_callback: Optional[Callable[[], str]] = None) -> bool:
        """
        Login method for backward compatibility.
        Playwright visits pages like a normal browser - no login needed!

        Args:
            username: Ignored
            password: Ignored
            two_factor_callback: Ignored

        Returns:
            Always returns True
        """
        print("ℹ️  Using browser automation - no login needed")
        return True

    def is_logged_in(self) -> bool:
        """
        Check login status.

        Returns:
            Always True (no login needed)
        """
        return True

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
        Download a single Instagram reel using Playwright with network interception.

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

        # Try to download with retries
        for attempt in range(max_retries):
            try:
                if progress_callback:
                    progress_callback(f"Launching browser... (attempt {attempt + 1}/{max_retries})")

                # Use Playwright to capture video URL from network traffic
                video_url = self._capture_video_url_from_network(url, progress_callback)

                if not video_url:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(f"Could not find video URL, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return False, None, "Could not find video URL - reel might be private or deleted"

                # Download the video from CDN
                if progress_callback:
                    progress_callback(f"Downloading from CDN...")

                response = requests.get(video_url, stream=True, timeout=30)
                response.raise_for_status()

                # Save video
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Verify download
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    if progress_callback:
                        progress_callback(f"✓ Successfully downloaded: {shortcode}")
                    return True, output_path, None
                else:
                    if attempt < max_retries - 1:
                        if progress_callback:
                            progress_callback(f"Download incomplete, retrying...")
                        time.sleep(retry_delay)
                    else:
                        return False, None, "Downloaded file is too small or corrupt"

            except requests.RequestException as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"Network error, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Download failed: {error_msg[:200]}"

            except PlaywrightTimeout as e:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"Timeout, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    return False, None, "Timeout while loading Instagram page"

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"Error: {error_msg[:100]}, retrying...")
                    time.sleep(retry_delay)
                else:
                    return False, None, f"Error: {error_msg[:300]}"

        return False, None, "Download failed after all retries"

    def _capture_video_url_from_network(
        self,
        url: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Use Playwright to visit Instagram page and capture video URL from network traffic.

        Args:
            url: Instagram reel URL
            progress_callback: Optional callback for progress updates

        Returns:
            Video CDN URL if found, None otherwise
        """
        video_url = None

        def handle_response(response):
            """Capture video URLs from network responses."""
            nonlocal video_url
            try:
                # Look for .mp4 video files in network traffic
                response_url = response.url
                if '.mp4' in response_url and response.status == 200:
                    # Instagram video CDN URLs contain .mp4
                    if any(domain in response_url for domain in ['cdninstagram', 'fbcdn', 'instagram']):
                        video_url = response_url
                        if progress_callback:
                            progress_callback(f"✓ Captured video URL from network")
            except:
                pass

        try:
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = context.new_page()

                # Set up response listener to capture video URLs
                page.on('response', handle_response)

                if progress_callback:
                    progress_callback("Loading Instagram page...")

                # Visit the page
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait a bit for video to load
                time.sleep(3)

                # Try to click play button if it exists (sometimes needed to trigger video load)
                try:
                    play_button = page.locator('button[aria-label*="Play"], button[aria-label*="play"]').first
                    if play_button.is_visible(timeout=2000):
                        play_button.click()
                        time.sleep(2)
                except:
                    pass

                browser.close()

                return video_url

        except Exception as e:
            if progress_callback:
                progress_callback(f"Browser error: {str(e)[:100]}")
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
        browser: Not used (kept for compatibility)

    Returns:
        Tuple of (success, video_path, error_message)
    """
    downloader = InstagramDownloader(output_folder, browser)
    return downloader.download_reel(url)
