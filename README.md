# VirusTotal Data Pipeline Challenge

This is a data pipeline that fetches threat intelligence from the VirusTotal API v3, stores it in a relational database (SQLite/PostgreSQL), implements an efficient caching backplane, and exposes the data via a fast REST API alongside a beautiful React frontend dashboard.

## Features
* **Data Ingestion**: Fetches API data asynchronously from VirusTotal.
* **Caching Strategy**: 
    1. **Primary Cache (In-Memory/Redis)**: Keeps ultra-fast lookups for frequently accessed indicators.
    2. **Secondary Cache (Database)**: Persists data systematically with SQLAlchemy to minimize underlying VT API calls.
* **REST API**: Built with FastAPI. Supports querying specific resource types and forced regeneration endpoints.
* **Interactive React Dashboard**: A specialized glassmorphism-styled GUI built with Vite to visualize detection stats, lookup history, and cache sources efficiently.

## Prerequisites
* Python 3.9+ 
* Node.js (v18+)

## Setup
1. Clone the repository / initialize the project environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install greenlet # needed for async DB connections
    ```

2. Generate API Key:
    * Go to VirusTotal and create a free account.
    * Once logged in, navigate to your API Key under the profile section. Copy it.

3. Complete `.env` configuration:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and replace the placeholder value with your actual VirusTotal API key.

## Usage
Start the Uvicorn standalone ASGI server to run the backend API locally:

```bash
uvicorn main:app --reload
```
Then visit `http://127.0.0.1:8000/docs` in your browser to access the interactive Swagger API docs where you can test the APIs (or easily send CURL requests).

### React Frontend Dashboard
To launch the interactive user interface, open a second terminal window and run:
```bash
cd frontend
npm install
npm run dev
```
Then visit `http://localhost:5173/` in your browser to access the metrics dashboard and effortlessly lookup domains, IPs, and file hashes!

### Endpoints
* `GET /api/v1/domains/{domain}`: Lookup reputation tracking for isolated domains.
* `GET /api/v1/ips/{ip}`: Retrieve Autonomous System (ASN) origins and IP routing history.
* `GET /api/v1/files/{hash}`: Fetch matching SHA-256 analysis records and metadata.
    * All endpoints return data based on the optimal cache source (`cache`, `database`, or direct `virustotal` query).
    * Pass the `?refresh=true` query parameter to bypass caching mechanisms completely and forcefully fetch upstream data.
