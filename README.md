---
title: WhatsApp Catalog AI
emoji: 📦
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# WhatsApp Catalog AI

A FastAPI-based middleware that receives unstructured WhatsApp messages, extracts structured business catalog data using an LLM, stores the results in a database, and serves them through a REST API and a responsive frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue?logo=docker&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hosted-Hugging%20Face%20Spaces-yellow?logo=huggingface&logoColor=white)

## Live Demo

🚀 **[Open Live App on Hugging Face Spaces](https://huggingface.co/spaces/zeev72/whatsapp-catalog-ai)**

## Overview

This project is intended for workflows where:

- incoming WhatsApp messages are unstructured
- an AI model is needed to extract catalog information
- the extracted data should be stored in a persistent cloud database
- the catalog must be accessible through a simple web interface

## Features

- AI-powered extraction for `product_name`, `location`, `menus`, and `unique_selling_point`
- WhatsApp webhook endpoint with background processing
- per-sender rate limiting
- database persistence via SQLAlchemy (supports both SQLite and PostgreSQL)
- automatic database seeding on container startup
- seed logic with upsert behavior per `user_id`
- built-in responsive frontend served directly by FastAPI
- frontend default view that shows all catalogs before filtering by WhatsApp number
- automatic deployment to Hugging Face Spaces via GitHub Actions

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| AI / LLM | LangChain, Groq |
| Database | PostgreSQL (production), SQLite (local dev) |
| Configuration | Pydantic Settings |
| Frontend | HTML, CSS, JavaScript (served by FastAPI) |
| Testing | Pytest, HTTPX |
| Deployment | Docker, Hugging Face Spaces |
| CI/CD | GitHub Actions |

## Application Flow

```text
WhatsApp Message
      |
      v
POST /api/v1/whatsapp-catalog
      |
      v
Background task calls the AI extractor
      |
      v
Extracted result is upserted into PostgreSQL
      |
      +--> GET /               -> frontend UI (KatalogKu)
      |
      +--> GET /api/v1/catalogs/                -> all catalogs (JSON)
      |
      `--> GET /api/v1/catalogs/users/{user_id}/catalogs
                                               -> filter by WhatsApp number (JSON)
```

## Screenshots

![Homepage](docs/screenshots/homepage.png)
![Filter By Phone](docs/screenshots/filter-phone.png)
![Swagger Docs](docs/screenshots/swagger-docs.png)

## Project Structure

```text
whatsapp-catalog-ai/
|- .github/
|  `- workflows/
|     `- huggingface.yml        # auto-sync to HF Spaces on push
|- app/
|  |- api/
|  |  |- catalog.py
|  |  `- webhook.py
|  |- core/
|  |  |- config.py
|  |  |- database.py
|  |  `- logger.py
|  |- models/
|  |  |- pydantic_schemas.py
|  |  `- schema.py
|  `- services/
|     `- ai_extractor.py
|- tests/
|  |- test_api.py
|  `- test_webhook.py
|- wa-catalog-frontend/
|  |- app.js
|  |- index.html
|  `- styles.css
|- docs/
|  `- screenshots/
|- docker-entrypoint.sh
|- Dockerfile
|- main.py
|- requirements.txt
`- seed.py
```

## Deployment (Hugging Face Spaces)

This project is deployed on **Hugging Face Spaces** using Docker. Deployment is fully automated:

1. Push code to the `main` branch on GitHub.
2. GitHub Actions (`.github/workflows/huggingface.yml`) automatically syncs the code to Hugging Face Spaces.
3. Hugging Face builds the Docker container and starts the application.

### Required Secrets

#### GitHub Repository Secrets

| Secret | Description |
|---|---|
| `HF_TOKEN` | Hugging Face Access Token (Write) for auto-sync |

#### Hugging Face Space Secrets

Set these in **Space Settings > Variables and secrets**:

| Secret | Description |
|---|---|
| `GROQ_API_KEY` | API key for Groq LLM |
| `DATABASE_URL` | PostgreSQL connection string (e.g., from Supabase) |
| `LANGCHAIN_TRACING_V2` | `true` to enable LangSmith tracing |
| `LANGCHAIN_ENDPOINT` | `https://api.smith.langchain.com` |
| `LANGCHAIN_API_KEY` | LangSmith API key |
| `LANGCHAIN_PROJECT` | LangSmith project name |

### Database

The production deployment uses **PostgreSQL** via [Supabase](https://supabase.com/) (free tier). Use the **Connection Pooler** URI (port `6543`) instead of the direct connection to avoid IPv6 issues on Hugging Face.

Example `DATABASE_URL` format:

```
postgresql://postgres.xxxxx:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## Local Development

1. Clone the repository:

```bash
git clone https://github.com/subki72/whatsapp-catalog-ai.git
cd whatsapp-catalog-ai
```

2. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=sqlite:///./catalog_db.sqlite
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=Wa bot katalog
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Seed the database:

```bash
python seed.py
```

5. Start the server:

```bash
uvicorn main:app --reload --port 8000
```

6. Open `http://127.0.0.1:8000` in your browser to see the frontend UI.

## Seed Behavior

The [seed.py](./seed.py) uses upsert logic:

- if a `user_id` does not exist, a new row is inserted
- if a `user_id` already exists, the row is updated
- if `FORCE_RESEED=true`, the `catalogs` table is cleared before reseeding

New entries added to the seed list are loaded without deleting existing data.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Frontend UI (KatalogKu) |
| `GET` | `/health` | Health check (JSON) |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/api/v1/whatsapp-catalog` | Receives incoming WhatsApp webhook payloads |
| `GET` | `/api/v1/catalogs/` | Returns all catalogs (JSON) |
| `GET` | `/api/v1/catalogs/users/{user_id}/catalogs` | Returns catalogs filtered by WhatsApp number |

## Frontend

The frontend is served directly by FastAPI from the `wa-catalog-frontend/` directory:

- static files (CSS, JS) are mounted at `/static/`
- the root URL `/` serves the `index.html` page
- the frontend uses relative API URLs (`/api/v1/catalogs`) so it works on any host

Current behavior:

- when the page loads, all catalogs are displayed by default
- the WhatsApp number input is used to filter catalogs by user
- the `Show All` button restores the full catalog list
- the layout is responsive for mobile, tablet, and desktop screens

## Troubleshooting

### The frontend shows "Gagal terhubung ke server"

- ensure the backend is running
- check the browser console for CORS or network errors
- for local development, verify `DATABASE_URL` in `.env`

### Database connection fails on Hugging Face

- use the Supabase **Connection Pooler** URI (not direct connection)
- the pooler URL uses port `6543` and a hostname like `aws-0-...pooler.supabase.com`
- direct connections (port `5432`, hostname `db.xxx.supabase.co`) may fail due to IPv6

### `seed.py` fails locally

- ensure dependencies are installed: `pip install -r requirements.txt`
- ensure `DATABASE_URL` in `.env` points to a valid local or remote database

## Important Notes

- `.env` contains secrets and must not be published to GitHub
- if any API key has been exposed, rotate it immediately
- the GitHub Actions workflow automatically syncs to Hugging Face on every push to `main`

## License

MIT
