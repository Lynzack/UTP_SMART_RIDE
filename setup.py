import subprocess
import sys

print("Installing Smart Ride dependencies...")

subprocess.check_call([
    sys.executable,
    "-m",
    "pip",
    "install",
    "-r",
    "requirements.txt"
])

print("\nAll dependencies installed successfully!")