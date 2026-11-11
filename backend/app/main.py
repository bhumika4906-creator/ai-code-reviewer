import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import ReviewResult
from app.schemas import CodeReviewRequest, CodeReviewResponse, Finding
from app.services.analyzer import StaticAnalyzerService
from app.services.cross_checker import CrossCheckerService
from app.services.llm import llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Code Review Assistant",
    version="1.0.0",
    description="Automated Python code review using Groq and static analysis validation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/review", response_model=CodeReviewResponse)
def create_code_review(request: CodeReviewRequest):
    try:
        llm_result = llm_service.review_code(request.code)
        static_result = StaticAnalyzerService.parse_ast(request.code)
        if not static_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Python syntax: {static_result['error']}",
            )

        static_findings = []
        ruff_result = StaticAnalyzerService.run_ruff(request.code)
        if ruff_result["success"]:
            for raw_line in ruff_result["stdout"].splitlines():
                if not raw_line.strip():
                    continue
                parts = raw_line.split(":")
                if len(parts) >= 4:
                    try:
                        line_no = int(parts[1].strip())
                    except ValueError:
                        continue
                    static_findings.append(
                        {
                            "line": line_no,
                            "category": "style",
                            "severity": "low",
                            "description": parts[-1].strip(),
                            "suggested_fix": "Review and fix the reported lint issue.",
                        }
                    )

        findings = CrossCheckerService.merge_findings(llm_result.findings, static_findings)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Review generation failed: {str(exc)}",
        ) from exc

    response = CodeReviewResponse(
        original_code=request.code,
        findings=findings,
        summary=f"Found {len(findings)} potential issue(s).",
    )

    db: Session = SessionLocal()
    try:
        record = ReviewResult(
            original_code=request.code,
            summary=response.summary,
            findings_json=json.dumps([f.model_dump() for f in findings]),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        response.id = record.id
    finally:
        db.close()

    return response
