# FitBuddy – AI Fitness Plan Generator (Gemini)

Web app that generates a personalized weekly workout plan and nutrition tips
for weight loss, muscle gain, or general wellness. Built with FastAPI and Gemini.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your Gemini API key
uvicorn main:app --reload
```
Open http://127.0.0.1:8000 (API docs at /docs).

## Structure
- `main.py` – FastAPI app, `/api/plan` endpoint, Gemini call with JSON output
- `static/index.html` – single-page frontend (form + plan view)
- `.env.example` – environment variables

## Ideas to extend
User accounts, saved plans (SQLite), progress tracking, PDF export.
Plans are general guidance, not medical advice.
