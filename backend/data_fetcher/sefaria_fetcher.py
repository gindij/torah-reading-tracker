"""
Fetch Hebrew Torah text from Sefaria API and count words.
"""

import re
import time
from typing import Dict, List

import requests


def count_hebrew_words(text: str) -> int:
    """
    Count words in Hebrew text.

    Hebrew words are separated by spaces, but we need to handle:
    - Punctuation marks
    - Cantillation marks
    - Special markers like {פ}

    Args:
        text: Hebrew text string

    Returns:
        Number of words in the text
    """
    # Remove special markers like {פ}
    text = re.sub(r"\{[^}]+\}", "", text)

    # Split by whitespace and filter empty strings
    words = [w.strip() for w in text.split() if w.strip()]

    return len(words)


def fetch_hebrew_text(
    book: str, chapter: int, start_verse: int, end_verse: int
) -> Dict:
    """
    Fetch Hebrew text for a range of verses from Sefaria.

    Args:
        book: Book name (e.g., 'Genesis', 'Exodus')
        chapter: Chapter number
        start_verse: Starting verse number
        end_verse: Ending verse number

    Returns:
        Dict with Hebrew text array and metadata
    """
    # Construct the API URL
    if start_verse == end_verse:
        ref = f"{book}.{chapter}.{start_verse}"
    else:
        ref = f"{book}.{chapter}.{start_verse}-{end_verse}"

    url = f"https://www.sefaria.org/api/texts/{ref}"

    # Use context=0 to get only the requested verses without surrounding context
    response = requests.get(url, params={"context": 0})
    response.raise_for_status()

    data = response.json()

    return {
        "ref": data.get("ref"),
        "hebrew": data.get("he", []),
        "english": data.get("text", []),
    }


def count_words_and_verses_in_aliyah(verse_range: Dict) -> Dict[str, int]:
    """
    Count Hebrew words and verses in an aliyah by fetching text from Sefaria.

    Args:
        verse_range: Parsed verse range dict from hebcal_fetcher

    Returns:
        Dict with 'word_count' and 'verse_count'
    """
    book = verse_range["book"]
    start_ch = verse_range["start_chapter"]
    start_v = verse_range["start_verse"]
    end_ch = verse_range["end_chapter"]
    end_v = verse_range["end_verse"]

    total_words = 0
    total_verses = 0

    # Handle single chapter case
    if start_ch == end_ch:
        try:
            data = fetch_hebrew_text(book, start_ch, start_v, end_v)
            hebrew_verses = data["hebrew"]

            if isinstance(hebrew_verses, list):
                total_verses = len(hebrew_verses)
                for verse in hebrew_verses:
                    total_words += count_hebrew_words(verse)
            else:
                total_verses = 1
                total_words += count_hebrew_words(hebrew_verses)

            # Small delay to be respectful to the API
            time.sleep(0.1)

        except Exception as e:
            print(f"Error fetching {book} {start_ch}:{start_v}-{end_v}: {e}")
            return {"word_count": 0, "verse_count": 0}

    else:
        # Multi-chapter case - fetch each chapter separately
        # First chapter (from start_v to end)
        try:
            data = fetch_hebrew_text(book, start_ch, start_v, 999)
            hebrew_verses = data["hebrew"]
            if isinstance(hebrew_verses, list):
                total_verses += len(hebrew_verses)
                for verse in hebrew_verses:
                    total_words += count_hebrew_words(verse)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching {book} {start_ch}:{start_v}-end: {e}")

        # Middle chapters (if any)
        for ch in range(start_ch + 1, end_ch):
            try:
                data = fetch_hebrew_text(book, ch, 1, 999)
                hebrew_verses = data["hebrew"]
                if isinstance(hebrew_verses, list):
                    total_verses += len(hebrew_verses)
                    for verse in hebrew_verses:
                        total_words += count_hebrew_words(verse)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error fetching {book} {ch}: {e}")

        # Last chapter (from 1 to end_v)
        try:
            data = fetch_hebrew_text(book, end_ch, 1, end_v)
            hebrew_verses = data["hebrew"]
            if isinstance(hebrew_verses, list):
                total_verses += len(hebrew_verses)
                for verse in hebrew_verses:
                    total_words += count_hebrew_words(verse)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching {book} {end_ch}:1-{end_v}: {e}")

    return {"word_count": total_words, "verse_count": total_verses}
