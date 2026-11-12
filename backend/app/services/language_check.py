import re

# Lines that only really appear in Python
PYTHON_PATTERNS = [
    re.compile(r"^\s*def\s+\w+\s*\(.*\)\s*(->\s*[^:]+)?:\s*$"),
    re.compile(r"^\s*class\s+\w+(\(.*\))?\s*:\s*$"),
    re.compile(r"^\s*(if|elif|while)\s+[^{]*:\s*$"),
    re.compile(r"^\s*else\s*:\s*$"),
    re.compile(r"^\s*for\s+\w+(\s*,\s*\w+)*\s+in\s+.+:\s*$"),
    re.compile(r"^\s*(try|finally)\s*:\s*$"),
    re.compile(r"^\s*except\b.*:\s*$"),
    re.compile(r"^\s*from\s+[\w.]+\s+import\s+.+$"),
    re.compile(r"^\s*import\s+[\w.]+(\s+as\s+\w+)?\s*$"),
    re.compile(r"^\s*print\s*\("),
    re.compile(r"^\s*if\s+__name__\s*=="),
]

# Lines that only really appear in JavaScript
JS_PATTERNS = [
    re.compile(r"\b(const|let|var)\s+\w+"),
    re.compile(r"\bfunction\s*\w*\s*\("),
    re.compile(r"=>"),
    re.compile(r"\bconsole\.(log|error|warn|info)\s*\("),
    re.compile(r"^\s*import\s+.+\s+from\s+['\"].+['\"]"),
    re.compile(r"^\s*export\s+(default|const|function|class)\b"),
    re.compile(r"\brequire\s*\(\s*['\"]"),
    re.compile(r"\b(document|window)\."),
    re.compile(r"===|!=="),
    re.compile(r"\)\s*\{\s*$"),
]


def _score(code: str, patterns) -> int:
    """Count how many lines match at least one pattern."""
    return sum(
        1
        for line in code.splitlines()
        if any(p.search(line) for p in patterns)
    )


def detect_mismatch(code: str, selected: str):
    """
    Return a user-facing message if the code clearly looks like the OTHER
    language, otherwise None. Only triggers when the evidence is clear, so
    short or ambiguous snippets are never blocked.
    """
    selected = (selected or "python").strip().lower()
    py_score = _score(code, PYTHON_PATTERNS)
    js_score = _score(code, JS_PATTERNS)

    if selected == "javascript" and py_score >= 2 and js_score == 0:
        return (
            "This looks like Python code, but JavaScript is selected. "
            "Please switch the language dropdown to Python."
        )
    if selected == "python" and js_score >= 2 and py_score == 0:
        return (
            "This looks like JavaScript code, but Python is selected. "
            "Please switch the language dropdown to JavaScript."
        )
    return None