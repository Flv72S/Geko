"""Diagnostica finale Fase 1 per progetto Geko.

Esegue controlli su ambiente, struttura repository, configurazioni,
Docker e genera report JSON/Markdown con esiti dettagliati.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
LOG_DIR = BACKEND_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "diagnostic_phase_1.log"

DIAGNOSTIC_DIR = BACKEND_DIR / "diagnostics"
DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)
STATUS_JSON = DIAGNOSTIC_DIR / "phase_1_status.json"
REPORT_MD = DIAGNOSTIC_DIR / "phase_1_report.md"

REQUIRED_DIRECTORIES = [
    BACKEND_DIR,
    ROOT_DIR / "frontend",
    ROOT_DIR / "docs",
    ROOT_DIR / "data",
    ROOT_DIR / "deploy",
]

CONFIG_FILES = {
    ".env.example": {
        "required_keys": ["DB_HOST", "DB_USER", "PORT", "REDIS_URL"],
    },
    "docker-compose.yml": {
        "required_services": ["backend", "db", "redis"],
    },
    "backend/requirements.txt": {
        "minimum_lines": 1,
    },
    "frontend/package.json": {
        "required_fields": {"name": "geko-frontend"},
    },
}

REQUIRED_COMMANDS = {
    "python": ["python", "--version"],
    "node": ["node", "-v"],
    "docker": ["docker", "--version"],
    "git": ["git", "--version"],
    "redis": ["redis-cli", "ping"],
    "postgres": ["psql", "--version"],
}

CONTAINER_NAMES = ["geko_backend", "geko_db", "geko_redis"]


@dataclass
class DiagnosticResult:
    label: str
    status: str
    details: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "status": self.status,
            "details": self.details,
            "errors": self.errors,
        }


def log(message: str) -> None:
    timestamp = datetime.now().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")
    print(message)


def run_command(command: List[str], timeout: int = 30, check: bool = False) -> subprocess.CompletedProcess:
    log(f"Esecuzione comando: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )
        log(f"Output STDOUT: {result.stdout.strip()}")
        if result.stderr:
            log(f"Output STDERR: {result.stderr.strip()}")
        return result
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        log(f"Errore comando {' '.join(command)}: {exc}")
        raise


def check_environment() -> DiagnosticResult:
    details: Dict[str, str] = {}
    errors: List[str] = []
    status = "OK"
    for key, cmd in REQUIRED_COMMANDS.items():
        try:
            completed = run_command(cmd)
            output = completed.stdout.strip() or completed.stderr.strip()
            if key == "redis":
                details[key] = "OK" if "PONG" in output else "KO"
                if "PONG" not in output:
                    status = "ISSUES"
                    errors.append(f"redis-cli non ha risposto con PONG (output: {output})")
            else:
                if completed.returncode == 0:
                    details[key] = "OK"
                else:
                    details[key] = "KO"
                    status = "ISSUES"
                    errors.append(f"Comando {' '.join(cmd)} ha restituito codice {completed.returncode}")
        except Exception as exc:
            details[key] = "MISSING"
            status = "NOT_READY"
            errors.append(f"Comando {' '.join(cmd)} non disponibile: {exc}")
    return DiagnosticResult("environment", status, details, errors)


def check_repository_structure() -> DiagnosticResult:
    missing: List[str] = []
    for directory in REQUIRED_DIRECTORIES:
        if not directory.exists():
            missing.append(str(directory))
    root_readme = ROOT_DIR / "README.md"
    git_dir = ROOT_DIR / ".git"
    gitignore = ROOT_DIR / ".gitignore"
    license_file = ROOT_DIR / "LICENSE"
    details = {
        "readme": "OK" if root_readme.exists() else "MISSING",
        "git_initialized": "OK" if git_dir.exists() else "MISSING",
        "gitignore": "OK" if gitignore.exists() else "MISSING",
        "license": "OK" if license_file.exists() else "MISSING",
        "directories": "OK" if not missing else "MISSING",
    }
    errors = [f"Directory mancante: {path}" for path in missing]
    status = "OK" if not errors else "NOT_READY"
    if details["gitignore"] == "MISSING" or details["license"] == "MISSING":
        status = "ISSUES" if status == "OK" else status
    return DiagnosticResult("repository_structure", status, details, errors)


def check_configuration_files() -> DiagnosticResult:
    errors: List[str] = []
    details: Dict[str, str] = {}
    status = "OK"
    for relative_path, rules in CONFIG_FILES.items():
        file_path = ROOT_DIR / relative_path
        if not file_path.exists():
            details[relative_path] = "MISSING"
            errors.append(f"File mancante: {relative_path}")
            status = "NOT_READY"
            continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        details[relative_path] = "OK"
        if "required_keys" in rules:
            missing_keys = [key for key in rules["required_keys"] if key not in content]
            if missing_keys:
                details[relative_path] = "ISSUES"
                status = "ISSUES" if status != "NOT_READY" else status
                errors.append(f"Chiavi mancanti in {relative_path}: {', '.join(missing_keys)}")
        if "required_services" in rules:
            for service in rules["required_services"]:
                if service not in content:
                    details[relative_path] = "ISSUES"
                    status = "ISSUES" if status != "NOT_READY" else status
                    errors.append(f"Servizio '{service}' non definito in {relative_path}")
        if "minimum_lines" in rules and len(content.strip().splitlines()) < rules["minimum_lines"]:
            details[relative_path] = "ISSUES"
            status = "ISSUES" if status != "NOT_READY" else status
            errors.append(f"File {relative_path} sembra vuoto")
        if "required_fields" in rules:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as exc:
                details[relative_path] = "ISSUES"
                status = "NOT_READY"
                errors.append(f"package.json non valido: {exc}")
            else:
                for field, expected in rules["required_fields"].items():
                    if data.get(field) != expected:
                        details[relative_path] = "ISSUES"
                        status = "ISSUES" if status != "NOT_READY" else status
                        errors.append(f"Campo {field} in {relative_path} diverso da {expected}")
    return DiagnosticResult("configuration", status, details, errors)


def ensure_docker_compose_up() -> DiagnosticResult:
    details: Dict[str, str] = {}
    errors: List[str] = []
    status = "OK"
    try:
        run_command(["docker", "compose", "up", "-d"])
        ps = run_command(["docker", "ps", "--format", "{{.Names}}"])
        lines = [line.strip() for line in ps.stdout.splitlines() if line.strip()]
        running_containers: List[str] = lines
        details["running_containers"] = ", ".join(running_containers)
        missing = [name for name in CONTAINER_NAMES if name not in running_containers]
        if missing:
            status = "ISSUES"
            errors.append(f"Container non in esecuzione: {', '.join(missing)}")
        else:
            status = "OK"
        for container in CONTAINER_NAMES:
            if container not in running_containers:
                continue
            try:
                logs = run_command(["docker", "logs", container])
            except Exception as log_exc:
                status = "ISSUES"
                errors.append(f"Impossibile leggere i log di {container}: {log_exc}")
                continue
            if "error" in logs.stdout.lower() or "error" in logs.stderr.lower():
                status = "ISSUES" if status == "OK" else status
                errors.append(f"Log del container {container} contengono 'error'")
    except Exception as exc:
        status = "NOT_READY"
        errors.append(str(exc))
    return DiagnosticResult("docker", status, details, errors)


def aggregate_status(results: List[DiagnosticResult]) -> str:
    if any(r.status == "NOT_READY" for r in results):
        return "NOT_READY"
    if any(r.status == "ISSUES" for r in results):
        return "PARTIAL"
    return "READY"


def generate_json_report(results: List[DiagnosticResult], overall_status: str) -> None:
    data = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "steps": {result.label: result.to_dict() for result in results},
    }
    STATUS_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_markdown_report(results: List[DiagnosticResult], overall_status: str) -> None:
    lines = [
        "# 🧪 Report Diagnostico Fase 1 — GEKO",
        "",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Risultato finale:** {'✅ READY' if overall_status == 'READY' else ('⚠️ PARTIAL' if overall_status == 'PARTIAL' else '❌ NOT_READY')} — Sistema {'pronto per la Fase 2' if overall_status == 'READY' else 'con problemi da risolvere'}",
        "",
    ]
    for result in results:
        lines.append(f"## {result.label.title()}")
        lines.append(f"- Stato: {result.status}")
        if result.details:
            lines.append("- Dettagli:")
            for key, value in result.details.items():
                lines.append(f"  - {key}: {value}")
        if result.errors:
            lines.append("- Problemi:")
            for error in result.errors:
                lines.append(f"  - {error}")
        lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def maybe_commit_results() -> None:
    try:
        run_command(["git", "add", str(DIAGNOSTIC_DIR)])
        run_command(["git", "commit", "-m", "test(phase1): diagnosi completata, sistema pronto per Fase 2"])
    except Exception as exc:
        log(f"Commit automatico non eseguito: {exc}")


def main(auto_commit: bool = False) -> int:
    LOG_FILE.write_text("", encoding="utf-8")
    log("Avvio diagnostica finale Fase 1")
    results = [
        check_environment(),
        check_repository_structure(),
        check_configuration_files(),
        ensure_docker_compose_up(),
    ]
    overall_status = aggregate_status(results)
    generate_json_report(results, overall_status)
    generate_markdown_report(results, overall_status)
    log(f"Diagnostica completata con stato: {overall_status}")
    if auto_commit and overall_status == "READY":
        maybe_commit_results()
    return 0 if overall_status == "READY" else 1


if __name__ == "__main__":
    auto_commit_flag = "--auto-commit" in sys.argv
    sys.exit(main(auto_commit=auto_commit_flag))
