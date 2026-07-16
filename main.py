import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


class PodcastRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "AI Podcast Backend Running"}


@app.post("/generate")
def generate_podcast(request: PodcastRequest):

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
            "api-key": MURF_API_KEY
        },
        json={
            "text": script,
            "voiceId": "Natalie",
            "locale": "en-US"
        }
    )

    murf_data = murf_response.json()

    return {
        "script": script,
        "audio": murf_data
    }