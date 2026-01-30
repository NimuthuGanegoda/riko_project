import torch
import cpuinfo
import logging

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
        # 1. Check for CUDA
        if torch.cuda.is_available():
            logger.info("CUDA detected.")
            self.device_priority.append("cuda")

        # 2. Check for OpenVINO (specifically GPU/NPU)
        if OPENVINO_AVAILABLE:
            try:
                core = Core()
                devices = core.available_devices
                logger.info(f"OpenVINO devices: {devices}")
                if "GPU" in devices:
                    logger.info("OpenVINO GPU detected.")
                    self.device_priority.append("openvino_gpu")
                if "NPU" in devices:
                    self.device_priority.append("openvino_npu")
                self.device_priority.append("openvino_cpu")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenVINO Core: {e}")

        # 3. Check for AVX2
        info = cpuinfo.get_cpu_info()
        flags = info.get('flags', [])
        # flags are usually lowercase in cpuinfo, but let's handle case insensitivity
        flags = [f.lower() for f in flags]

        if 'avx2' in flags:
            logger.info("AVX2 instructions detected.")
            self.avx2_supported = True
            self.device_priority.append("cpu_avx2")
        else:
            logger.warning("No AVX2 instructions detected. Using legacy CPU mode.")
            self.avx2_supported = False
            self.device_priority.append("cpu_legacy")

    def get_best_backend(self):
        """Returns the best backend found based on priority."""
        if "cuda" in self.device_priority:
            return "cuda"
        elif "openvino_gpu" in self.device_priority:
            return "openvino" # Can clarify specific device later if needed
        elif "cpu_legacy" in self.device_priority:
            return "cpu_legacy"
        else:
            return "cpu"

    def get_hardware_config(self):
        return {
            "backend": self.get_best_backend(),
            "avx2": self.avx2_supported,
            "priority_list": self.device_priority,
            "openvino_available": OPENVINO_AVAILABLE
        }

if __name__ == "__main__":
    detector = HardwareDetector()
    print("Hardware Config:", detector.get_hardware_config())
