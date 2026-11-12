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
from app.services.language_check import detect_mismatch


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Code Review Assistant",
    version="1.0.0",
    description="Automated code review using LLM intelligence and static analysis validation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Allow your specific Render frontend URL and local Vite server
    allow_origins=[
        "http://localhost:5173",
        "https://ai-code-reviewer-1-9a9s.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/review", response_model=CodeReviewResponse)
def create_code_review(request: CodeReviewRequest):
    lang = (getattr(request, "language", "python") or "python").strip().lower()

    # 0. Reject obvious language mismatches before doing any work
    mismatch = detect_mismatch(request.code, lang)
    if mismatch:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=mismatch,
        )

    try:
        # 1. AST syntax check (the analyzer skips non-Python languages)
        static_result = StaticAnalyzerService.parse_ast(request.code, language=lang)
        if not static_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Python syntax: {static_result['error']}",
            )

        # 2. LLM analysis
        llm_result = llm_service.review_code(request.code, lang)

        # 3. Static linters (Ruff)
        static_findings = []
        ruff_result = StaticAnalyzerService.run_ruff(request.code, language=lang)
        if ruff_result.get("success") and ruff_result.get("stdout"):
            for raw_line in ruff_result["stdout"].splitlines():
                if not raw_line.strip():
                    continue
                parts = raw_line.split(":")
                if len(parts) >= 4:
                    try:
                        line_no = int(parts[1].strip())
                    except ValueError:
                        continue
                    static_findings.append({
                        "line": line_no,
                        "category": "style",
                        "severity": "low",
                        "message": parts[-1].strip(),
                        "suggestion": "Review and fix the reported lint issue.",
                    })

        # 4. Merge findings without dropping LLM detections
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
        summary=llm_result.summary or f"Found {len(findings)} potential issue(s).",
    )

    # 5. Persist to SQLite
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
    except Exception as db_err:
        print(f"[DB Warning] Could not persist review: {db_err}")
    finally:
        db.close()

    return response