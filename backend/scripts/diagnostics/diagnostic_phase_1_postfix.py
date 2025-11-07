import subprocess
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
LOG_FILE = BACKEND_DIR / "logs" / "diagnostic_phase_1_postfix.log"
STATUS_FILE = BACKEND_DIR / "diagnostics" / "phase_1_status.json"
REPORT_FILE = BACKEND_DIR / "diagnostics" / "phase_1_report.md"
REQUIRED_DIRS = ["backend", "frontend", "docs", "deploy", "data"]
REQUIRED_FILES = {
    "README.md": "# Geko Project\n\nDocumentazione iniziale del progetto Geko.\n",
    "LICENSE": "MIT License\n\nCopyright (c) "
    + str(datetime.now().year)
    + " Geko Project Contributors\n\nPermission is hereby granted...\n",
}
ENV_EXAMPLE_CONTENT = """# Environment example for Geko
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=geko_db
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/geko_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change_me
BACKEND_PORT=8000
FRONTEND_PORT=5173
"""
BACKEND_REQUIREMENTS_FALLBACK = """fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
pydantic[dotenv]
requests
"""
FRONTEND_PACKAGE_PLACEHOLDER = """{
  "name": "geko-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
"""


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)


def ensure_repository_structure() -> None:
    for relative_dir in REQUIRED_DIRS:
        dir_path = ROOT_DIR / relative_dir
        dir_path.mkdir(parents=True, exist_ok=True)
    for filename, content in REQUIRED_FILES.items():
        file_path = ROOT_DIR / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
    env_example = ROOT_DIR / ".env.example"
    if not env_example.exists():
        env_example.write_text(ENV_EXAMPLE_CONTENT, encoding="utf-8")
    backend_requirements = BACKEND_DIR / "requirements.txt"
    if not backend_requirements.exists():
        backend_requirements.write_text(BACKEND_REQUIREMENTS_FALLBACK, encoding="utf-8")
    frontend_package = ROOT_DIR / "frontend" / "package.json"
    if not frontend_package.exists():
        frontend_package.write_text(FRONTEND_PACKAGE_PLACEHOLDER, encoding="utf-8")


def check_command(cmd: str) -> bool:
    try:
        subprocess.run([cmd, "--version"], check=True, capture_output=True)
        log(f"[OK] {cmd} disponibile")
        return True
    except Exception as e:
        log(f"[ERR] {cmd} non trovato o non accessibile: {e}")
        return False


def ensure_docker_up(timeout: int = 120) -> bool:
    try:
        result = subprocess.run(["docker", "info"], capture_output=True)
        if result.returncode != 0:
            log("[WARN] Docker non risponde, avvio manuale richiesto.")
            return False
        log("[OK] Docker attivo.")
        log("Avvio dei container con docker compose up -d ...")
        proc = subprocess.run(["docker", "compose", "up", "-d"], timeout=timeout)
        if proc.returncode == 0:
            time.sleep(5)
            running = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            log(f"Container attivi:\n{running.stdout}")
            return True
        else:
            log("[ERR] docker compose non completato correttamente.")
            return False
    except subprocess.TimeoutExpired:
        log(f"[ERR] docker compose ha superato il timeout di {timeout}s.")
        return False
    except FileNotFoundError as exc:
        log(f"[ERR] docker non disponibile: {exc}")
        return False


def rerun_phase1_diagnostic() -> str:
    log("Riesecuzione diagnostica finale (phase_1_final.py)...")
    result = subprocess.run(
        [sys.executable, str(BACKEND_DIR / "scripts" / "diagnostics" / "diagnostic_phase_1_final.py")],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR
    )
    log(result.stdout)
    if result.stderr:
        log(result.stderr)
    if STATUS_FILE.exists():
        with STATUS_FILE.open("r", encoding="utf-8") as f:
            status = json.load(f)
        return status.get("overall_status", status.get("result", "NOT_READY"))
    return "NOT_READY"


def commit_if_ready():
    log("🔄 Controllo stato diagnostica...")
    if STATUS_FILE.exists():
        with STATUS_FILE.open("r", encoding="utf-8") as f:
            status = json.load(f)
        current_state = status.get(
            "overall_status",
            status.get("diagnostic_result", status.get("result"))
        )
        if current_state == "READY":
            log("Tutti i test superati, esecuzione commit finale.")
            subprocess.run(["git", "add", "-A"], cwd=ROOT_DIR)
            subprocess.run(["git", "commit", "-m", "diagnostic: phase 1 complete"], cwd=ROOT_DIR)
            subprocess.run(["git", "push"], cwd=ROOT_DIR)
        else:
            log("Stato non READY, commit non eseguito.")
    else:
        log("File di stato non trovato.")


def main():
    LOG_FILE.write_text("", encoding="utf-8") if LOG_FILE.exists() else None
    log("Avvio script diagnostico post-fix Fase 1 Geko")
    ensure_repository_structure()

    checks = {
        "redis-cli": check_command("redis-cli"),
        "psql": check_command("psql")
    }

    docker_ok = ensure_docker_up(timeout=120)
    status = rerun_phase1_diagnostic()

    summary = {
        "timestamp": datetime.now().isoformat(),
        "redis": checks["redis-cli"],
        "postgresql": checks["psql"],
        "docker_ok": docker_ok,
        "diagnostic_result": status
    }

    with STATUS_FILE.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    if status == "READY":
        commit_if_ready()

    log(f"Risultato complessivo: {status}")


if __name__ == "__main__":
    main()
