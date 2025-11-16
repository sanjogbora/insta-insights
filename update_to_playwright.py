#!/usr/bin/env python3
"""
Update Script - Switch to Playwright
Pulls latest code and updates to Playwright-based downloader
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("UPDATE TO PLAYWRIGHT - ZERO AUTHENTICATION!")
    print("=" * 60)
    print()
    print("This will:")
    print("  1. Pull latest code from git")
    print("  2. Uninstall yt-dlp")
    print("  3. Install Playwright")
    print("  4. Install Chromium browser")
    print()
    input("Press Enter to continue or Ctrl+C to cancel...")

    # Step 1: Git pull
    if not run_command("git pull", "Step 1: Pulling latest code..."):
        print("\n❌ Failed to pull code. Make sure you're in the git repository.")
        return 1

    # Step 2: Uninstall yt-dlp
    run_command(f"{sys.executable} -m pip uninstall -y yt-dlp",
                "Step 2: Uninstalling yt-dlp...")

    # Step 3: Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt",
                      "Step 3: Installing new requirements (Playwright)..."):
        print("\n❌ Failed to install requirements.")
        return 1

    # Step 4: Install Playwright browsers
    if not run_command(f"{sys.executable} install_browser.py",
                      "Step 4: Installing Chromium browser..."):
        print("\n❌ Failed to install browser. Try manually:")
        print("  python install_browser.py")
        return 1

    print("\n" + "=" * 60)
    print("✅ UPDATE COMPLETE!")
    print("=" * 60)
    print()
    print("You're now using Playwright - ZERO authentication required!")
    print()
    print("Changes:")
    print("  ✓ Removed: yt-dlp (and browser cookie issues)")
    print("  ✓ Added: Playwright browser automation")
    print("  ✓ Result: No login, no cookies, no authentication needed!")
    print()
    print("You can now run the app:")
    print("  python main.py")
    print()
    print("See PLAYWRIGHT_USAGE_GUIDE.md for details.")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nUpdate cancelled by user.")
        sys.exit(1)
