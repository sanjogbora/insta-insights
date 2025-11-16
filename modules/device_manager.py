"""
Device Manager Module
Smart detection and selection of compute devices (CUDA/MPS/ROCm/CPU).
Works with any PyTorch installation without forcing changes.
"""

import sys
import platform
from typing import Tuple, Dict, Optional


class DeviceManager:
    """
    Manages device detection and selection for PyTorch.
    Automatically detects best available device without modifying installation.
    """

    def __init__(self):
        """Initialize the device manager."""
        self.device = None
        self.device_type = None
        self.device_name = None
        self.device_info = {}
        self.pytorch_available = False
        self.torch = None

        # Try to import PyTorch
        try:
            import torch
            self.torch = torch
            self.pytorch_available = True
        except ImportError:
            self.pytorch_available = False

    def detect_best_device(self, verbose: bool = False) -> str:
        """
        Detect and return the best available compute device.

        Detection order:
        1. NVIDIA CUDA (if available)
        2. Apple MPS (if available)
        3. AMD ROCm (if available)
        4. CPU (fallback)

        Args:
            verbose: If True, print detection details

        Returns:
            Device string: 'cuda', 'mps', 'cpu', etc.
        """
        if not self.pytorch_available:
            if verbose:
                print("⚠️  PyTorch not installed - cannot detect GPU")
            self.device = "cpu"
            self.device_type = "cpu"
            self.device_name = "CPU (PyTorch not available)"
            return "cpu"

        # Try CUDA (NVIDIA) - Priority 1
        cuda_available, cuda_info = self._check_cuda()
        if cuda_available:
            self.device = "cuda"
            self.device_type = "cuda"
            self.device_name = cuda_info.get("name", "NVIDIA GPU")
            self.device_info = cuda_info
            if verbose:
                print(f"✓ Using NVIDIA CUDA: {self.device_name}")
            return "cuda"

        # Try MPS (Apple Silicon) - Priority 2
        mps_available, mps_info = self._check_mps()
        if mps_available:
            self.device = "mps"
            self.device_type = "mps"
            self.device_name = mps_info.get("name", "Apple Silicon GPU")
            self.device_info = mps_info
            if verbose:
                print(f"✓ Using Apple MPS: {self.device_name}")
            return "mps"

        # Try ROCm (AMD) - Priority 3
        rocm_available, rocm_info = self._check_rocm()
        if rocm_available:
            self.device = "cuda"  # ROCm uses 'cuda' device string
            self.device_type = "rocm"
            self.device_name = rocm_info.get("name", "AMD GPU (ROCm)")
            self.device_info = rocm_info
            if verbose:
                print(f"✓ Using AMD ROCm: {self.device_name}")
            return "cuda"

        # Fallback to CPU
        cpu_info = self._get_cpu_info()
        self.device = "cpu"
        self.device_type = "cpu"
        self.device_name = cpu_info.get("name", "CPU")
        self.device_info = cpu_info
        if verbose:
            print(f"ℹ️  Using CPU: {self.device_name}")
            print("   (GPU not available - transcription will be slower)")
        return "cpu"

    def _check_cuda(self) -> Tuple[bool, Dict]:
        """
        Check if NVIDIA CUDA is available.

        Returns:
            Tuple of (is_available, device_info_dict)
        """
        if not self.pytorch_available:
            return False, {}

        try:
            if self.torch.cuda.is_available():
                info = {
                    "name": self.torch.cuda.get_device_name(0),
                    "count": self.torch.cuda.device_count(),
                    "current_device": self.torch.cuda.current_device(),
                    "cuda_version": self.torch.version.cuda,
                    "pytorch_version": self.torch.__version__,
                }

                # Get additional CUDA properties
                try:
                    props = self.torch.cuda.get_device_properties(0)
                    info["total_memory"] = props.total_memory
                    info["compute_capability"] = f"{props.major}.{props.minor}"
                except:
                    pass

                return True, info
        except Exception as e:
            # CUDA check failed
            pass

        return False, {}

    def _check_mps(self) -> Tuple[bool, Dict]:
        """
        Check if Apple MPS (Metal Performance Shaders) is available.
        Only available on macOS with Apple Silicon (M1/M2/M3).

        Returns:
            Tuple of (is_available, device_info_dict)
        """
        if not self.pytorch_available:
            return False, {}

        # MPS only available on macOS
        if platform.system() != "Darwin":
            return False, {}

        try:
            # Check if MPS is available (PyTorch 1.12+)
            if hasattr(self.torch.backends, "mps") and self.torch.backends.mps.is_available():
                info = {
                    "name": "Apple Silicon GPU (MPS)",
                    "platform": platform.machine(),  # arm64 for Apple Silicon
                    "pytorch_version": self.torch.__version__,
                    "mps_built": hasattr(self.torch.backends, "mps"),
                }

                # Check if MPS is built and enabled
                if hasattr(self.torch.backends.mps, "is_built"):
                    info["mps_built"] = self.torch.backends.mps.is_built()

                return True, info
        except Exception as e:
            # MPS check failed
            pass

        return False, {}

    def _check_rocm(self) -> Tuple[bool, Dict]:
        """
        Check if AMD ROCm is available.
        Only available on Linux with AMD GPUs.

        Returns:
            Tuple of (is_available, device_info_dict)
        """
        if not self.pytorch_available:
            return False, {}

        # ROCm primarily Linux-only
        if platform.system() != "Linux":
            return False, {}

        try:
            # Check if PyTorch was built with ROCm
            # ROCm builds use 'cuda' interface but with ROCm backend
            if self.torch.cuda.is_available() and hasattr(self.torch.version, "hip"):
                # HIP version indicates ROCm build
                info = {
                    "name": "AMD GPU (ROCm)",
                    "count": self.torch.cuda.device_count(),
                    "hip_version": self.torch.version.hip,
                    "pytorch_version": self.torch.__version__,
                }

                try:
                    info["device_name"] = self.torch.cuda.get_device_name(0)
                except:
                    pass

                return True, info
        except Exception as e:
            # ROCm check failed
            pass

        return False, {}

    def _get_cpu_info(self) -> Dict:
        """
        Get CPU information.

        Returns:
            Dictionary with CPU info
        """
        info = {
            "name": f"{platform.processor() or platform.machine()} CPU",
            "platform": platform.system(),
            "architecture": platform.machine(),
        }

        if self.pytorch_available:
            info["pytorch_version"] = self.torch.__version__

        # Try to get CPU count
        try:
            import multiprocessing
            info["cpu_count"] = multiprocessing.cpu_count()
        except:
            pass

        return info

    def get_device_info(self) -> Dict:
        """
        Get detailed information about the current device.

        Returns:
            Dictionary with device information
        """
        if self.device is None:
            self.detect_best_device()

        return {
            "device": self.device,
            "device_type": self.device_type,
            "device_name": self.device_name,
            "details": self.device_info,
            "pytorch_available": self.pytorch_available,
        }

    def get_device_string(self) -> str:
        """
        Get the device string to use with PyTorch.

        Returns:
            Device string: 'cuda', 'mps', 'cpu'
        """
        if self.device is None:
            self.detect_best_device()
        return self.device

    def get_friendly_name(self) -> str:
        """
        Get a user-friendly device name.

        Returns:
            Friendly device name string
        """
        if self.device is None:
            self.detect_best_device()
        return self.device_name or "Unknown Device"

    def is_gpu_available(self) -> bool:
        """
        Check if any GPU is available.

        Returns:
            True if GPU (CUDA/MPS/ROCm) is available
        """
        if self.device is None:
            self.detect_best_device()
        return self.device_type in ["cuda", "mps", "rocm"]

    def get_speed_estimate(self) -> str:
        """
        Get estimated processing speed category.

        Returns:
            Speed estimate: 'Very Fast', 'Fast', 'Medium', 'Slow'
        """
        if self.device_type == "cuda":
            # Check compute capability for NVIDIA
            if "compute_capability" in self.device_info:
                cc = float(self.device_info["compute_capability"])
                if cc >= 7.5:  # RTX 2000 series and newer
                    return "Very Fast (Modern GPU)"
                elif cc >= 6.0:  # GTX 1000 series and newer
                    return "Fast (Good GPU)"
                else:
                    return "Medium (Older GPU)"
            return "Fast (NVIDIA GPU)"

        elif self.device_type == "mps":
            # Apple Silicon is generally fast
            return "Fast (Apple Silicon)"

        elif self.device_type == "rocm":
            return "Fast (AMD GPU)"

        else:
            # CPU
            cpu_count = self.device_info.get("cpu_count", 1)
            if cpu_count >= 8:
                return "Medium (Multi-core CPU)"
            else:
                return "Slow (CPU only)"

    def print_device_summary(self):
        """Print a formatted summary of the detected device."""
        if self.device is None:
            self.detect_best_device()

        print("=" * 70)
        print("DEVICE DETECTION SUMMARY")
        print("=" * 70)
        print(f"Device Type: {self.device_type.upper()}")
        print(f"Device Name: {self.device_name}")
        print(f"PyTorch Device String: {self.device}")
        print(f"Speed Estimate: {self.get_speed_estimate()}")
        print()

        if self.device_info:
            print("Details:")
            for key, value in self.device_info.items():
                if key != "total_memory":
                    print(f"  {key}: {value}")
                else:
                    # Format memory in GB
                    print(f"  {key}: {value / (1024**3):.2f} GB")

        print("=" * 70)


# Convenience functions
def get_device(verbose: bool = False) -> str:
    """
    Quick function to get the best available device.

    Args:
        verbose: Print detection details

    Returns:
        Device string for PyTorch
    """
    manager = DeviceManager()
    return manager.detect_best_device(verbose=verbose)


def get_device_info() -> Dict:
    """
    Quick function to get device information.

    Returns:
        Dictionary with device info
    """
    manager = DeviceManager()
    manager.detect_best_device()
    return manager.get_device_info()


def print_device_info():
    """Print device information summary."""
    manager = DeviceManager()
    manager.detect_best_device()
    manager.print_device_summary()
