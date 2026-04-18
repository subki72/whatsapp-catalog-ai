# WhatsApp Catalog AI Backend

This is the backend system for the **WhatsApp Catalog AI Bot**, powered by FastAPI, SQLAlchemy (SQLite), and LangChain (Groq Llama-3).

## Features
- **AI-Powered Extraction**: Automatically reads unstructured WhatsApp chats and extracts `Product Name`, `Location`, `Menus`, and `Unique Selling Points`.
- **Fonnte Webhook Integration**: Accepts incoming Webhooks from WhatsApp providers (Fonnte).
- **Background Processing**: Heavy AI tasks run asynchronously in the background to prevent provider timeouts.
- **REST API**: Provides endpoints to fetch user catalogs.

## Installation & Setup

1. **Clone the repository** (or navigate to this folder).
2. **Create a virtual environment (Conda / Venv):**
   ```bash
   conda create -n wa-catalog-ai python=3.10
   conda activate wa-catalog-ai
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables (.env)**
   Add your `GROQ_API_KEY` and Fonnte Token to the `.env` file or `app/api/webhook.py`.
   Make sure you comment out the Docker override `DATABASE_URL` in `.env` if running locally.

## Running the Server Locally

```bash
uvicorn main:app --reload --port 8001
```
*(If port 8000 is occupied, you can change the port to `8001` or any available port)*

## Docker Deployment (Production)

You can containerize this app easily using the included Docker setup.
```bash
docker-compose up -d --build
```
This will run the server in the background and persist your database inside the `/data/` volume.

## Endpoints
- `POST /api/v1/whatsapp-catalog`: Fonnte incoming Webhook Endpoint
- `GET /api/v1/catalogs/users/{user_id}/catalogs`: Get a user's generated catalogs

## Testing
To test the webhook locally without Fonnte:
```bash
python test_webhook.py
```
