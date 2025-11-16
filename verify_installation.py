#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all required dependencies are installed correctly.
"""

import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False


def check_module(module_name, import_name=None):
    """Check if a Python module is installed."""
    if import_name is None:
        import_name = module_name

    print(f"Checking {module_name}...", end=" ")
    try:
        __import__(import_name)
        print("✓")
        return True
    except ImportError:
        print("✗")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("Checking FFmpeg...", end=" ")
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            print("✓")
            return True
        else:
            print("✗")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗")
        return False


def check_gpu():
    """Check if GPU is available (CUDA/MPS/ROCm)."""
    print("Checking GPU...", end=" ")
    try:
        # Try to use DeviceManager for better detection
        try:
            from modules.device_manager import DeviceManager
            manager = DeviceManager()
            manager.detect_best_device()

            if manager.is_gpu_available():
                device_name = manager.get_friendly_name()
                device_type = manager.device_type.upper()
                print(f"✓ {device_name} ({device_type})")
                return True
            else:
                print("✗ (CPU only - this is okay, just slower)")
                return False
        except ImportError:
            # Fallback to basic CUDA check if DeviceManager not available
            import torch
            if torch.cuda.is_available():
                print(f"✓ {torch.cuda.get_device_name(0)} (CUDA)")
                return True
            else:
                print("✗ (CPU only - this is okay, just slower)")
                return False
    except:
        print("✗ (CPU only)")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Instagram Reel Transcriber - Installation Verification")
    print("=" * 60)
    print()

    checks = []

    # Python version
    checks.append(("Python 3.8+", check_python_version()))

    print()
    print("Checking Python packages...")
    print("-" * 60)

    # Required packages
    packages = [
        ("yt-dlp", "yt_dlp"),
        ("openai-whisper", "whisper"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("tqdm", "tqdm"),
        ("customtkinter", "customtkinter"),
        ("Pillow", "PIL"),
        ("moviepy", "moviepy"),
        ("torch", "torch"),
    ]

    for package_name, import_name in packages:
        checks.append((package_name, check_module(package_name, import_name)))

    print()
    print("Checking system dependencies...")
    print("-" * 60)

    # FFmpeg
    checks.append(("FFmpeg", check_ffmpeg()))

    print()
    print("Checking optional features...")
    print("-" * 60)

    # GPU (optional)
    gpu_available = check_gpu()

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    required_checks = [check for check in checks if check[0] != "GPU (CUDA)"]
    passed = sum(1 for _, result in required_checks if result)
    total = len(required_checks)

    print(f"Required checks passed: {passed}/{total}")

    if passed == total:
        print()
        print("✓ All required dependencies are installed!")
        print()
        print("You can now run the application with:")
        print("  python main.py")
        print()
        if not gpu_available:
            print("Note: GPU not available. Transcription will use CPU (slower).")
            print("For GPU support, install CUDA and reinstall PyTorch with CUDA support.")
        return 0
    else:
        print()
        print("✗ Some dependencies are missing!")
        print()
        print("To install missing dependencies:")
        print("  pip install -r requirements.txt")
        print()
        if not checks[required_checks.index(("FFmpeg", checks[-1][1]))][1]:
            print("FFmpeg installation instructions:")
            print("  Windows: Download from ffmpeg.org and add to PATH")
            print("  macOS: brew install ffmpeg")
            print("  Linux: sudo apt install ffmpeg")
        return 1


if __name__ == "__main__":
    sys.exit(main())
