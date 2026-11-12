import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from app.schemas import Finding, LLMReviewResult

# Force Python to read your .env file directly
load_dotenv()

VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}

LANGUAGE_LABELS = {
    "python": "Python",
    "javascript": "JavaScript",
}


class LLMService:
    # Models that are NOT general chat models (classifiers, audio, embeddings, etc.)
    _EXCLUDE = (
        "guard", "whisper", "tts", "playai", "orpheus",
        "embed", "classif", "moderation", "vision", "safeguard",
    )

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = self._get_active_model()

    def _get_active_model(self) -> str:
        """Pick a chat model: .env pin first, then live discovery, then a default."""
        pinned = os.getenv("GROQ_MODEL")
        if pinned:
            print(f"[LLMService] Using pinned model: {pinned}")
            return pinned

        try:
            models = self.client.models.list().data
            candidates = [
                m.id for m in models
                if getattr(m, "active", True)
                and not any(bad in m.id.lower() for bad in self._EXCLUDE)
            ]
            for preferred in ("gpt-oss-20b", "gpt-oss-120b", "70b", "8b"):
                for m_id in candidates:
                    if preferred in m_id.lower():
                        print(f"[LLMService] Auto-selected model: {m_id}")
                        return m_id
            if candidates:
                print(f"[LLMService] Fallback model: {candidates[0]}")
                return candidates[0]
        except Exception as e:
            print(f"[LLMService] Could not dynamically fetch models: {e}")

        return "llama-3.1-8b-instant"

    def _extract_json(self, raw_text: str) -> dict:
        """Strip code fences / stray prose and parse the first JSON object."""
        text = (raw_text or "").strip()
        if not text:
            raise ValueError("Model returned an empty response")

        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE).strip()

        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start:end + 1]
        return json.loads(text)

    @staticmethod
    def _to_line(value):
        """Coerce the model's 'line' value to an int, or None."""
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    def _call_model(self, system_msg: str, prompt: str) -> str:
        """Call Groq once and return the text content (may be empty)."""
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=4096,  # leave room for reasoning + the JSON answer
        )
        # gpt-oss models are reasoning models: keep the thinking short
        if "gpt-oss" in self.model.lower():
            kwargs["extra_body"] = {"reasoning_effort": "low"}

        completion = self.client.chat.completions.create(**kwargs)
        content = completion.choices[0].message.content
        print(f"[LLMService] Raw model output (first 300 chars): {(content or '')[:300]!r}")
        return content or ""

    def review_code(self, code: str, language: str = "python") -> LLMReviewResult:
        lang_key = (language or "python").strip().lower()
        lang_label = LANGUAGE_LABELS.get(lang_key, language or "Python")

        # Number each line so the model reads line numbers instead of guessing them
        numbered_code = "\n".join(
            f"{i}: {line}" for i, line in enumerate(code.splitlines(), start=1)
        )

        prompt = f"""
You are an expert static code analysis and security auditing system.
The code below is written in {lang_label}. Review it as {lang_label} code, using {lang_label} syntax and conventions.
Do NOT report syntax that is valid {lang_label} as an error.
Look for security vulnerabilities, runtime bugs, and edge cases.
Each line of the code starts with its line number followed by a colon (for example "6: query = ...").
That prefix is NOT part of the code. Use it as the "line" value in your findings.

Code:
---
{numbered_code}
---

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "Short 1-2 sentence overview of the issues found.",
  "findings": [
    {{
      "line": 5,
      "severity": "critical",
      "category": "security",
      "description": "Direct use of eval allows arbitrary code execution.",
      "suggestion": "Avoid eval and parse the input with a safe, explicit parser instead."
    }}
  ]
}}

Rules:
- Report each distinct issue as its own separate finding. Never combine multiple issues into one finding.
- "line" must be the line number where the issue occurs.
- Severity must be one of: critical, high, medium, low.
- Category should be one of: security, bug, performance, style.
- If the code has no real issues, return an empty findings array and say so in the summary.
"""
        system_msg = "You are a professional code review engine that outputs pure JSON."

        try:
            raw_json = None
            last_error = None

            # Try up to 2 times: reasoning models occasionally return empty content
            for attempt in (1, 2):
                try:
                    content = self._call_model(system_msg, prompt)
                    raw_json = self._extract_json(content)
                    break
                except (ValueError, json.JSONDecodeError) as parse_err:
                    last_error = parse_err
                    print(f"[LLMService] Attempt {attempt} failed to parse: {parse_err}")

            if raw_json is None:
                raise last_error or ValueError("Could not parse model output")

            findings_list = []
            for item in raw_json.get("findings", []):
                severity = str(item.get("severity", "medium")).lower()
                if severity not in VALID_SEVERITIES:
                    severity = "medium"

                findings_list.append(
                    Finding(
                        line=self._to_line(item.get("line")),
                        severity=severity,
                        category=item.get("category", "bug"),
                        # LLM returns "description"; your schema field is "message"
                        message=item.get("description") or item.get("message", "Issue detected"),
                        suggestion=item.get("suggestion") or item.get("suggested_fix", ""),
                    )
                )

            return LLMReviewResult(
                summary=raw_json.get(
                    "summary", f"Identified {len(findings_list)} potential issue(s)."
                ),
                findings=findings_list,
            )

        except Exception as e:
            print(f"[LLMService Error] Groq failed using model {self.model}: {e}")
            return LLMReviewResult(
                summary=f"Analysis encountered an API error: {str(e)}",
                findings=[],
            )


llm_service = LLMService()