import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def install_dependencies():
    """Create a virtual environment and install required Python dependencies."""
    print("Creating virtual environment...")
    venv_dir = Path("venv")
    
    # Create the virtual environment if it doesn't exist
    if not venv_dir.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
        print(f"Virtual environment created at {venv_dir}")
    else:
        print("Virtual environment already exists.")

    # Determine the correct pip executable
    if os.name == "nt":  # Windows
        pip_executable = venv_dir / "Scripts" / "pip"
    else:  # macOS/Linux
        pip_executable = venv_dir / "bin" / "pip"

    # Install dependencies
    print("Installing Python dependencies...")
    subprocess.check_call([str(pip_executable), "install", "-r", "requirements.txt"])

    print("Dependencies installed successfully!")

def download_ffmpeg():
    """Check for FFmpeg and download if not available."""
    try:
        # Attempt to check if FFmpeg is installed
        subprocess.run(
            ["ffmpeg", "-version"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        print("FFmpeg is already installed.")
        return  # Exit the function if FFmpeg is found
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Handle case where FFmpeg is not installed or not in PATH
        print("FFmpeg is not installed or not found in PATH, proceeding with download.")

    
    print("Downloading FFmpeg...")
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_zip = "ffmpeg.zip"
    ffmpeg_dir = Path("ffmpeg") 

    # Example placeholder for your download logic
    print("Downloading and setting up FFmpeg...")
    # Add your download and setup code here

    # Download FFmpeg with progress bar
    def download_progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rDownloading FFmpeg: {percent}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip, reporthook=download_progress_hook)
    print()  # Move to the next line after the download is complete

    print("Extracting FFmpeg...")

    # Extract FFmpeg
    with zipfile.ZipFile(ffmpeg_zip, "r") as zip_ref:
        zip_ref.extractall(ffmpeg_dir)

    print("Setting up FFmpeg...")

    # Add FFmpeg to PATH
    ffmpeg_bin = ffmpeg_dir / "ffmpeg-release-essentials" / "bin"
    if ffmpeg_bin.exists():
        os.environ["PATH"] += os.pathsep + str(ffmpeg_bin)
        print(f"FFmpeg installed and added to PATH: {ffmpeg_bin}")
    else:
        print("FFmpeg installation failed.")

    print("Cleaning up...")

    # Clean up
    os.remove(ffmpeg_zip)

def main():
    print("Setting up the environment...")
    install_dependencies()
    download_ffmpeg()
    print("Setup complete!")

if __name__ == "__main__":
    main()
