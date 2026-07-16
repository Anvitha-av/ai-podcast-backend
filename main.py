import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(title="AI Podcast Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing!")

if not MURF_API_KEY:
    raise RuntimeError("MURF_API_KEY is missing!")

client = genai.Client(api_key=GEMINI_API_KEY)


class PodcastRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Podcast Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/generate")
def generate_podcast(request: PodcastRequest):

    try:
        prompt = f"""
Generate a podcast script under 2500 characters suitable for text-to-speech narration.

Topic:
{request.text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        script = response.text

        murf_response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers={
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": script,
                "voiceId": "Natalie",
                "locale": "en-US"
            },
            timeout=60
        )

        murf_response.raise_for_status()

        murf_data = murf_response.json()

        return {
            "success": True,
            "script": script,
            "audio": murf_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )