"""
Manage reading progress tracking in CSV format.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProgressTracker:
    """Track Torah reading progress in a CSV file."""

    def __init__(self, csv_path: str):
        """
        Initialize progress tracker.

        Args:
            csv_path: Path to the CSV file for storing progress
        """
        self.csv_path = Path(csv_path)
        self._progress_cache: Optional[Dict] = None
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["parsha_name", "aliyah_number", "is_complete", "date_completed"]
                )

    def mark_complete(self, parsha_name: str, aliyah_number: int) -> None:
        """
        Mark an aliyah as complete.

        Args:
            parsha_name: Name of the parsha
            aliyah_number: Aliyah number (1-7)
        """
        progress = self.load_progress()

        # Check if already marked
        key = (parsha_name, aliyah_number)
        if key not in progress or not progress[key]["is_complete"]:
            progress[key] = {
                "is_complete": True,
                "date_completed": datetime.now().isoformat(),
            }
            self._save_progress(progress)

    def mark_incomplete(self, parsha_name: str, aliyah_number: int) -> None:
        """
        Mark an aliyah as incomplete.

        Args:
            parsha_name: Name of the parsha
            aliyah_number: Aliyah number (1-7)
        """
        progress = self.load_progress()
        key = (parsha_name, aliyah_number)

        if key in progress:
            progress[key] = {"is_complete": False, "date_completed": None}
            self._save_progress(progress)

    def load_progress(self) -> Dict:
        """
        Load all progress from CSV (cached).

        Returns:
            Dict mapping (parsha_name, aliyah_number) to progress data
        """
        if self._progress_cache is not None:
            return self._progress_cache

        progress = {}

        if not self.csv_path.exists():
            self._progress_cache = progress
            return progress

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["parsha_name"], int(row["aliyah_number"]))
                progress[key] = {
                    "is_complete": row["is_complete"].lower() == "true",
                    "date_completed": (
                        row["date_completed"] if row["date_completed"] else None
                    ),
                }

        self._progress_cache = progress
        return progress

    def _save_progress(self, progress: Dict) -> None:
        """
        Save progress dict to CSV and update cache.

        Args:
            progress: Dict mapping (parsha_name, aliyah_number) to progress data
        """
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["parsha_name", "aliyah_number", "is_complete", "date_completed"]
            )

            for (parsha_name, aliyah_number), data in sorted(progress.items()):
                writer.writerow(
                    [
                        parsha_name,
                        aliyah_number,
                        data["is_complete"],
                        data["date_completed"] or "",
                    ]
                )

        # Update cache
        self._progress_cache = progress
