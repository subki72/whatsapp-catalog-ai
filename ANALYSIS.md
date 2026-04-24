# Project Bottleneck Analysis

This document outlines the analysis of the WhatsApp Catalog AI project, evaluating potential bottlenecks across performance, security, and business logic.

## 1. Performance Bottlenecks

### A. AI Processing in Background Tasks
*   **Issue:** The AI extraction (`extractor.extract_catalog_data`) occurs within a FastAPI `BackgroundTasks`. While this prevents blocking the initial HTTP request, it means the API server itself is handling computationally/network-heavy AI tasks. Under high load (many concurrent WhatsApp messages), this can starve the API server of resources, block the event loop, and potentially crash the Uvicorn workers.
*   **Recommendation:** Offload AI processing to a dedicated asynchronous task queue (e.g., Celery or RQ backed by Redis). This decouples the web server from the heavy processing workers.

### B. Database Connection Management & SQLite Limitations
*   **Issue:** In `app/api/webhook.py`, `SessionLocal()` is manually instantiated inside the `background_process_wa_message` task, bypassing the standard `get_db` dependency pattern.
*   **Issue:** The project uses SQLite. SQLite has limited write concurrency (locking the entire database during a write). If multiple background tasks attempt to write to SQLite simultaneously under high traffic, it will lead to `database is locked` errors.
*   **Recommendation:** For production environments, migrate to a more robust RDBMS like PostgreSQL or MySQL that handles concurrent writes and connection pooling efficiently.

### C. In-Memory Rate Limiting
*   **Issue:** The `rate_limit_cache` in `app/api/webhook.py` uses an in-memory Python `defaultdict`.
*   **Issue:** This approach fails in a multi-worker setup (e.g., running multiple Gunicorn/Uvicorn workers or scaling across multiple containers/pods). Each worker maintains its own isolated rate limit cache, rendering the rate limiting ineffective.
*   **Recommendation:** Migrate the rate limiting state to a centralized, high-performance store like Redis.

---

## 2. Security Bottlenecks / Risks

### A. Hardcoded Authentication Tokens
*   **Issue:** The Fonnte API token is hardcoded in `app/api/webhook.py` (`"Authorization": "YOUR_FONNTE_TOKEN_HERE"`). This is a critical security risk.
*   **Recommendation:** Move this sensitive credential to environment variables (`.env`) and manage it via Pydantic `settings`.

### B. Overly Permissive CORS Configuration
*   **Issue:** In `main.py`, CORS is configured with `allow_origins=["*"]`. This permits any domain to make cross-origin requests to your API.
*   **Recommendation:** Restrict `allow_origins` to explicitly trusted domains (e.g., the production URL of your frontend application).

### C. Missing Webhook Authentication
*   **Issue:** The `/api/v1/whatsapp-catalog` endpoint blindly accepts incoming POST requests without verifying their origin. An attacker could flood this endpoint with fake payloads, spamming the database and exhausting your Groq API credits.
*   **Recommendation:** Implement robust authentication for the webhook. Require a shared secret token in the headers or validate cryptographic signatures if provided by the webhook sender (Fonnte).

### D. LLM Prompt Injection & Output Validation
*   **Issue:** The system relies on the LLM's output to populate the database. While SQLAlchemy mitigates traditional SQL injection, there is a risk of Prompt Injection where a user crafts a message to manipulate the LLM output into returning malicious strings or exceptionally large payloads.
*   **Recommendation:** Implement strict validation and sanitization on the extracted Pydantic model (`CatalogItem`) before database insertion. Set maximum string lengths for all fields.

---

## 3. Business Bottlenecks

### A. Single Catalog per User (Upsert Logic)
*   **Issue:** The logic in `webhook.py` performs an upsert based on `user_id`. If an existing user sends a new message, their previous catalog is overwritten.
*   **Issue:** This inherently limits a business owner to having only **one** active catalog. If they wish to manage multiple distinct catalogs (e.g., they run two different types of businesses), the system does not support it.
*   **Recommendation:** Re-evaluate the business requirements. Consider changing the data model to allow a one-to-many relationship between a user and their catalogs.

### B. Poor Error Recovery and User Feedback
*   **Issue:** When the AI fails to extract data, the system responds with a generic error: `"Sorry, the AI failed to process your sales data..."`. The user is not provided with actionable guidance on how to format their message for a better outcome.
*   **Issue:** Failures in database writes or Fonnte API interactions might result in silent failures from the user's perspective.
*   **Recommendation:** Improve error handling to provide specific, constructive feedback to the user. Implement robust internal alerting for unhandled exceptions.

### C. Hard Dependency on External LLM Provider
*   **Issue:** The core business process relies entirely on the availability and latency of Groq's `llama-3.3-70b-versatile` API.
*   **Recommendation:** Design a fallback mechanism. If Groq experiences downtime or high latency, have a secondary LLM provider or a gracefully degraded manual fallback process available.
