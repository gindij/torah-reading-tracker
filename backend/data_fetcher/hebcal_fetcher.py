"""
Fetch Torah reading aliyah structure from Hebcal API.
Enhanced version that fetches all 54 individual parshiot and organizes by book.
"""

import json
import re
from typing import Any, Dict, List

import requests

BOOK_ORDER = {"Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4, "Deuteronomy": 5}

# Complete list of all 54 Torah parshiot in canonical order
ALL_54_PARSHIOT = [
    # Genesis (12)
    "Parashat Bereshit",
    "Parashat Noach",
    "Parashat Lech-Lecha",
    "Parashat Vayera",
    "Parashat Chayei Sara",
    "Parashat Toldot",
    "Parashat Vayetzei",
    "Parashat Vayishlach",
    "Parashat Vayeshev",
    "Parashat Miketz",
    "Parashat Vayigash",
    "Parashat Vayechi",
    # Exodus (11)
    "Parashat Shemot",
    "Parashat Vaera",
    "Parashat Bo",
    "Parashat Beshalach",
    "Parashat Yitro",
    "Parashat Mishpatim",
    "Parashat Terumah",
    "Parashat Tetzaveh",
    "Parashat Ki Tisa",
    "Parashat Vayakhel",
    "Parashat Pekudei",
    # Leviticus (10)
    "Parashat Vayikra",
    "Parashat Tzav",
    "Parashat Shmini",
    "Parashat Tazria",
    "Parashat Metzora",
    "Parashat Achrei Mot",
    "Parashat Kedoshim",
    "Parashat Emor",
    "Parashat Behar",
    "Parashat Bechukotai",
    # Numbers (10)
    "Parashat Bamidbar",
    "Parashat Nasso",
    "Parashat Beha'alotcha",
    "Parashat Sh'lach",
    "Parashat Korach",
    "Parashat Chukat",
    "Parashat Balak",
    "Parashat Pinchas",
    "Parashat Matot",
    "Parashat Masei",
    # Deuteronomy (11)
    "Parashat Devarim",
    "Parashat Vaetchanan",
    "Parashat Eikev",
    "Parashat Re'eh",
    "Parashat Shoftim",
    "Parashat Ki Teitzei",
    "Parashat Ki Tavo",
    "Parashat Nitzavim",
    "Parashat Vayeilech",
    "Parashat Ha'azinu",
    "Parashat V'Zot HaBerachah",
]

# Parshiot that are sometimes combined (to exclude from results)
COMBINED_PARSHIOT = [
    "Parashat Vayakhel-Pekudei",
    "Parashat Tazria-Metzora",
    "Parashat Achrei Mot-Kedoshim",
    "Parashat Behar-Bechukotai",
    "Parashat Chukat-Balak",
    "Parashat Matot-Masei",
    "Parashat Nitzavim-Vayeilech",
]


def parse_verse_range(verse_range: str) -> Dict[str, Any]:
    """
    Parse a verse range string like 'Exodus 1:1-1:17' into structured data.

    Args:
        verse_range: String in format 'Book Chapter:Verse-Chapter:Verse'
                    May include additional info after pipe (|) which is ignored

    Returns:
        Dict with book, start_chapter, start_verse, end_chapter, end_verse
    """
    if "|" in verse_range:
        verse_range = verse_range.split("|")[0].strip()

    # Remove any extra portions (like Numbers reference in combined readings)
    if ";" in verse_range:
        verse_range = verse_range.split(";")[0].strip()
    if "," in verse_range:
        verse_range = verse_range.split(",")[0].strip()

    # Pattern: Book Chapter:Verse-Chapter:Verse
    pattern = r"^(.+?)\s+(\d+):(\d+)-(\d+):(\d+)$"
    match = re.match(pattern, verse_range)

    if not match:
        raise ValueError(f"Could not parse verse range: {verse_range}")

    book, start_ch, start_v, end_ch, end_v = match.groups()

    return {
        "book": book,
        "start_chapter": int(start_ch),
        "start_verse": int(start_v),
        "end_chapter": int(end_ch),
        "end_verse": int(end_v),
        "raw": verse_range,
    }


def fetch_torah_readings_multi_year(years: List[int]) -> List[Dict[str, Any]]:
    """
    Fetch Torah readings across multiple years to get all 54 parshiot.

    Args:
        years: List of Gregorian years to fetch

    Returns:
        List of unique parsha dictionaries
    """
    all_readings = {}

    for year in years:
        url = f"https://www.hebcal.com/hebcal?v=1&cfg=json&s=on&year={year}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("items", []):
            if item.get("category") == "parashat" and "leyning" in item:
                leyning = item["leyning"]
                title = item.get("title")

                # Skip combined parshiot
                if title in COMBINED_PARSHIOT:
                    continue

                # Skip if not in our canonical list of 54
                if title not in ALL_54_PARSHIOT:
                    continue

                # Skip if we already have this parsha
                if title in all_readings:
                    continue

                # Extract aliyot 1-7 (not maftir)
                aliyot = []
                for i in range(1, 8):
                    aliyah_key = str(i)
                    if aliyah_key in leyning:
                        verse_range = leyning[aliyah_key]
                        try:
                            parsed = parse_verse_range(verse_range)

                            aliyot.append(
                                {
                                    "number": i,
                                    "verses": verse_range,
                                    "parsed": parsed,
                                    "verse_count": 0,  # Will be set from Sefaria
                                }
                            )
                        except ValueError as e:
                            print(f"Warning: Could not parse {verse_range}: {e}")
                            continue

                if aliyot:
                    # Get book from first aliyah
                    book = aliyot[0]["parsed"]["book"]
                    start_chapter = aliyot[0]["parsed"]["start_chapter"]

                    parsha = {
                        "name": item.get("hebrew", item.get("title")),
                        "title": title,
                        "date": item.get("date"),
                        "torah_portion": leyning.get("torah"),
                        "book": book,
                        "book_order": BOOK_ORDER.get(book, 99),
                        "start_chapter": start_chapter,
                        "aliyot": aliyot,
                    }

                    all_readings[title] = parsha

    # Sort by the canonical order from ALL_54_PARSHIOT
    sorted_readings = []
    for parsha_title in ALL_54_PARSHIOT:
        if parsha_title in all_readings:
            sorted_readings.append(all_readings[parsha_title])
        else:
            # Placeholder for missing parshiot (like V'Zot HaBerachah)
            print(f"Warning: {parsha_title} not found in calendar data")

    return sorted_readings
