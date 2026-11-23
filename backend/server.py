from flask import Flask, jsonify, send_from_directory
from pathlib import Path
import subprocess
import sys
import json
import csv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

RESULT_FILE = BASE_DIR / "result.json"
MAIN_FILE = BASE_DIR / "main.py"
LOCATION_FILE = PROJECT_DIR / "dataset" / "location.csv"

app = Flask(__name__)


# Serve the frontend
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Serve frontend files such as CSS and JavaScript
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# Get the latest matching results
@app.route("/api/results", methods=["GET"])
def get_results():
    if not RESULT_FILE.exists():
        return jsonify({
            "error": "No matching results found. Please run matching first."
        }), 404

    with open(RESULT_FILE, "r", encoding="utf-8") as file:
        results = json.load(file)

    return jsonify(results)


# Run the existing matching algorithm
@app.route("/api/run-matching", methods=["POST"])
def run_matching():
    try:
        process = subprocess.run(
            [sys.executable, str(MAIN_FILE)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )

        if process.returncode != 0:
            print(process.stdout)
            print(process.stderr)

            return jsonify({
                "error": "Matching failed. Check the backend terminal.",
                "details": process.stderr[-3000:]
            }), 500

        if not RESULT_FILE.exists():
            return jsonify({
                "error": "Matching finished, but result.json was not created."
            }), 500

        with open(RESULT_FILE, "r", encoding="utf-8") as file:
            results = json.load(file)

        print(process.stdout)

        return jsonify({
            "message": "Matching completed successfully.",
            "results": results
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Matching took too long and timed out."
        }), 500

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# Get campus locations
@app.route("/api/locations", methods=["GET"])
def get_locations():
    if not LOCATION_FILE.exists():
        return jsonify({
            "error": "Location CSV file not found."
        }), 404

    with open(LOCATION_FILE, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        locations = list(reader)

    return jsonify(locations)


if __name__ == "__main__":
    print("Starting UTP SmartRide server...")
    print("Open http://127.0.0.1:5000 in your browser")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )