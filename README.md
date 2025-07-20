# Airguardian Backend (drone-rush)

## Overview

Airguardian is a backend system for real-time monitoring of drone activity near restricted airspace. It detects and logs violations of a No-Fly Zone (NFZ) and exposes API endpoints for health checks, real-time drone data, and recent violations.

---

## Features

- **Fetches drone position data** from an external API every 10 seconds using Celery.
- **Detects violations** when drones enter a 1,000-unit radius NFZ centered at (0, 0).
- **Fetches owner information** only for violating drones.
- **Stores violations** in a PostgreSQL database.
- **Exposes API endpoints** for health, drone data, and violations from the last 24 hours.
- **Basic error handling and logging** using Python’s logging module.

---

## Requirements

- Python 3.13+
- Poetry (for dependency management)
- Docker & Docker Compose (for local development)
- PostgreSQL and Redis (provided via Docker Compose)

---

## Setup

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd drone_rush
```

### 2. Environment Variables

- Copy `.env.example` to `.env` and fill in the required values:
  ```sh
  cp .env.example .env
  ```
- **Do not commit your `.env` file!**
## Running the Application

### Using Docker Compose (recommended)

This will start the FastAPI app, Celery worker, PostgreSQL, and Redis:

```sh
docker-compose up --build -d
```

- FastAPI app: [http://localhost:8000](http://localhost:8000)
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Accessing Services

When running with Docker Compose, you can access the following services:

- **Backend API (FastAPI):**  
  [http://localhost:8000](http://localhost:8000)  
  Use this URL to access the backend API endpoints from your browser or API client.

- **Frontend (React app):**  
  [http://localhost:3000](http://localhost:3000)  
  Open this URL in your browser to use the web interface.

- **PostgreSQL Database:**  
  Host: `localhost`  
  Port: `5432`  
  Use these settings in your database client or application configuration.

- **Redis:**  
  Host: `localhost`  
  Port: `6379`  
  Use these settings for connecting to Redis.

> The database and Redis ports are mapped for local development and are intended for internal use or advanced users (e.g., connecting with a database GUI or Redis CLI).

### Running Locally (without Docker)

1. Start PostgreSQL and Redis locally.
2. Ensure your `.env` points to the correct local services.
3. Start the FastAPI app:
   ```sh
   poetry run uvicorn drone_rush:app --reload
   ```
4. Start the Celery worker:
   ```sh
   poetry run celery -A drone_rush.celery_bot.celery_app worker --beat --loglevel=info
   ```

---

## API Endpoints

### `GET /health`
- Health check endpoint.
- Response: `{"success": "ok"}`

### `GET /drones`
- Proxies real-time drone data from the external API.
- Returns a list of drones with their positions.

### `GET /nfz`
- Returns all violations detected in the last 24 hours.
- **Requires** header: `X-Secret: <your-secret-key>`
- Response: List of violation records with drone and owner info.

---

## Logging

- In Docker, view logs with `docker-compose logs web` or `docker-compose logs celery_worker`.
- To log to a file, modify the `logging.basicConfig` call in the code (see `main.py`, `logic.py`, and `celery_bot.py`).
- Docker logs are stored on the host at `/var/lib/docker/containers/<container-id>/<container-id>-json.log` (Linux), but are usually accessed via Docker commands.

---

## Development Notes

- **No secrets or API URLs are hardcoded**; all configuration is via environment variables.
- **Celery** schedules the drone data fetch every 10 seconds.
- **Violations** are only stored if a drone enters the NFZ.
- **Owner info** is fetched only for violating drones to minimize external API calls.
- All API endpoints use Pydantic models for request/response validation.
