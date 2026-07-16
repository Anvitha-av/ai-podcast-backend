import os
import requests
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

from google.genai.errors import ServerError
import time

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

VOICE_MAP = {
    "English": {
        "voiceId": "Natalie",
        "locale": "en-US"
    },
    "Hindi": {
        "voiceId": "hi-IN-sunaina",
        "locale": "hi-IN"
    },
    "Kannada": {
        "voiceId": "Ruby",
        "locale": "kn-IN"
    }
}

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing!")

if not MURF_API_KEY:
    raise RuntimeError("MURF_API_KEY is missing!")

client = genai.Client(api_key=GEMINI_API_KEY)


class PodcastRequest(BaseModel):
    text: str
    language: str


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


@app.post("/generate")
def generate_podcast(request: PodcastRequest):

    try:

        # Get voice configuration
        voice = VOICE_MAP.get(request.language)

        if not voice:
            raise HTTPException(
                status_code=400,
                detail="Unsupported language selected."
            )

        prompt = f"""
Generate a podcast script in {request.language}.

Requirements:
- Write ONLY in {request.language}.
- Keep it under 2500 characters.
- Make it engaging and conversational.
- Make it sound like a real podcast host.
- Do not use markdown.

Topic:
{request.text}
"""

        # Retry Gemini request up to 3 times
        response = None

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt
                )
                break

            except ServerError:
                if attempt == 2:
                    raise HTTPException(
                        status_code=503,
                        detail="AI service is temporarily busy. Please try again in a few seconds."
                    )

                time.sleep(3)

        script = response.text

        murf_response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers={
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": script,
                "voiceId": voice["voiceId"],
                "locale": voice["locale"]
            },
            timeout=60
        )

        if not murf_response.ok:
            print("Murf Error:", murf_response.text)
            raise HTTPException(
                status_code=400,
                detail=murf_response.text
    )

        return murf_response.json()

    except HTTPException:
        raise

    except requests.exceptions.HTTPError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Murf API Error: {str(e)}"
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Server Error: {str(e)}"
        )