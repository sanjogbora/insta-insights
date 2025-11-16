#!/usr/bin/env python3
"""
GPU Diagnostic and PyTorch CUDA Setup Guide
Helps diagnose GPU issues and provides installation instructions for CUDA support.
"""

import subprocess
import sys
import platform
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.device_manager import DeviceManager
    HAS_DEVICE_MANAGER = True
except ImportError:
    HAS_DEVICE_MANAGER = False


def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1


def detect_gpu():
    """Detect GPU type."""
    print("=" * 70)
    print("GPU DETECTION")
    print("=" * 70)
    print()

    os_type = platform.system()

    if os_type == "Linux":
        # Try lspci
        output, code = run_command("lspci | grep -i 'vga\\|3d\\|display'")
        if code == 0 and output:
            print("Detected GPU(s):")
            print(output)
            print()

            if "nvidia" in output.lower():
                return "nvidia"
            elif "amd" in output.lower() or "radeon" in output.lower():
                return "amd"
            elif "intel" in output.lower():
                return "intel"

    elif os_type == "Windows":
        # Try wmic
        output, code = run_command("wmic path win32_VideoController get name")
        if code == 0 and output:
            print("Detected GPU(s):")
            print(output)
            print()

            if "nvidia" in output.lower():
                return "nvidia"
            elif "amd" in output.lower() or "radeon" in output.lower():
                return "amd"
            elif "intel" in output.lower():
                return "intel"

    elif os_type == "Darwin":  # macOS
        output, code = run_command("system_profiler SPDisplaysDataType")
        if code == 0 and output:
            print("Detected GPU(s):")
            print(output[:500])  # First 500 chars
            print()

            if "nvidia" in output.lower():
                return "nvidia"
            elif "amd" in output.lower() or "radeon" in output.lower():
                return "amd"
            elif "intel" in output.lower():
                return "intel"

    print("⚠ Could not automatically detect GPU")
    print()
    return "unknown"


def check_nvidia_driver():
    """Check if NVIDIA driver is installed."""
    print("=" * 70)
    print("NVIDIA DRIVER CHECK")
    print("=" * 70)
    print()

    output, code = run_command("nvidia-smi")
    if code == 0:
        print("✓ NVIDIA driver is installed!")
        print()
        print(output)
        print()
        return True
    else:
        print("✗ NVIDIA driver not found")
        print()
        return False


def check_pytorch_cuda():
    """Check PyTorch CUDA configuration."""
    print("=" * 70)
    print("PYTORCH CUDA CHECK")
    print("=" * 70)
    print()

    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"CUDA version (built with): {torch.version.cuda if torch.version.cuda else 'None (CPU-only)'}")

        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"Current CUDA device: {torch.cuda.current_device()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print()
            print("⚠ PyTorch is installed but CUDA is not available")
            return False
    except ImportError:
        print("⚠ PyTorch is not installed yet")
        return False
    except Exception as e:
        print(f"⚠ Error checking PyTorch: {e}")
        return False


def get_cuda_install_command():
    """Get the correct PyTorch installation command for CUDA."""
    print()
    print("=" * 70)
    print("PYTORCH INSTALLATION INSTRUCTIONS")
    print("=" * 70)
    print()

    print("To install PyTorch with CUDA support, visit:")
    print("👉 https://pytorch.org/get-started/locally/")
    print()
    print("Recommended installation commands:")
    print()
    print("For CUDA 11.8 (most compatible):")
    print("-" * 70)
    print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print()
    print("For CUDA 12.1:")
    print("-" * 70)
    print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    print()
    print("For CPU-only (no GPU):")
    print("-" * 70)
    print("pip3 install torch torchvision torchaudio")
    print()


