# AI Code Review Assistant

Paste Python or JavaScript code and get an AI-powered security and quality review. Every finding comes with a line number, a severity, and a suggested fix.

### [**Live demo: ai-code-reviewer-1-9a9s.onrender.com**](https://ai-code-reviewer-1-9a9s.onrender.com/)

> Note: The app runs on a free hosting tier. If it has been idle, the first review can take up to a minute while the server wakes up.

## Why I built this

Code review is slow, and security mistakes like SQL injection and `eval` are easy to miss. I wanted an LLM-based first-pass reviewer that acts like a security auditor, and I wanted to make its output reliable, not just call an API.

## How it helps

- Quick sanity check before a pull request
- Helps students see *why* a pattern is risky
- Structured results: line, severity, category, description, suggestion

## How it works

1. **React UI:** paste code and pick Python or JavaScript
2. **FastAPI:** checks for a language mismatch and, for Python, validates syntax
3. **Groq LLM:** reviews the code with numbered lines and returns strict JSON
4. **Pydantic:** validates the output
5. **Ruff:** adds lint findings for Python
6. **Result:** findings are merged, saved to SQLite and shown in the UI

## Try it

Select **JavaScript** and paste:

```javascript
function run(input) {
  return eval(input);
}
```

Expected: a critical `eval` finding on line 2.

## Tech stack

React (Vite) · FastAPI · Groq API · Ruff · SQLite · pytest · GitHub Actions · Render

## Run locally

```bash
git clone https://github.com/bhumika4906-creator/ai-code-reviewer.git

# Backend
cd ai-code-reviewer/backend
pip install -r requirements.txt
# copy .env.example to .env and add GROQ_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd ai-code-reviewer/frontend
npm install
npm run dev
```

Set `API_BASE_URL` in `frontend/src/api.js` to `http://127.0.0.1:8000` for local use.

## Limitations

- AI findings can be wrong, so verify before acting
- JavaScript gets AI review only (no linter yet)
- Review history resets on redeploy (free-tier SQLite)
