"""FitBuddy - AI fitness plan generator (FastAPI + Gemini)."""
import json
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

app = FastAPI(title="FitBuddy")


class PlanRequest(BaseModel):
    goal: Literal["weight_loss", "muscle_gain", "general_wellness"]
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    days_per_week: int = Field(3, ge=1, le=7)
    equipment: Literal["none", "home_basics", "full_gym"] = "none"
    diet: str = Field("no restrictions", max_length=80)
    notes: str = Field("", max_length=300)


SYSTEM = """You are FitBuddy, a careful fitness coach. Return ONLY valid JSON:
{
  "summary": "2-3 sentence overview of the plan",
  "weekly_plan": [
    {"day": "Day 1", "focus": "string", "exercises": [
      {"name": "string", "sets": 3, "reps": "8-12", "notes": "short form cue"}
    ]}
  ],
  "nutrition_tips": ["5 short, practical tips matching the goal and diet"],
  "safety_note": "one sentence reminding the user to check with a doctor"
}
Give exactly the requested number of training days. Only use equipment the
user has. Do not give medical advice or extreme calorie targets."""


@app.post("/api/plan")
def generate_plan(req: PlanRequest):
    prompt = (
        f"Goal: {req.goal}\nLevel: {req.level}\nDays per week: {req.days_per_week}\n"
        f"Equipment: {req.equipment}\nDiet: {req.diet}\nNotes: {req.notes or 'none'}"
    )
    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        return json.loads(res.text)
    except json.JSONDecodeError:
        raise HTTPException(502, "The AI returned an unreadable plan. Try again.")
    except Exception as e:  # network, quota, bad key
        raise HTTPException(502, f"Could not reach Gemini: {e}")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
