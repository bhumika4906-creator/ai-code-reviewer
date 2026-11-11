import ast
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class FindingCategory(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    STYLE = "style"
    TEST_SUGGESTION = "test-suggestion"


class FindingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=4000, description="Python source code to review")

    @field_validator("code")
    @classmethod
    def validate_python_syntax(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Code snippet cannot be empty or whitespace only.")
        try:
            ast.parse(trimmed)
        except SyntaxError as exc:
            raise ValueError(f"Invalid Python syntax: {exc.msg} (line {exc.lineno})") from exc
        return trimmed


class FindingRaw(BaseModel):
    line: int = Field(..., ge=1, description="1-indexed line number")
    category: FindingCategory
    severity: FindingSeverity
    description: str = Field(..., min_length=5)
    suggested_fix: str = Field(..., min_length=1)


class LLMReviewResponse(BaseModel):
    findings: List[FindingRaw] = Field(default_factory=list)


class Finding(FindingRaw):
    source: str = Field(default="ai", description="'ai' or 'static_analyzer'")
    is_verified: bool = Field(default=False)
    verification_detail: Optional[str] = None


class CodeReviewResponse(BaseModel):
    id: Optional[int] = None
    original_code: str
    findings: List[Finding]
    summary: str
