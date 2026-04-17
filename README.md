# WhatsApp Catalog AI

An AI-powered middleware that receives unstructured WhatsApp business messages, extracts structured product catalog data using LLM, and serves it through a REST API and a glassmorphism web frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Groq_Llama_3.3-orange?logo=chainlink&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **AI-Powered Extraction** — Parses unstructured WhatsApp chat messages and extracts `Product Name`, `Location`, `Menu List`, and `Unique Selling Point` using Groq Llama-3.3-70B via LangChain.
- **Webhook Integration** — Accepts incoming webhooks from WhatsApp providers (e.g., Fonnte) and replies automatically.
- **Upsert Logic** — Intelligently updates existing catalog entries or creates new ones based on the sender's phone number.
- **Background Processing** — AI extraction and database operations run asynchronously to prevent webhook timeouts.
- **Rate Limiting** — Built-in per-sender anti-spam protection (max 3 requests/minute).
- **Centralized Logging** — Consistent structured logging across all modules.
- **Web Frontend** — A responsive glassmorphism UI that displays all catalogs with search-by-phone functionality.
- **Docker Ready** — Includes `Dockerfile` and `docker-compose.yml` for one-command deployment.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn |
| AI / LLM | LangChain + Groq (Llama-3.3-70B) |
| Database | SQLAlchemy + SQLite |
| Data Validation | Pydantic v2 |
| Frontend | Vanilla HTML/CSS/JS (Glassmorphism UI) |
| Testing | Pytest + HTTPX (async) |
| Deployment | Docker + Docker Compose |

## Project Structure

```
whatsapp-catalog-ai/
├── main.py                  # FastAPI app entrypoint
├── seed.py                  # Database seeder with sample F&B data
├── test_webhook.py          # Manual webhook test script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                     # API keys (not committed)
│
├── app/
│   ├── api/
│   │   ├── webhook.py       # WhatsApp webhook endpoint + rate limiter
│   │   └── catalog.py       # REST API for catalog data
│   ├── core/
│   │   ├── config.py        # Environment settings (Pydantic)
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   └── logger.py        # Centralized logger
│   ├── models/
│   │   ├── schema.py        # SQLAlchemy ORM model
│   │   └── pydantic_schemas.py  # Request/response schemas
│   └── services/
│       └── ai_extractor.py  # LangChain AI extraction chain
│
├── tests/
│   └── test_api.py          # Async API tests (webhook + rate limit)
│
└── wa-catalog-frontend/
    ├── index.html
    ├── app.js               # Fetch API + dynamic card rendering
    ├── styles.css
```

## Getting Started

### Prerequisites

- Python 3.10+
- [Groq API Key](https://console.groq.com/) (free tier available)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-catalog-ai.git
cd whatsapp-catalog-ai

# Create virtual environment
conda create -n wa-catalog-ai python=3.10
conda activate wa-catalog-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=wa-catalog-bot
```

### 3. Run the Server

```bash
uvicorn main:app --reload --port 8001
```

The API will be available at `http://127.0.0.1:8001`. Interactive docs at `/docs`.

### 4. Seed Sample Data (Optional)

```bash
python seed.py
```

This populates the database with 12 sample Indonesian F&B business catalogs.

### 5. Open the Frontend

Open `wa-catalog-frontend/index.html` in your browser. Make sure the backend is running on the same port configured in `app.js`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/whatsapp-catalog` | Incoming WhatsApp webhook |
| `GET` | `/api/v1/catalogs/` | Get all catalogs (randomized) |
| `GET` | `/api/v1/catalogs/users/{user_id}/catalogs` | Get catalogs by phone number |

## Testing

```bash
# Run async API tests
pytest tests/ -v

# Manual webhook test (server must be running)
python test_webhook.py
```

## Docker Deployment

```bash
docker-compose up -d --build
```

This runs the server on port `8000` with the SQLite database persisted in the `./data/` volume.

## License

This project is licensed under the MIT License.
