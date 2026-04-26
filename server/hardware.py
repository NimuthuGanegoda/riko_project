import torch
import cpuinfo
import logging
import platform

try:
    from openvino.runtime import Core
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardwareDetector:
    def __init__(self):
        self.device_priority = []
        self._detect_hardware()

    def _detect_hardware(self):
        # 1. Check for CUDA / ROCm (AMD GPU)
        if torch.cuda.is_available():
            if hasattr(torch.version, 'hip') and torch.version.hip:
                logger.info("ROCm (AMD GPU) detected.")
                self.device_priority.append("rocm")
            else:
                logger.info("CUDA (NVIDIA GPU) detected.")
                self.device_priority.append("cuda")

        # 2. Check for Apple Silicon (MPS)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("Apple Silicon (Metal Performance Shaders) detected!")
            self.device_priority.append("mps")

        # 3. Check for OpenVINO (specifically Intel NPU / GPU)
        if OPENVINO_AVAILABLE:
            try:
                core = Core()
                devices = core.available_devices
                logger.info(f"OpenVINO devices: {devices}")
                
                # Prioritize NPU for ultra-lite power consumption
                if "NPU" in devices:
                    logger.info("⚡ Intel NPU detected! Activating Super-Lite Battery Saver Mode.")
                    self.device_priority.append("openvino_npu")
                if "GPU" in devices:
                    logger.info("OpenVINO GPU detected.")
                    self.device_priority.append("openvino_gpu")
                self.device_priority.append("openvino_cpu")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenVINO Core: {e}")

        # 4. Check CPU Architecture (AVX2 / ARM64)
        info = cpuinfo.get_cpu_info()
        flags = [f.lower() for f in info.get('flags', [])]
        arch = platform.machine().lower()

        if 'avx2' in flags or 'arm64' in arch or 'aarch64' in arch:
            logger.info(f"Modern CPU architecture detected ({arch} with AVX2/ARM).")
            self.modern_cpu = True
            self.device_priority.append("cpu_modern")
        else:
            logger.warning("Legacy CPU detected. Using Maximum Compatibility Potato Mode 🥔")
            self.modern_cpu = False
            self.device_priority.append("cpu_legacy")

    def get_best_backend(self):
        """Returns the best backend found based on ultra-lite priority."""
        # For 'super lite' mode, if NPU exists, use it first!
        if "openvino_npu" in self.device_priority:
            return "openvino"
            
        if "cuda" in self.device_priority:
            return "cuda"
        elif "rocm" in self.device_priority:
            return "rocm" 
        elif "mps" in self.device_priority:
            return "mps"
        elif any(ov in self.device_priority for ov in ["openvino_gpu", "openvino_cpu"]):
            return "openvino"
        elif "cpu_legacy" in self.device_priority:
            return "cpu_legacy"
        else:
            return "cpu"

    def get_openvino_device(self):
        if "openvino_npu" in self.device_priority:
            return "NPU"
        elif "openvino_gpu" in self.device_priority:
            return "GPU"
        elif "openvino_cpu" in self.device_priority:
            return "CPU"
        return "CPU"

    def get_hardware_config(self):
        return {
            "backend": self.get_best_backend(),
            "openvino_device": self.get_openvino_device(),
            "modern_cpu": getattr(self, 'modern_cpu', False),
            "priority_list": self.device_priority,
            "openvino_available": OPENVINO_AVAILABLE
        }

if __name__ == "__main__":
    detector = HardwareDetector()
    print("Hardware Config:", detector.get_hardware_config())
