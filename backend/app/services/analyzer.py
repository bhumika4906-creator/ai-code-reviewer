import ast
import json
import subprocess
import sys
from pathlib import Path


class StaticAnalyzerService:
    @staticmethod
    def run_ruff(code: str, language: str = "python"):
        if language.lower() != "python":
            return {"success": True, "stdout": "", "stderr": ""}
            
        temp_path = Path("temp_review.py")
        temp_path.write_text(code, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", str(temp_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            return {
                "success": result.returncode in {0, 1},
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    @staticmethod
    def run_bandit(code: str, language: str = "python"):
        if language.lower() != "python":
            return {"success": True, "payload": {}, "stderr": ""}
            
        temp_path = Path("temp_review.py")
        temp_path.write_text(code, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", str(temp_path), "-f", "json"],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout or "{}") if result.stdout.strip() else {}
            return {
                "success": result.returncode in {0, 1},
                "payload": payload,
                "stderr": result.stderr,
            }
        except json.JSONDecodeError:
            return {"success": False, "payload": {}, "stderr": result.stderr if 'result' in locals() else ""}
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    @staticmethod
    def parse_ast(code: str, language: str = "python"):
        if language.lower() != "python":
            return {"success": True, "tree": None}
            
        try:
            tree = ast.parse(code)
            return {"success": True, "tree": tree}
        except SyntaxError as exc:
            return {"success": False, "error": str(exc)}