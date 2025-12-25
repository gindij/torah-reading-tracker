# Torah Reading Tracker

A web application to track your progress through the annual Torah readings by word count, verse count, and aliyah count.

## Features

- Track completion of aliyot (7 per parsha, excluding maftir)
- View progress by words, verses, and aliyot
- Weekly view with detailed aliyah information
- Annual overview showing progress across all parshiot
- Persistent progress tracking using CSV file storage
- Real Hebrew word counts from Sefaria API

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- uv (Python package manager)

### Installation

1. Install Python dependencies:
```bash
uv sync
```

2. Install frontend dependencies:
```bash
cd frontend && npm install && cd ..
```

3. Initialize Torah reading data:
```bash
uv run python backend/data_fetcher/initialize_data.py
```

This will fetch all 54 Torah parshiot with word counts from Hebcal and Sefaria APIs and save to `data/torah_readings_complete.json`.

## Running the Application

### Option 1: Run both servers manually

Terminal 1 - Start Flask API:
```bash
uv run python -m backend.api.app
```

Terminal 2 - Start React frontend:
```bash
cd frontend && npm run dev
```

Then open http://localhost:5173 in your browser.

### Option 2: Use the run script

```bash
./run.sh
```

This will start both servers. Access the app at http://localhost:5173.

## Project Structure

```
.
├── backend/
│   ├── api/
│   │   └── app.py              # Flask API server
│   └── data_fetcher/
│       ├── hebcal_fetcher.py   # Fetch aliyah structure from Hebcal API
│       ├── sefaria_fetcher.py  # Fetch Hebrew text and counts from Sefaria API
│       ├── initialize_data.py  # Initialize complete Torah data
│       └── progress_tracker.py # CSV-based progress tracking
├── frontend/
│   └── src/
│       ├── App.jsx             # Main app component
│       ├── WeeklyView.jsx      # Weekly parsha view
│       ├── AnnualOverview.jsx  # Annual progress overview
│       ├── Stats.jsx           # Overall statistics
│       └── api.js              # API client
├── data/
│   ├── torah_readings_complete.json  # Complete Torah data (all 54 parshiot)
│   └── progress.csv                  # Your reading progress
└── tests/                       # Test files
```

## Data Sources

- **Hebcal API**: Provides Torah reading structure and aliyah divisions
- **Sefaria API**: Provides Hebrew text for word counting

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black backend/
uv run isort backend/
```

## Progress Tracking

Your reading progress is stored in `data/progress.csv`. This file is automatically created and updated as you mark aliyot complete in the UI.

## Notes

- Tracks all 54 weekly Torah portions (parshiot)
- Maftir aliyot are not counted
- Word and verse counts are fetched from actual Hebrew text via Sefaria API
- The Flask API runs on port 5001 (port 5000 conflicts with macOS AirPlay)
- All data is stored locally - no external database required
- Progress is cached in memory for performance
