#!/usr/bin/env python3
"""
Test script to verify Instagram download fix is working.
This tests the updated downloader with improved anti-bot measures.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.downloader import InstagramDownloader


def test_download(url: str, use_login: bool = False):
    """
    Test downloading a single Instagram reel.

    Args:
        url: Instagram reel URL to test
        use_login: Whether to attempt login
    """
    print("=" * 60)
    print("Instagram Download Test")
    print("=" * 60)
    print(f"\nTesting URL: {url}")
    print(f"Using login: {use_login}\n")

    # Create downloader instance
    downloader = InstagramDownloader("./test_downloads")

    # Setup with improved anti-bot measures
    print("Setting up downloader with anti-bot measures...")
    downloader.setup_instaloader()
    print("✓ Downloader configured with:")
    print("  - Realistic User-Agent")
    print("  - Randomized rate limiting (2-4 seconds)")
    print("  - Session management")

    # Optional: Login
    if use_login:
        username = input("\nEnter Instagram username: ")
        password = input("Enter Instagram password: ")

        print("\nAttempting to login...")
        if downloader.login(username, password):
            print("✓ Successfully logged in")
        else:
            print("✗ Login failed - continuing without authentication")

    # Download the reel
    print(f"\nAttempting to download reel...")
    print("-" * 60)

    success, video_path, error = downloader.download_reel(
        url,
        progress_callback=lambda msg: print(f"  {msg}")
    )

    print("-" * 60)

    # Display results
    if success:
        print("\n✓ SUCCESS!")
        print(f"Video downloaded to: {video_path}")
        print("\nThe fix is working! You can now use the main application.")
    else:
        print("\n✗ FAILED")
        print(f"Error: {error}")
        print("\nPlease try the following:")
        print("1. Run again with login: python test_download.py --login")
        print("2. Install browser_cookie3: pip install browser_cookie3")
        print("3. See TROUBLESHOOTING.md for more solutions")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Default test URL (you can change this to your URL)
    test_url = "https://www.instagram.com/reel/C_example/"

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python test_download.py [URL] [--login]")
            print("\nExamples:")
            print("  python test_download.py https://www.instagram.com/reel/ABC123/")
            print("  python test_download.py https://www.instagram.com/reel/ABC123/ --login")
            sys.exit(0)

        # Check if --login flag is present
        use_login = "--login" in sys.argv

        # Get URL if provided
        for arg in sys.argv[1:]:
            if arg.startswith("http"):
                test_url = arg
                break
    else:
        use_login = False

    # Prompt for URL if default is still set
    if test_url == "https://www.instagram.com/reel/C_example/":
        test_url = input("Enter Instagram reel URL to test: ").strip()

        if not test_url:
            print("Error: No URL provided")
            sys.exit(1)

        # Ask if they want to login
        login_choice = input("Do you want to login to Instagram? (y/n): ").strip().lower()
        use_login = login_choice in ['y', 'yes']

    # Run the test
    try:
        test_download(test_url, use_login)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
