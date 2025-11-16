"""
Instagram Downloader Module
Handles downloading Instagram reels using Playwright browser automation.
Zero authentication required - works like visiting Instagram in your browser!
"""

import os
import time
import re
import requests
from typing import Optional, Callable, List, Tuple
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class InstagramDownloader:
    """Handles downloading Instagram reels using browser automation (zero auth!)."""

    def __init__(self, output_folder: str = "./downloads"):
        """
        Initialize the Instagram downloader.

        Args:
            output_folder: Folder to save downloaded reels
        """
        self.output_folder = output_folder
        self.username = None  # For compatibility with old interface
        self.browser = None
        self.playwright = None

        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    def setup_instaloader(self, session_file: Optional[str] = None, auto_load_session: bool = True):
        """
        Dummy method for backward compatibility with GUI.
        Playwright doesn't need setup - it works out of the box!

        Args:
            session_file: Ignored (kept for compatibility)
            auto_load_session: Ignored (kept for compatibility)
        """
        print("✓ Using Playwright browser automation - zero authentication required!")
        print("✓ Works for all public Instagram reels - no login needed!")

    def login(self, username: str, password: str, two_factor_callback: Optional[Callable[[], str]] = None) -> bool:
        """
        Login method for backward compatibility.
        Playwright doesn't need login for public Instagram reels!

        Args:
            username: Ignored
            password: Ignored
            two_factor_callback: Ignored

        Returns:
            Always returns True (no login needed)
        """
        print("ℹ️  Playwright doesn't require login for public Instagram content")
        print("✓ Ready to download public reels using browser automation!")
        return True

    def is_logged_in(self) -> bool:
        """
        Check login status (always False for Playwright).

        Returns:
            False (Playwright doesn't use login)
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
        Download a single Instagram reel using Playwright browser automation.

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

        # Retry logic
        for attempt in range(max_retries):
            try:
                if progress_callback:
                    progress_callback(f"Launching browser automation... (attempt {attempt + 1}/{max_retries})")

                with sync_playwright() as p:
                    # Launch browser in headless mode
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-blink-features=AutomationControlled'
                        ]
                    )

                    # Create context with realistic browser settings
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080},
                        locale='en-US',
                        timezone_id='America/New_York',
                        extra_http_headers={
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        }
                    )

                    page = context.new_page()

                    # Track video URL from network requests
                    video_url = None
                    video_urls = []

                    def handle_response(response):
                        nonlocal video_url, video_urls
                        try:
                            # Look for video file in response
                            if response.status == 200:
                                content_type = response.headers.get('content-type', '')
                                url_lower = response.url.lower()

                                # Check if it's a video
                                if ('video' in content_type or
                                    '.mp4' in url_lower or
                                    'video' in url_lower):
                                    # Prefer Instagram CDN URLs
                                    if 'cdninstagram.com' in response.url or 'fbcdn.net' in response.url:
                                        video_urls.append(response.url)
                                        if not video_url:
                                            video_url = response.url
                        except Exception:
                            pass  # Ignore errors in response handler

                    page.on('response', handle_response)

                    try:
                        if progress_callback:
                            progress_callback(f"Loading Instagram page...")

                        # Navigate to the reel
                        page.goto(url, wait_until='networkidle', timeout=30000)

                        # Wait for video to load
                        time.sleep(3)

                        # Try to find and click play button (sometimes needed)
                        try:
                            play_button = page.query_selector('button[aria-label*="Play"], video')
                            if play_button:
                                play_button.click()
                                time.sleep(2)
                        except:
                            pass  # Play button might not exist

                        # Scroll a bit to trigger video load
                        page.evaluate('window.scrollTo(0, 100)')
                        time.sleep(2)

                        # Check if we captured video URL
                        if video_url:
                            if progress_callback:
                                progress_callback(f"Found video URL, downloading...")

                            # Download the video
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Referer': 'https://www.instagram.com/',
                                'Accept': '*/*',
                            }

                            response = requests.get(video_url, headers=headers, stream=True, timeout=60)
                            response.raise_for_status()

                            # Save video file
                            with open(output_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)

                            browser.close()

                            # Verify file was downloaded
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                if progress_callback:
                                    progress_callback(f"✓ Successfully downloaded: {shortcode}")
                                return True, output_path, None
                            else:
                                os.remove(output_path) if os.path.exists(output_path) else None
                                raise Exception("Downloaded file is too small or empty")

                        else:
                            browser.close()

                            # Try alternative: look for video element in page
                            if progress_callback:
                                progress_callback(f"Video URL not captured, trying alternative method...")

                            # This is a fallback - might not always work
                            raise Exception("Could not capture video URL from network requests")

                    except PlaywrightTimeout:
                        browser.close()
                        raise Exception("Timeout while loading Instagram page")

            except Exception as e:
                error_msg = str(e)

                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(
                            f"Attempt {attempt + 1} failed: {error_msg[:50]}... Retrying..."
                        )
                    time.sleep(retry_delay)
                else:
                    # Last attempt failed
                    if "private" in error_msg.lower():
                        return False, None, "This reel is private - cannot download without authentication"
                    elif "not available" in error_msg.lower() or "removed" in error_msg.lower():
                        return False, None, "Reel has been deleted or is unavailable"
                    elif "timeout" in error_msg.lower():
                        return False, None, "Timeout while loading reel - Instagram might be slow or blocking"
                    else:
                        return False, None, f"Download failed after {max_retries} attempts: {error_msg}"

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

            # Add delay between downloads to be respectful
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
        Playwright doesn't use sessions.

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
