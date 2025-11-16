#!/usr/bin/env python3
"""
Install Playwright Browser

This script installs the Chromium browser needed by Playwright.
Run this ONCE after installing Python dependencies.
"""

import subprocess
import sys

def main():
    print("=" * 60)
    print("Installing Playwright Browser (Chromium)")
    print("=" * 60)
    print()
    print("This will download and install Chromium (~300MB).")
    print("You only need to run this ONCE after installing requirements.txt")
    print()

    try:
        # Install Playwright browsers
        print("Installing Chromium browser...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✓ SUCCESS!")
            print("=" * 60)
            print()
            print("Chromium browser installed successfully!")
            print("You can now run the application with: python main.py")
            print()
            return 0
        else:
            print()
            print("=" * 60)
            print("✗ ERROR")
            print("=" * 60)
            print()
            print("Failed to install browser:")
            print(result.stderr)
            print()
            print("Try installing manually:")
            print("  playwright install chromium")
            return 1

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ ERROR")
        print("=" * 60)
        print()
        print(f"An error occurred: {e}")
        print()
        print("Make sure Playwright is installed:")
        print("  pip install playwright")
        print()
        print("Then try installing browsers manually:")
        print("  playwright install chromium")
        return 1

if __name__ == "__main__":
    sys.exit(main())
