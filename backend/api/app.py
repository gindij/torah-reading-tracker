"""
Flask API for Torah reading tracker.
"""

import json
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.data_fetcher.progress_tracker import ProgressTracker

app = Flask(__name__)
CORS(app)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
TORAH_DATA_FILE = DATA_DIR / "torah_readings_complete.json"
PROGRESS_FILE = DATA_DIR / "progress.csv"

tracker = ProgressTracker(str(PROGRESS_FILE))

# Load Torah data once at startup (it never changes during runtime)
_torah_data_cache: List[Dict] = []


def load_torah_data() -> List[Dict]:
    """Load Torah reading data from JSON file (cached)."""
    global _torah_data_cache

    if _torah_data_cache:
        return _torah_data_cache

    if not TORAH_DATA_FILE.exists():
        return []

    with open(TORAH_DATA_FILE, "r", encoding="utf-8") as f:
        _torah_data_cache = json.load(f)

    return _torah_data_cache


def merge_progress_with_data(torah_data: List[Dict]) -> List[Dict]:
    """
    Merge progress information with Torah reading data.

    Args:
        torah_data: List of parsha dicts

    Returns:
        Torah data enriched with progress information
    """
    progress = tracker.load_progress()

    for parsha in torah_data:
        for aliyah in parsha["aliyot"]:
            key = (parsha["title"], aliyah["number"])
            if key in progress:
                aliyah["is_complete"] = progress[key]["is_complete"]
                aliyah["date_completed"] = progress[key]["date_completed"]
            else:
                aliyah["is_complete"] = False
                aliyah["date_completed"] = None

    return torah_data


@app.route("/api/parshiot", methods=["GET"])
def get_all_parshiot():
    """Get all Torah readings with progress."""
    torah_data = load_torah_data()
    enriched_data = merge_progress_with_data(torah_data)
    return jsonify(enriched_data)


@app.route("/api/parshiot/<parsha_title>", methods=["GET"])
def get_parsha(parsha_title: str):
    """Get a specific parsha with progress."""
    torah_data = load_torah_data()
    enriched_data = merge_progress_with_data(torah_data)

    for parsha in enriched_data:
        if parsha["title"] == parsha_title:
            return jsonify(parsha)

    return jsonify({"error": "Parsha not found"}), 404


@app.route("/api/parshiot/<parsha_title>/aliyot/<int:aliyah_number>", methods=["PUT"])
def update_aliyah_status(parsha_title: str, aliyah_number: int):
    """
    Update completion status of an aliyah.

    Request body:
        {"is_complete": true/false}
    """
    data = request.get_json()
    is_complete = data.get("is_complete", False)

    if is_complete:
        tracker.mark_complete(parsha_title, aliyah_number)
    else:
        tracker.mark_incomplete(parsha_title, aliyah_number)

    return jsonify({"success": True})


@app.route("/api/stats", methods=["GET"])
def get_statistics():
    """
    Get overall reading statistics.

    Returns word count, verse count, and aliyah count for completed readings.
    """
    torah_data = load_torah_data()
    enriched_data = merge_progress_with_data(torah_data)

    total_aliyot = 0
    completed_aliyot = 0
    total_verses = 0
    completed_verses = 0
    total_words = 0
    completed_words = 0

    for parsha in enriched_data:
        for aliyah in parsha["aliyot"]:
            total_aliyot += 1
            total_verses += aliyah["verse_count"]
            total_words += aliyah.get("word_count", 0)

            if aliyah["is_complete"]:
                completed_aliyot += 1
                completed_verses += aliyah["verse_count"]
                completed_words += aliyah.get("word_count", 0)

    return jsonify(
        {
            "total": {
                "aliyot": total_aliyot,
                "verses": total_verses,
                "words": total_words,
            },
            "completed": {
                "aliyot": completed_aliyot,
                "verses": completed_verses,
                "words": completed_words,
            },
            "percentage": {
                "aliyot": (
                    round(completed_aliyot / total_aliyot * 100, 1)
                    if total_aliyot > 0
                    else 0
                ),
                "verses": (
                    round(completed_verses / total_verses * 100, 1)
                    if total_verses > 0
                    else 0
                ),
                "words": (
                    round(completed_words / total_words * 100, 1)
                    if total_words > 0
                    else 0
                ),
            },
        }
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "data_initialized": TORAH_DATA_FILE.exists(),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
