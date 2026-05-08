# AI Risk Narrative Generator

AI Risk Narrative Generator is a production-ready Flask microservice that generates business-grade risk descriptions, recommendations, and structured reports using the Groq `llama-3.3-70b-versatile` model.

## Features

- Flask JSON API with modular blueprints
- Redis caching with SHA256 key hashing and 15-minute TTL
- Async AI request pipeline with retries and graceful fallback
- Security hardening with headers, validation, sanitization, and rate limiting
- Professional prompt engineering for risk narratives, recommendations, and reports
- Docker ready with Compose support

## Installation

1. Clone the repository.
2. Change into the project folder.
3. Create a Python 3.11 virtual environment.
4. Install dependencies.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root with:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
REDIS_HOST=localhost
REDIS_PORT=6379
FLASK_ENV=development
```

## Running Locally

```bash
python app.py
```

The service starts on `http://127.0.0.1:5000`.

## API Endpoints

### POST /describe

Request:

```json
{
  "risk_type": "Cybersecurity",
  "severity": "High",
  "details": "Potential phishing attack detected"
}
```

Curl example:

```bash
curl -X POST http://127.0.0.1:5000/describe \
  -H "Content-Type: application/json" \
  -d '{"risk_type":"Cybersecurity","severity":"High","details":"Potential phishing attack detected"}'
```

### POST /recommend

Request:

```json
{
  "risk_type": "Cybersecurity",
  "severity": "High",
  "details": "Potential phishing attack detected"
}
```

### POST /generate-report

Request:

```json
{
  "risk_type": "Cybersecurity",
  "severity": "High",
  "details": "Potential phishing attack detected"
}
```

### GET /health

Response:

```json
{
  "status": "healthy",
  "model": "llama-3.3-70b-versatile",
  "uptime": "00:05:24",
  "average_response_time": "0.48s",
  "cache": "connected"
}
```

## Postman

Import the endpoints above into Postman as raw JSON requests. Set `Content-Type: application/json`.

## Docker

Build and run with Docker:

```bash
docker build -t ai-risk-narrative-generator .
docker run --env-file .env -p 5000:5000 ai-risk-narrative-generator
```

Or with Docker Compose:

```bash
docker compose up --build
```

## Testing

Run the test suite with:

```bash
pytest
```

## Production

Use Gunicorn for production deployment:

```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```
