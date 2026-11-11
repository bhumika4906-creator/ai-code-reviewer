"""Backward-compatible compatibility shim.

The project now uses Groq for free-tier inference. Older imports that still
reference ``app.services.gemini`` continue to work by delegating to the Groq
service implementation.
"""

from app.services.llm import LLMService, llm_service

GeminiService = LLMService
gemini_service = llm_service
