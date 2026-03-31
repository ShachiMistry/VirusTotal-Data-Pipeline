# 🛡️ VirusTotal Data Pipeline

A production-ready data pipeline that ingests threat intelligence from the VirusTotal API v3, securely persists it in a relational database, provides efficient caching strategies, and exposes a clean, interactive React dashboard for Security Operations visualization.

## ✨ Key Features

- **Asynchronous Threat Ingestion**: Built utilizing modern `async` principles using FastAPI and `httpx`.
- **Advanced Rate Limiting**: Intelligent token-bucket algorithms built-in to respectfully comply with VirusTotal's strict API quotas (4 requests/minute).
- **Dual-Tier Caching Architecture**: Configurable abstraction layer utilizing `Redis` by default with an automatic fallback to an efficient, in-memory TTL mechanism.
- **Relational Persistence Layer**: Extracted JSON VT reports mapped perfectly onto a seamless SQLite/PostgreSQL `SQLAlchemy` ORM foundation.
- **Dynamic React Dashboard**: A specialized security glassmorphism-styled metrics GUI without heavy component dependencies using pure CSS arrays.
- **Comprehensive Test Suite**: Handled using `pytest` async event loops simulating both the backend REST calls and mocking engine outputs gracefully.

## 🛠️ Architecture Tech Stack

**Backend System**
- **Framework:** FastAPI / Uvicorn
- **Database / ORM:** SQLite (`aiosqlite`), SQLAlchemy 2.0
- **HTTP/Cache Control:** `httpx`, `tenacity` (retries), `redis.asyncio`
- **Testing:** `pytest`, `pytest-asyncio`

**Frontend Dashboard**
- **Core Library:** React 18 / Vite
- **Styling:** Vanilla Hand-Rolled Glassmorphic CSS (No bulky external UI framework)
- **Communications:** Native browser Fetch API with FastAPI CORS routing

---

## 🚀 Quickstart Guide

### 1. Requirements
Ensure you have the following installed natively on your system:
- Python 3.9+ 
- Node.js (v18+)

### 2. Backend Setup
Clone this repository and boot up the main virtual environment:

```bash
git clone https://github.com/ShachiMistry/VirusTotal-Data-Pipeline.git
cd VirusTotal-Data-Pipeline

# Prepare Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Core & Async Packages
pip install -r requirements.txt
pip install greenlet # needed for async SQL
```

### 3. Environment Context
Before initializing the service, create your `.env` file referencing the `.env.example` configurations. Place your custom VT API key here.

```bash
cp .env.example .env
```

### 4. Running the Servers
You will need two terminals running simultaneously for full-stack interactivity.

**Terminal 1 (FastAPI Backend)**
```bash
source venv/bin/activate
uvicorn main:app --reload
# API running at: http://localhost:8000
```
**Terminal 2 (React Frontend)**
```bash
cd frontend
npm install
npm run dev
# Dashboard available at: http://localhost:5173
```

---

## 📡 API Endpoints 
The backend REST endpoints natively power the frontend dashboard but behave wonderfully alone through HTTP REST clients as well. 

You can append `?refresh=true` queries manually to force-bust the persistence engines straight to VirusTotal's backend.

| Method | Endpoint | Description |
| ---- | --------- | ----------- |
| `GET` | `/api/v1/domains/{domain}` | Lookup reputation tracking for isolated domains. |
| `GET` | `/api/v1/ips/{ip}` | Retrieve Autonomous System (ASN) origins and IP routing history. |
| `GET` | `/api/v1/files/{hash}` | Fetch matching SHA-256 analysis records and sizes. |
| `GET` | `/health` | Diagnostic ping for monitoring up-time integrations. |

> Interactive Swagger documentation auto-generates live at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🗃️ Application Structure

```text
virustotal-pipeline/
├── .env.example
├── main.py                    # Application Entrypoint & Lifespans
├── requirements.txt
├── app/
│   ├── core/                  # Configurations, Logging & Rate Tokens
│   ├── db/                    # DB Async Connectors
│   ├── models/                # SQLAlchemy ORM Tables (Reports, IPs, Hashes)
│   ├── services/              # Pipeline Logic (VT Client + Cache Backends)
│   └── api/routes/            # Exposed FastAPI Routers
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx            # React Dashboard Component 
│       ├── App.css            # Glassmorphism UI Variables 
│       └── main.jsx           # App Mount
└── tests/
    └── test_*.py              # Comprehensive Mock Pipeline Validations
```

---
*Created and Architected for Security Intelligence Visualization.*
