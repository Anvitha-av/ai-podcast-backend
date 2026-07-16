# 🎙️ AI Podcast Backend

Backend API for the AI Podcast Generator.

This FastAPI application generates podcast scripts using Google Gemini and converts them into speech using Murf AI.

---

## 🚀 Live API

https://ai-podcast-backend-production.up.railway.app

Swagger Documentation:

https://ai-podcast-backend-production.up.railway.app/docs

---

## Features

- AI podcast script generation
- Text-to-Speech conversion
- REST API
- FastAPI
- Railway Deployment

---

## API Endpoints

### GET /

Returns backend status.

### POST /generate

Request

```json
{
  "text": "Artificial Intelligence"
}
```

Response

```json
{
  "audioFile": "https://..."
}
```

---

## Tech Stack

- Python
- FastAPI
- Google Gemini API
- Murf AI API
- Railway

---

## Installation

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn main:app --reload
```

---

## Author

Anvitha A V
