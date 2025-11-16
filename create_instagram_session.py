#!/usr/bin/env python3
"""
Instagram Session Creator
Creates a session file for use with the Instagram Reel Transcriber.
This handles 2FA authentication interactively.

Usage:
    python create_instagram_session.py

The script will:
1. Ask for your Instagram username and password
2. Handle 2FA code if required
3. Save a session file that can be imported into the main app
"""

import instaloader
import sys
import os
from getpass import getpass


def create_session():
    """Create an Instagram session file with 2FA support."""
    print("=" * 70)
    print("Instagram Session Creator")
    print("=" * 70)
    print()
    print("This tool will help you create a session file for Instagram login.")
    print("If you have 2FA enabled, you'll be prompted for the code.")
    print()

    # Get credentials
    username = input("Instagram username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return False

    password = getpass("Instagram password: ")
    if not password:
        print("Error: Password cannot be empty")
        return False

    print()
    print("Logging in to Instagram...")
    print()

    # Create instaloader instance
    loader = instaloader.Instaloader()

    try:
        # Login (this will prompt for 2FA if needed)
        loader.login(username, password)

        print()
        print("✓ Login successful!")
        print()

        # Save session
        session_dir = os.path.join(os.path.dirname(__file__), "config")
        os.makedirs(session_dir, exist_ok=True)

        session_file = os.path.join(session_dir, f"instagram_session_{username}")
        loader.save_session_to_file(session_file)

        print(f"✓ Session saved to: {session_file}")
        print()
        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print()
        print("You can now use this session in the main application:")
        print()
        print("Option 1: The app will automatically detect and use this session")
        print("Option 2: Manually import it in the GUI settings")
        print()
        print(f"Session file location: {session_file}")
        print()
        print("Note: Sessions expire after some time. If you get login errors,")
        print("run this script again to create a fresh session.")
        print()

        return True

    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print()
        print("✗ Two-factor authentication is required.")
        print()
        print("The 2FA code should be prompted above.")
        print("If not, please try again or check your Instagram app.")
        return False

    except instaloader.exceptions.BadCredentialsException:
        print()
        print("✗ Login failed: Invalid username or password")
        print()
        print("Please check your credentials and try again.")
        return False

    except instaloader.exceptions.ConnectionException as e:
        print()
        print(f"✗ Connection error: {e}")
        print()
        print("Please check your internet connection and try again.")
        return False

    except Exception as e:
        print()
        print(f"✗ Login failed: {e}")
        print()
        print("Common issues:")
        print("- Instagram may be blocking automated logins")
        print("- Your account may have security restrictions")
        print("- Try logging in from Instagram app/website first")
        return False


def main():
    """Main entry point."""
    success = create_session()

    if success:
        sys.exit(0)
    else:
        print()
        print("Session creation failed. Please try again or contact support.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
