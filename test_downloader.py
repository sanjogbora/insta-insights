#!/usr/bin/env python3
"""
Quick test script for the yt-dlp downloader.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly to avoid loading all dependencies
import importlib.util
spec = importlib.util.spec_from_file_location("downloader", "modules/downloader.py")
downloader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloader_module)
InstagramDownloader = downloader_module.InstagramDownloader

def test_download():
    """Test downloading a single reel."""
    # Test URL provided by user
    test_url = "https://www.instagram.com/reel/DNgJb4Hs5FZ/?utm_source=ig_web_copy_link"

    print("=" * 70)
    print("Testing yt-dlp Instagram Downloader")
    print("=" * 70)
    print()
    print(f"Test URL: {test_url}")
    print()

    downloader = InstagramDownloader(output_folder="./test_downloads")
    downloader.setup_instaloader()

    print()
    print("Starting download...")
    print()

    success, video_path, error = downloader.download_reel(
        test_url,
        progress_callback=lambda msg: print(f"  {msg}")
    )

    print()
    print("=" * 70)
    if success:
        print("✓ SUCCESS!")
        print(f"Video downloaded to: {video_path}")

        # Check file size
        if os.path.exists(video_path):
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"File size: {size_mb:.2f} MB")
    else:
        print("✗ FAILED!")
        print(f"Error: {error}")
    print("=" * 70)

    return success

if __name__ == "__main__":
    try:
        success = test_download()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
