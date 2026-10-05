"""FitBuddy - AI fitness plan generator powered by Gemini models (FastAPI)."""
import json
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="FitBuddy", version="1.0.0")
client = genai.Client(api_key=API_KEY) if API_KEY else None


class PlanRequest(BaseModel):
    goal: Literal["weight_loss", "muscle_gain", "general_wellness"]
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    days_per_week: int = Field(4, ge=1, le=7)
    minutes_per_session: int = Field(45, ge=15, le=120)
    equipment: Literal["none", "home_basics", "full_gym"] = "none"
    diet: str = Field("no restrictions", max_length=80)


SYSTEM = (
    "You are FitBuddy, a certified-trainer-style assistant. Create safe, realistic "
    "plans. Respond with JSON only, matching this shape: "
    '{"summary": str, "weekly_plan": [{"day": str, "focus": str, '
    '"exercises": [{"name": str, "sets": int, "reps": str, "notes": str}]}], '
    '"nutrition_tips": [str], "safety_note": str}. '
    "Include rest days. Give 4-6 nutrition tips that respect the diet field."
)


@app.post("/api/plan")
def generate_plan(req: PlanRequest):
    if client is None:
        raise HTTPException(500, "GEMINI_API_KEY is not set. Add it to your .env file.")
    prompt = (
        f"Goal: {req.goal.replace('_', ' ')}\nLevel: {req.level}\n"
        f"Days per week: {req.days_per_week}\nSession length: {req.minutes_per_session} min\n"
        f"Equipment: {req.equipment.replace('_', ' ')}\nDiet: {req.diet}"
    )
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        return json.loads(resp.text)
    except json.JSONDecodeError:
        raise HTTPException(502, "The model returned an unreadable plan. Try again.")
    except Exception as exc:  # network, quota, auth
        raise HTTPException(502, f"Gemini request failed: {exc}")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL, "key_loaded": client is not None}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")
