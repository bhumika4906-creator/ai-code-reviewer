# AI Code Reviewer

A modular Python backend and React frontend proving the concept for AI-assisted code review with static validation.

## Quick start

### Backend

```bash
cd backend
python -m venv venv
# Windows
# venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add a valid GROQ_API_KEY to .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

- `GET /health`
- `POST /api/review`

## Current provider

This project uses Groq as the free-tier LLM provider so it works well in a lightweight backend and does not require a local GPU or huge RAM footprint.

## Phase 1 status

The backend includes:
- Python syntax validation
- structured JSON review contract
- FastAPI review endpoint
- Groq integration with graceful fallback when no key is configured
- static validation and DB persistence hooks
