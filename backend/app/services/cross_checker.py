from typing import List, Union

from app.schemas import Finding

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class CrossCheckerService:
    @staticmethod
    def _to_finding(item: Union[Finding, dict]) -> Finding:
        """Accept either a Finding object (LLM) or a plain dict (Ruff)."""
        if isinstance(item, Finding):
            return item
        return Finding(
            line=item.get("line"),
            severity=item.get("severity", "low"),
            category=item.get("category", "style"),
            message=item.get("message", "Issue detected"),
            suggestion=item.get("suggestion", ""),
        )

    @staticmethod
    def merge_findings(llm_findings: list, static_findings: list) -> List[Finding]:
        """
        Merge LLM and static-analysis findings.
        - Every LLM finding is kept.
        - A static finding is skipped if the LLM already flagged the same line.
        - Result is sorted by severity, then line number.
        """
        merged: List[Finding] = [CrossCheckerService._to_finding(f) for f in llm_findings]
        llm_lines = {f.line for f in merged if f.line is not None}

        for raw in static_findings:
            finding = CrossCheckerService._to_finding(raw)
            if finding.line is not None and finding.line in llm_lines:
                continue
            merged.append(finding)

        merged.sort(
            key=lambda f: (
                SEVERITY_ORDER.get((f.severity or "").lower(), 5),
                f.line if f.line is not None else 10**9,
            )
        )
        return merged