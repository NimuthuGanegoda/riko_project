import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, base_model_dir="models"):
        self.base_model_dir = Path(base_model_dir)

    def find_model(self, model_name_or_path, backend_type):
        """
        Finds the best model file for the given backend.

        Args:
            model_name_or_path (str): The name of the model or path.
            backend_type (str): 'openvino', 'cpu_legacy' (uses GGUF), 'cuda'.

        Returns:
            Path: The path to the model to load.
        """
        path = Path(model_name_or_path)

        # If it's an absolute path that exists, check for variants nearby
        if path.exists():
            search_dir = path.parent
            base_name = path.stem
        else:
            # Check in local models dir
            search_dir = self.base_model_dir
            base_name = model_name_or_path

        if backend_type == "openvino":
            # Check for OpenVINO IR (.xml)
            # Priority: INT4 -> INT8 -> FP16 -> FP32
            candidates = [
                f"{base_name}_int4.xml",
                f"{base_name}_int8.xml",
                f"{base_name}_fp16.xml",
                f"{base_name}.xml"
            ]
            for c in candidates:
                p = search_dir / c
                if p.exists():
                    logger.info(f"Found OpenVINO model: {p}")
                    return str(p)

            # If not found, return original if it exists and looks compatible (unlikely for raw path)
            if path.suffix == ".xml" and path.exists():
                return str(path)

        elif backend_type == "cpu_legacy" or backend_type == "cpu":
            # Check for GGUF
            # Priority: Q4_K_M -> Q8_0 -> any .gguf
            candidates = [
                f"{base_name}.q4_k_m.gguf",
                f"{base_name}.q8_0.gguf",
                f"{base_name}.gguf"
            ]
            for c in candidates:
                p = search_dir / c
                if p.exists():
                    logger.info(f"Found GGUF model: {p}")
                    return str(p)

            # Search for any GGUF in the directory starting with base_name
            if search_dir.exists():
                ggufs = list(search_dir.glob(f"{base_name}*.gguf"))
                if ggufs:
                    # Sort by modification time or name? Let's pick shortest name (simplest) or first.
                    # Usually Q4 is preferred for legacy.
                    # Let's try to find one with 'q4' in name
                    q4 = [g for g in ggufs if 'q4' in g.name.lower()]
                    if q4:
                        return str(q4[0])
                    return str(ggufs[0])

            if path.suffix == ".gguf" and path.exists():
                return str(path)

        # Default: return original path
        return str(path)

if __name__ == "__main__":
    mm = ModelManager()
    print("Model Manager initialized.")