def main():
    """Main diagnostic routine."""
    print()
    print("🔍 Instagram Reel Transcriber - GPU Diagnostic Tool")
    print()

    # Quick check using DeviceManager if available
    if HAS_DEVICE_MANAGER:
        print("=" * 70)
        print("PYTORCH DEVICE DETECTION (Using DeviceManager)")
        print("=" * 70)
        print()
        try:
            manager = DeviceManager()
            manager.print_device_summary()
            print()

            # If GPU is detected and working, we're done!
            if manager.is_gpu_available():
                print("✅ GPU DETECTED AND WORKING!")
                print()
                print("Your PyTorch installation is correctly configured.")
                print(f"The app will use: {manager.get_friendly_name()}")
                print()
                return

            # If no GPU, continue with detailed diagnostics
            print("ℹ️  No GPU acceleration detected - running detailed diagnostics...")
            print()
        except Exception as e:
            print(f"⚠️  DeviceManager error: {e}")
            print("Falling back to manual detection...")
            print()

    # Step 1: Detect GPU
    gpu_type = detect_gpu()

    # Step 2: NVIDIA-specific checks
    if gpu_type == "nvidia":
        print("✓ You have an NVIDIA GPU - CUDA support is possible!")
        print()

        has_driver = check_nvidia_driver()

        if not has_driver:
            print()
            print("❌ PROBLEM: NVIDIA driver is not installed")
            print()
            print("SOLUTION:")
            print("1. Install NVIDIA driver from: https://www.nvidia.com/download/index.aspx")
            print("2. After installing, restart your computer")
            print("3. Run 'nvidia-smi' to verify installation")
            print()

        has_cuda = check_pytorch_cuda()

        if not has_cuda:
            print()
            print("❌ PROBLEM: PyTorch doesn't have CUDA support")
            print()
            print("SOLUTION:")
            print("1. Uninstall current PyTorch: pip uninstall torch torchvision torchaudio")
            print("2. Install PyTorch with CUDA support (see commands below)")
            print()
            get_cuda_install_command()

    elif gpu_type == "amd":
        print("ℹ You have an AMD GPU")
        print()
        print("PyTorch CUDA only works with NVIDIA GPUs.")
        print("For AMD GPUs, you can use ROCm (Linux only):")
        print("👉 https://pytorch.org/get-started/locally/")
        print()
        print("However, for this application, CPU mode will work fine (just slower).")
        print()

    elif gpu_type == "intel":
        print("ℹ You have an Intel GPU")
        print()
        print("PyTorch CUDA only works with NVIDIA GPUs.")
        print("Intel GPUs are not supported for CUDA acceleration.")
        print()
        print("The application will work fine in CPU mode (just slower).")
        print()

    else:
        print("ℹ Could not detect GPU type")
        print()
        print("Please manually check what GPU you have:")
        print()
        print("Windows: Device Manager > Display adapters")
        print("macOS: Apple Menu > About This Mac > System Report > Graphics")
        print("Linux: lspci | grep -i vga")
        print()
        print("If you have:")
        print("- NVIDIA GPU: Install NVIDIA drivers + PyTorch with CUDA")
        print("- AMD/Intel GPU: Use CPU mode (CUDA not supported)")
        print()
        get_cuda_install_command()

    print()
    print("=" * 70)
    print("QUICK FIX FOR NVIDIA GPU USERS")
    print("=" * 70)
    print()
    print("If you have an NVIDIA GPU and want GPU acceleration:")
    print()
    print("1. Check NVIDIA driver:")
    print("   nvidia-smi")
    print()
    print("2. If driver missing, install from:")
    print("   https://www.nvidia.com/download/index.aspx")
    print()
    print("3. Reinstall PyTorch with CUDA (uninstall first):")
    print("   pip uninstall torch torchvision torchaudio")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print()
    print("4. Verify:")
    print("   python -c \"import torch; print(torch.cuda.is_available())\"")
    print("   (should print: True)")
    print()
    print("=" * 70)
    print()
    print("Note: GPU acceleration speeds up transcription ~5-10x")
    print("But CPU mode works fine, just slower (1-2 min per video vs 10-20 sec)")
    print()


if __name__ == "__main__":
    main()
