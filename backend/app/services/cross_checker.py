from app.schemas import Finding


class CrossCheckerService:
    @staticmethod
    def merge_findings(llm_findings, static_findings):
        merged = []
        seen = set()

        for finding in llm_findings:
            key = (finding.line, finding.category, finding.description)
            seen.add(key)
            merged.append(
                Finding(
                    line=finding.line,
                    category=finding.category,
                    severity=finding.severity,
                    description=finding.description,
                    suggested_fix=finding.suggested_fix,
                    source="ai",
                    is_verified=False,
                    verification_detail="Pending static analysis cross-check",
                )
            )

        for finding in static_findings:
            key = (finding["line"], finding["category"], finding["description"])
            if key in seen:
                continue
            merged.append(
                Finding(
                    line=finding["line"],
                    category=finding["category"],
                    severity=finding["severity"],
                    description=finding["description"],
                    suggested_fix=finding["suggested_fix"],
                    source="static_analyzer",
                    is_verified=True,
                    verification_detail="Confirmed by static analyzer",
                )
            )

        return merged
