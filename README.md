# VirusTotal Data Pipeline Challenge

This is a mini data pipeline that fetches data from the VirusTotal API, stores it in a relational database (SQLite), and exposes the data via an API. The project implements a robust two-layer caching strategy and handles VirusTotal API rate limits properly.

## Features
* **Data Ingestion**: Fetches API data from VirusTotal.
* **Smart Identifier Recognition**: Automatically detects and maps given identifiers to `domain`, `ip`, or `hash`.
* **Caching Strategy**: 
    1. **Primary Cache (In-Memory)**: Keeps ultra-fast lookup for frequently accessed IDs (TTL 60s).
    2. **Secondary Cache (Database)**: Persists data indefinitely but triggers staleness after a certain interval (TTL 24h by default) to minimize VT API calls.
* **REST API**: Built with FastAPI. Supports querying data and forced regeneration endpoints.

## Prerequisites
* Python 3.9+ 

## Setup
1. Clone the repository / initialize the project environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Generate API Key:
    * Go to VirusTotal and create a free account.
    * Once logged in, navigate to your API Key under the profile section. Copy it.

3. Complete `.env` configuration:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and replace the placeholder value with your actual actual VirusTotal API key.

## Usage
Start the Uvicorn standalone ASGI server to test the APIs locally:

```bash
uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` in your browser to access the interactive Swagger API docs where you can test the APIs (or easily send CURL requests).

### Endpoints
* `GET /api/v1/report/{identifier}`: Fetch data for domain, IP, or hash.
    * Returns data based on optimal cache source (memory, database, or direct VT query)
    * Pass `?force_refresh=true` keyword argument to bypass caching mechanisms entirely.
* `POST /api/v1/report/{identifier}/refresh`: Re-ingests and forcefully populates existing data back to Database caches. Completely ignores TTLs.
