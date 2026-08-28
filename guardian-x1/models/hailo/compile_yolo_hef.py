"""
Guardian X-1 Hailo-8L NPU HEF Model Compiler
---------------------------------------------
Compiles PyTorch/ONNX YOLOv8n object detection model into Hailo Executable Format (.hef)
optimized for 26 TOPS 8-bit quantized execution on the Raspberry Pi 5 M.2 Hailo-8L chip.
"""

import os
import sys


def compile_hailo_hef(
        onnx_model_path: str = "models/onnx/yolov8n_tactical.onnx",
        output_hef_path: str = "models/hailo/yolov8n_tactical.hef",
        calib_dataset_dir: str = "datasets/calib_images"
):
    os.makedirs(os.path.dirname(output_hef_path), exist_ok=True)

    print("==========================================================")
    print("GUARDIAN X-1 HAILO-8L DATAFLOW COMPILER (DFC) PIPELINE")
    print("==========================================================")

    try:
        from hailo_sdk_client import ClientRunner
    except ImportError:
        print("[WARN] Hailo SDK Client not installed in this environment.")
        print("[INFO] Writing compilation task script wrapper for Hailo DFC Docker container...")

        script_content = f"""#!/usr/bin/env bash
# Hailo-8L Compilation Container Invocation
docker run --rm -v $(pwd):/workspace hailo_dfc:latest bash -c "
    hailo parser onnx {onnx_model_path} --hw-arch hailo8l --start-node-names 'images' --end-node-names 'output0'
    hailo optimize yolov8n_tactical.hn --hw-arch hailo8l --calib-path {calib_dataset_dir} --use-quant-stats
    hailo compiler yolov8n_tactical_optimized.hn --hw-arch hailo8l --output {output_hef_path}
"
"""
        with open("models/hailo/compile_container.sh", "w") as f:
            f.write(script_content)
        os.chmod("models/hailo/compile_container.sh", 0o755)
        print("[SUCCESS] Created compilation script: models/hailo/compile_container.sh")
        return

    # Native SDK Compilation Stream
    print(f"[1/4] Loading ONNX model into Hailo ClientRunner: {onnx_model_path}")
    runner = ClientRunner(hw_arch="hailo8l")
    hn, npz = runner.translate_onnx_model(
        onnx_model_path,
        model_name="yolov8n_tactical",
        start_node_names=["images"],
        end_node_names=["output0"]
    )

    print("[2/4] Applying 8-bit Quantization and Optimization rules...")
    runner.load_model_script("models/hailo/yolov8n_tactical.alls")
    runner.optimize(calib_dataset_dir)

    print("[3/4] Compiling Model stream to HEF executable format...")
    hef = runner.compile()

    print(f"[4/4] Writing binary HEF file to: {output_hef_path}")
    with open(output_hef_path, "wb") as f:
        f.write(hef)

    print("[SUCCESS] Hailo-8L HEF model compilation complete!")


if __name__ == "__main__":
    compile_hailo_hef()
