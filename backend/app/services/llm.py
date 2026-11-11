import json
import logging

from groq import Groq

from app.config import settings
from app.schemas import LLMReviewResponse

logger = logging.getLogger(__name__)

REVIEW_SYSTEM_INSTRUCTION = """
You are an expert Python code reviewer. Your job is to analyze Python code snippets for:
1. Real bugs and runtime edge cases.
2. Security vulnerabilities (OWASP top 10, injection, insecure deserialization, credential leakage).
3. PEP 8 and readability issues.
4. Suggested unit tests for critical edge cases.

Be precise with line numbers. Do not hallucinate issues that do not exist.
Output ONLY structured JSON conforming strictly to the requested schema.
"""


class LLMService:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model_name = "llama-3.3-70b-versatile"

    def review_code(self, code: str) -> LLMReviewResponse:
        if not self.client:
            logger.warning("GROQ_API_KEY is not configured; returning empty review.")
            return LLMReviewResponse(findings=[])

        prompt = f"Review this Python code snippet:\n\n```python\n{code}\n```"

        for attempt in range(2):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": REVIEW_SYSTEM_INSTRUCTION},
                        {"role": "user", "content": prompt},
                    ],
                    model=self.model_name,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                raw_content = chat_completion.choices[0].message.content
                if not raw_content:
                    raise ValueError("Groq returned empty content.")

                data = json.loads(raw_content)
                return LLMReviewResponse(**data)
            except Exception as exc:
                logger.warning("Attempt %d failed to generate valid review: %s", attempt + 1, exc)
                if attempt == 0:
                    prompt += f"\n\nPrevious attempt failed with validation error: {str(exc)}. Fix format and return valid JSON only."
                else:
                    logger.error("All attempts to produce structured LLM review failed.")
                    return LLMReviewResponse(findings=[])


llm_service = LLMService()
