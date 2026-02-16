#!/usr/bin/env python3
"""
Real-ESRGAN Portable Image Upscale Skill - Upscales an image using a portable Real-ESRGAN binary.

Usage:
    python upscale_image.py <input-image> <output-image> [image_type] [extra_args...]

Arguments:
    <input-image>     Path to the input image
    <output-image>    Path to save the upscaled image
    [image_type]      Type of image: "anime" or "general" (default: "general")
    [extra_args...]   Any extra command-line arguments to pass to Real-ESRGAN

Examples:
    python upscale_image.py input.jpg output.png general
    python upscale_image.py input.png output.png anime
"""
import sys
import os
import platform
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # User input
    INPUT = sys.argv[1]
    OUTPUT = sys.argv[2]
    IMAGE_TYPE = sys.argv[3] if len(sys.argv) > 3 else "general"
    EXTRA_ARGS = sys.argv[4:]

    # Determine model
    if IMAGE_TYPE.lower() == "anime":
        MODEL = "realesrgan-x4plus-anime"
    else:
        MODEL = "realesrgan-x4plus"

    # Detect OS
    OS_NAME = platform.system().lower()
    ARCH = platform.machine()
    FOLDER = Path("binary/realesrgan-ncnn-vulkan")

    # Determine download URL
    if OS_NAME == "linux":
        ZIP_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
    elif OS_NAME == "darwin":
        ZIP_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip"
    elif OS_NAME in ["windows", "msys", "windowsnt"]:
        ZIP_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip"
    else:
        print(f"Unsupported OS: {OS_NAME}")
        sys.exit(1)

    # Download & extract if folder doesn't exist
    if FOLDER.exists():
        print(f"Real-ESRGAN portable binary already exists at {FOLDER}")
    else:
        print("Real-ESRGAN not found. Preparing to download...")
        FOLDER.parent.mkdir(parents=True, exist_ok=True)
        zip_path = Path("realesrgan.zip")

        print(f"Downloading Real-ESRGAN portable binary from {ZIP_URL}...")
        with urllib.request.urlopen(ZIP_URL) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        print(f"Extracting to {FOLDER}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(FOLDER)

        zip_path.unlink()
        print("Download and extraction complete.")

    # Find binary
    binaries = list(FOLDER.glob("realesrgan-ncnn-vulkan*"))
    if not binaries:
        print("Error: Real-ESRGAN binary not found after extraction.")
        sys.exit(1)
    BINARY = binaries[0]

    # Ensure executable
    BINARY.chmod(BINARY.stat().st_mode | 0o111)

    # Run upscaler
    cmd = [str(BINARY), "-i", INPUT, "-o", OUTPUT, "-n", MODEL] + EXTRA_ARGS
    print(f"Upscaling your image with command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    print(f"Image upscale complete: {os.path.abspath(OUTPUT)}, using model: {MODEL}")

if __name__ == "__main__":
    main()
