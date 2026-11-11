from typing import List, Optional
from pydantic import BaseModel, Field


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to review")
    language: str = Field(default="python", description="Programming language")


class Finding(BaseModel):
    line: Optional[int] = Field(default=None, description="Line number of the issue")
    severity: str = Field(default="medium", description="critical | high | medium | low | info")
    category: str = Field(default="general", description="security | performance | style | bug")
    message: str = Field(..., description="Description of the finding")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix or remediation")


class LLMReviewResult(BaseModel):
    summary: str = ""
    findings: List[Finding] = []


class CodeReviewResponse(BaseModel):
    id: Optional[int] = None
    original_code: str
    findings: List[Finding] = []
    summary: str