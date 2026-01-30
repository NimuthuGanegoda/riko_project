import argparse
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_model(model_id, output_dir):
    try:
        from optimum.intel import OVModelForCausalLM
        from transformers import AutoTokenizer
        import openvino as ov
    except ImportError:
        logger.error("Dependencies missing. Install requirements_legacy.txt")
        sys.exit(1)

    logger.info(f"Loading and exporting {model_id} to {output_dir}...")

    # Exporting using Optimum
    # This automatically converts the model to OpenVINO IR
    try:
        model = OVModelForCausalLM.from_pretrained(
            model_id,
            export=True,
            compile=False,
            device="CPU" # Exporting happens on CPU usually
        )

        model.save_pretrained(output_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.save_pretrained(output_dir)

    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)

    logger.info("Export complete. Attempting FP16 compression and Shape Fix...")

    try:
        core = ov.Core()
        xml_path = Path(output_dir) / "openvino_model.xml"

        if xml_path.exists():
            ov_model = core.read_model(xml_path)

            # Apply FP16 compression
            # Using ov.save_model with compress_to_fp16=True if available
            if hasattr(ov, "save_model"):
                logger.info("Saving model with compress_to_fp16=True...")
                ov.save_model(ov_model, xml_path, compress_to_fp16=True)
            else:
                # Fallback for older versions using serialize
                from openvino.runtime import serialize
                logger.info("Using serialize (FP16 compression not guaranteed here without NNCF).")
                serialize(ov_model, xml_path)

            logger.info(f"Model saved to {xml_path}")

    except Exception as e:
        logger.warning(f"Post-processing failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert LLM to OpenVINO IR with FP16 compression.")
    parser.add_argument("model_id", type=str, help="HuggingFace Model ID or local path")
    parser.add_argument("output_dir", type=str, help="Directory to save the converted model")

    args = parser.parse_args()

    convert_model(args.model_id, args.output_dir)
