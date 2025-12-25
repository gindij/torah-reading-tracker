"""
Initialize complete Torah reading data with all 54 parshiot.
Handles special cases: Matot, Masei (usually combined), and V'Zot HaBerachah (Simchat Torah).
"""

import json
from pathlib import Path
from typing import Dict

from hebcal_fetcher import (ALL_54_PARSHIOT, fetch_torah_readings_multi_year,
                            parse_verse_range)
from sefaria_fetcher import count_words_and_verses_in_aliyah


def add_special_parshiot(readings_dict: Dict) -> Dict:
    """
    Add V'Zot HaBerachah manually since it doesn't appear in the regular calendar API.
    (It's read on Simchat Torah)

    Args:
        readings_dict: Dict of parsha title -> parsha data

    Returns:
        Updated dict with special parshiot added
    """

    # V'Zot HaBerachah - Deuteronomy 33:1-34:12
    # Standard 7 aliyah divisions
    vzot_aliyot_verses = [
        "Deuteronomy 33:1-33:7",
        "Deuteronomy 33:8-33:12",
        "Deuteronomy 33:13-33:17",
        "Deuteronomy 33:18-33:21",
        "Deuteronomy 33:22-33:26",
        "Deuteronomy 33:27-33:29",
        "Deuteronomy 34:1-34:12",
    ]

    vzot_aliyot = []
    for i, verses in enumerate(vzot_aliyot_verses, 1):
        try:
            parsed = parse_verse_range(verses)
            vzot_aliyot.append(
                {
                    "number": i,
                    "verses": verses,
                    "parsed": parsed,
                    "verse_count": 0,  # Will be set from Sefaria
                }
            )
        except Exception as e:
            print(f"Error parsing V'Zot HaBerachah aliyah {i}: {e}")

    readings_dict["Parashat V'Zot HaBerachah"] = {
        "name": "וזאת הברכה",
        "title": "Parashat V'Zot HaBerachah",
        "date": None,
        "torah_portion": "Deuteronomy 33:1-34:12",
        "book": "Deuteronomy",
        "book_order": 5,
        "start_chapter": 33,
        "aliyot": vzot_aliyot,
    }

    return readings_dict


def main() -> None:
    """Fetch and save complete Torah reading data with all 54 parshiot."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    output_file = data_dir / "torah_readings_complete.json"

    print("Step 1: Fetching Torah reading structure from Hebcal...")
    readings_list = fetch_torah_readings_multi_year(list(range(2014, 2031)))

    # Convert to dict for easier manipulation
    readings_dict = {r["title"]: r for r in readings_list}

    print(f"Found {len(readings_dict)} parshiot from API")

    print("\nStep 2: Adding special parshiot (V'Zot HaBerachah)...")
    readings_dict = add_special_parshiot(readings_dict)

    # Convert back to list in canonical order
    ordered_readings = []
    for parsha_title in ALL_54_PARSHIOT:
        if parsha_title in readings_dict:
            ordered_readings.append(readings_dict[parsha_title])
        else:
            print(f"Warning: {parsha_title} still missing")

    print(f"\nTotal parshiot: {len(ordered_readings)}")

    print("\nStep 3: Enriching with word counts from Sefaria...")
    print("This may take several minutes...")

    for i, parsha in enumerate(ordered_readings):
        print(f"\nProcessing {i+1}/{len(ordered_readings)}: {parsha['title']}")

        # Skip V'Zot HaBerachah word counting for now if no aliyot
        if len(parsha["aliyot"]) == 0:
            print("  Skipping (no aliyot structure available)")
            continue

        for aliyah in parsha["aliyot"]:
            print(f"  Aliyah {aliyah['number']}: {aliyah['verses']}")
            try:
                counts = count_words_and_verses_in_aliyah(aliyah["parsed"])
                aliyah["word_count"] = counts["word_count"]
                aliyah["verse_count"] = counts["verse_count"]
                print(
                    f"    -> {counts['word_count']} words, {counts['verse_count']} verses"
                )
            except Exception as e:
                print(f"    -> Error: {e}")
                aliyah["word_count"] = 0
                aliyah["verse_count"] = 0

    print(f"\nStep 4: Saving to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ordered_readings, f, ensure_ascii=False, indent=2)

    print("\nDone! Data initialization complete.")

    # Print summary
    total_aliyot = sum(len(p["aliyot"]) for p in ordered_readings)
    total_words = sum(
        a.get("word_count", 0) for p in ordered_readings for a in p["aliyot"]
    )
    total_verses = sum(a["verse_count"] for p in ordered_readings for a in p["aliyot"])

    # Group by book
    by_book = {}
    for parsha in ordered_readings:
        book = parsha["book"]
        if book not in by_book:
            by_book[book] = []
        by_book[book].append(parsha["title"])

    print(f"\nSummary:")
    print(f"  Total Parshiot: {len(ordered_readings)}")
    for book in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]:
        if book in by_book:
            print(f"  {book}: {len(by_book[book])}")
    print(f"  Total Aliyot: {total_aliyot}")
    print(f"  Total Verses: {total_verses}")
    print(f"  Total Words: {total_words}")


if __name__ == "__main__":
    main()
