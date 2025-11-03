#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Diagnostic Script - Fase 1.2
Esegue diagnostica completa del backend FastAPI
"""

import sys
import os
import json
import subprocess
import time
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configura encoding UTF-8 per Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Aggiungi il percorso del backend al PYTHONPATH
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Importa moduli del backend
try:
    from app.core.config import settings
    from app.db.session import SessionLocal, engine
    from app.main import app
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Errore importazione moduli: {e}")
    sys.exit(1)

# Risultati diagnostica
diagnostic_results = {
    "backend_diagnostics_phase_1_2": {
        "timestamp": datetime.now().isoformat(),
        "environment": {},
        "server": {},
        "database": {},
        "api_routes": {},
        "middlewares": {},
        "performance": {},
        "summary": {
            "status": "UNKNOWN",
            "recommendations": []
        }
    }
}

def log_section(title: str):
    """Stampa un header di sezione"""
    print("\n" + "=" * 60)
    print(f"[*] {title}")
    print("=" * 60)

def log_result(key: str, value: Any, status: str = "[OK]"):
    """Registra un risultato"""
    print(f"{status} {key}: {value}")

def log_error(key: str, error: str):
    """Registra un errore"""
    print(f"[ERROR] {key}: {error}")

def check_python_environment():
    """Microstep 1: Validazione ambiente Python"""
    log_section("MICROSTEP 1: Validazione Ambiente Backend")
    
    results = {}
    
    # Versione Python
    python_version = sys.version
    results["python_version"] = python_version.split()[0]
    log_result("Python", results["python_version"])
    
    # Verifica pip
    try:
        pip_version = subprocess.run(
            ["pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        results["pip_version"] = pip_version
        log_result("pip", pip_version)
    except Exception as e:
        log_error("pip", str(e))
        results["pip_error"] = str(e)
    
    # Verifica requirements.txt
    requirements_path = backend_root / "requirements.txt"
    if requirements_path.exists():
        results["requirements_file"] = "presente"
        log_result("requirements.txt", "trovato")
        
        # Leggi dipendenze principali
        with open(requirements_path, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        results["dependencies_count"] = len(deps)
        results["main_dependencies"] = deps[:10]  # Prime 10
        
        # Verifica installazione dipendenze critiche
        critical_deps = ["fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary", "pydantic"]
        installed = []
        missing = []
        
        for dep in critical_deps:
            try:
                __import__(dep.replace("-", "_"))
                installed.append(dep)
            except ImportError:
                missing.append(dep)
        
        results["critical_deps_installed"] = installed
        results["critical_deps_missing"] = missing
        
        if missing:
            log_error("Dipendenze critiche mancanti", ", ".join(missing))
        else:
            log_result("Dipendenze critiche", "tutte installate")
    else:
        log_error("requirements.txt", "file non trovato")
        results["requirements_file"] = "mancante"
    
    # Verifica .env
    env_path = backend_root.parent / ".env"
    if env_path.exists():
        results["env_file"] = "presente"
        log_result(".env", "trovato")
        
        # Leggi variabili (solo nomi, non valori)
        env_vars = []
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        var_name = line.split('=')[0].strip()
                        if var_name:
                            env_vars.append(var_name)
            results["env_variables_found"] = env_vars
            log_result("Variabili ambiente", f"{len(env_vars)} trovate")
        except Exception as e:
            log_error("Lettura .env", str(e))
    else:
        log_error(".env", "file non trovato")
        results["env_file"] = "mancante"
        diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
            "Creare file .env con DATABASE_URL e altre variabili necessarie"
        )
    
    # Verifica struttura directory
    required_dirs = ["app", "app/core", "app/db", "app/db/models"]
    existing_dirs = []
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = backend_root / dir_path
        if full_path.exists():
            existing_dirs.append(dir_path)
        else:
            missing_dirs.append(dir_path)
    
    results["structure_existing_dirs"] = existing_dirs
    results["structure_missing_dirs"] = missing_dirs
    
    if missing_dirs:
        log_error("Directory mancanti", ", ".join(missing_dirs))
    else:
        log_result("Struttura directory", "completa")
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["environment"] = results
    return len(missing) == 0 and len(results.get("critical_deps_missing", [])) == 0

def check_port_availability(port: int = 8000):
    """Verifica se una porta è disponibile"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True se libera

def check_server_startup():
    """Microstep 2: Test avvio server"""
    log_section("MICROSTEP 2: Test Avvio Server Backend")
    
    results = {}
    
    # Verifica porta
    port = 8000
    port_free = check_port_availability(port)
    results["port"] = port
    results["port_free"] = port_free
    
    if port_free:
        log_result("Porta 8000", "libera")
    else:
        log_error("Porta 8000", "già in uso")
        results["port_warning"] = "Porta occupata da altro processo"
    
    # Verifica file main.py
    main_path = backend_root / "app" / "main.py"
    if main_path.exists():
        results["main_file"] = "presente"
        log_result("app/main.py", "trovato")
    else:
        log_error("app/main.py", "non trovato")
        results["main_file"] = "mancante"
    
    # Test import app
    try:
        from app.main import app
        results["app_import"] = "successo"
        log_result("Import app", "OK")
        
        # Verifica configurazione FastAPI
        if hasattr(app, 'title'):
            results["fastapi_title"] = app.title
            results["fastapi_version"] = app.version
            log_result("FastAPI app", f"{app.title} v{app.version}")
        
        # Verifica middleware CORS
        if hasattr(app, 'middleware_stack'):
            results["middleware_configured"] = True
            log_result("Middleware", "configurato")
    except Exception as e:
        log_error("Import app", str(e))
        results["app_import"] = "errore"
        results["app_import_error"] = str(e)
    
    # Test sintassi (import senza eseguire)
    try:
        compile(open(main_path).read(), main_path, 'exec')
        results["syntax_check"] = "OK"
        log_result("Controllo sintassi", "OK")
    except SyntaxError as e:
        log_error("Sintassi", str(e))
        results["syntax_check"] = "errore"
        results["syntax_error"] = str(e)
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["server"] = results
    return results.get("app_import") == "successo" and results.get("syntax_check") == "OK"

def check_database_connection():
    """Microstep 3: Diagnostica database"""
    log_section("MICROSTEP 3: Diagnostica Connessione Database")
    
    results = {}
    
    # Verifica configurazione DATABASE_URL
    try:
        db_url = settings.DATABASE_URL
        results["database_url_configured"] = True
        # Nascondi password nell'output
        db_url_safe = db_url.split('@')[1] if '@' in db_url else "configurato"
        log_result("DATABASE_URL", f"configurato ({db_url_safe})")
    except Exception as e:
        log_error("DATABASE_URL", f"non configurato: {e}")
        results["database_url_configured"] = False
        results["database_url_error"] = str(e)
        diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
            f"Configurare DATABASE_URL nel file .env: {e}"
        )
        return False
    
    # Test connessione
    try:
        db = SessionLocal()
        # Query di test
        result = db.execute(text("SELECT 1"))
        db.close()
        
        results["connection_status"] = "successo"
        log_result("Connessione DB", "riuscita")
    except Exception as e:
        error_msg = str(e)
        log_error("Connessione DB", error_msg)
        results["connection_status"] = "errore"
        results["connection_error"] = error_msg
        
        # Suggerimento specifico per errore hostname "db"
        if "db" in error_msg.lower() and "host" in error_msg.lower():
            diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
                "DATABASE_URL usa 'db' come hostname (funziona solo in Docker). Per test locali, usare 'localhost'"
            )
        else:
            diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
                f"Verificare connessione database: {error_msg[:100]}"
            )
        
        # Prova con localhost se il DATABASE_URL usa "db"
        if "db" in db_url.lower() and "@db:" in db_url:
            try:
                # Crea URL alternativo con localhost
                local_url = db_url.replace("@db:", "@localhost:")
                from sqlalchemy import create_engine
                test_engine = create_engine(local_url)
                test_conn = test_engine.connect()
                test_conn.execute(text("SELECT 1"))
                test_conn.close()
                
                results["connection_status"] = "successo_con_localhost"
                results["localhost_connection"] = "riuscita"
                log_result("Connessione DB (localhost)", "riuscita con localhost")
            except Exception as e2:
                results["localhost_connection_error"] = str(e2)
        
        return False
    
    # Verifica tabelle
    try:
        db = SessionLocal()
        # Lista tabelle
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables_result = db.execute(tables_query)
        tables = [row[0] for row in tables_result]
        db.close()
        
        results["tables_found"] = tables
        results["tables_count"] = len(tables)
        
        # Verifica tabelle principali
        expected_tables = ["users", "aziende", "leads", "logs"]
        found_expected = [t for t in expected_tables if t in tables]
        missing_expected = [t for t in expected_tables if t not in tables]
        
        results["expected_tables_found"] = found_expected
        results["expected_tables_missing"] = missing_expected
        
        if found_expected:
            log_result("Tabelle trovate", f"{len(tables)} ({', '.join(found_expected[:3])}...)")
        if missing_expected:
            log_error("Tabelle mancanti", ", ".join(missing_expected))
            diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
                f"Eseguire migrazioni per creare tabelle mancanti: {', '.join(missing_expected)}"
            )
    except Exception as e:
        log_error("Verifica tabelle", str(e))
        results["tables_check_error"] = str(e)
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["database"] = results
    return results.get("connection_status") == "successo"

def check_api_routes():
    """Microstep 4: Diagnostica API routes"""
    log_section("MICROSTEP 4: Diagnostica API e Routing")
    
    results = {}
    routes_tested = []
    
    # Lista route registrate
    try:
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else []
                })
        
        results["routes_registered"] = routes
        results["routes_count"] = len(routes)
        log_result("Route registrate", str(len(routes)))
        
        # Verifica route principali
        expected_routes = ["/", "/health", "/test-db"]
        found_routes = [r["path"] for r in routes]
        missing_routes = [r for r in expected_routes if r not in found_routes]
        
        results["expected_routes_found"] = [r for r in expected_routes if r in found_routes]
        results["expected_routes_missing"] = missing_routes
        
        if missing_routes:
            log_error("Route mancanti", ", ".join(missing_routes))
        
    except Exception as e:
        log_error("Lista route", str(e))
        results["routes_error"] = str(e)
    
    # Nota: Per testare le route effettivamente, servirebbe un server in esecuzione
    # Questo verrà fatto nel Microstep 6 se il server è avviato
    results["note"] = "Test effettivi delle route richiedono server in esecuzione"
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["api_routes"] = results
    return True

def check_middlewares():
    """Microstep 5: Diagnostica middleware"""
    log_section("MICROSTEP 5: Diagnostica Middleware e Logging")
    
    results = {}
    
    # Verifica middleware CORS
    try:
        cors_configured = False
        for middleware in app.user_middleware:
            if 'CORSMiddleware' in str(type(middleware)):
                cors_configured = True
                break
        
        results["cors_configured"] = cors_configured
        if cors_configured:
            log_result("CORS Middleware", "configurato")
        else:
            log_error("CORS Middleware", "non configurato")
    except Exception as e:
        log_error("Verifica CORS", str(e))
    
    # Verifica configurazione CORS da main.py
    try:
        # Leggi main.py per verificare configurazione
        main_file = backend_root / "app" / "main.py"
        with open(main_file, 'r') as f:
            content = f.read()
            if 'CORSMiddleware' in content:
                results["cors_in_code"] = True
                log_result("CORS in codice", "presente")
            else:
                results["cors_in_code"] = False
    except Exception as e:
        pass
    
    # Logging - verifica configurazione base
    results["logging_note"] = "Logging configurabile tramite uvicorn"
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["middlewares"] = results
    return True

def check_performance():
    """Microstep 6: Diagnostica performance (base)"""
    log_section("MICROSTEP 6: Diagnostica Performance")
    
    results = {}
    
    # Nota: Performance test completi richiedono server in esecuzione
    # Qui facciamo solo verifiche base
    
    results["note"] = "Test performance completi richiedono server in esecuzione"
    results["recommended_tests"] = [
        "Test carico con 5 req/sec per 30 sec",
        "Misura tempo medio risposta",
        "Verifica percentile 95°"
    ]
    
    # Verifica configurazione base per performance
    results["async_support"] = True  # FastAPI supporta async di default
    log_result("Supporto async", "attivo")
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["performance"] = results
    return True

def generate_final_report():
    """Microstep 7: Genera report finale"""
    log_section("MICROSTEP 7: Report Diagnostico Finale")
    
    # Calcola status complessivo
    env_ok = len(diagnostic_results["backend_diagnostics_phase_1_2"]["environment"].get("critical_deps_missing", [])) == 0
    server_ok = diagnostic_results["backend_diagnostics_phase_1_2"]["server"].get("app_import") == "successo"
    db_ok = diagnostic_results["backend_diagnostics_phase_1_2"]["database"].get("connection_status") == "successo"
    
    if env_ok and server_ok and db_ok:
        status = "OK"
    elif env_ok and server_ok:
        status = "WARNING"
    else:
        status = "ERROR"
    
    diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["status"] = status
    
    # Aggiungi raccomandazioni se necessario
    if status != "OK":
        if not env_ok:
            diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
                "Installare dipendenze mancanti: pip install -r requirements.txt"
            )
        if not server_ok:
            diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"].append(
                "Correggere errori di importazione o sintassi nel backend"
            )
    
    # Salva report JSON
    report_path = backend_root / "diagnostic_phase_1_2.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(diagnostic_results, f, indent=2, ensure_ascii=False)
    
    log_result("Report generato", str(report_path))
    
    # Stampa riepilogo
    print("\n" + "=" * 60)
    print("[*] RIEPILOGO DIAGNOSTICA")
    print("=" * 60)
    print(f"Status: {status}")
    print(f"\nAmbiente: {'[OK]' if env_ok else '[ERROR]'}")
    print(f"Server: {'[OK]' if server_ok else '[ERROR]'}")
    print(f"Database: {'[OK]' if db_ok else '[ERROR]'}")
    
    if diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"]:
        print("\n[*] Raccomandazioni:")
        for rec in diagnostic_results["backend_diagnostics_phase_1_2"]["summary"]["recommendations"]:
            print(f"   - {rec}")
    
    print("\n" + "=" * 60)
    
    return report_path

def main():
    """Esegui tutti i microstep diagnostici"""
    print("=" * 60)
    print("[*] DIAGNOSTICA COMPLETA BACKEND GEKO - FASE 1.2")
    print("=" * 60)
    print(f"Data/ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend root: {backend_root}")
    
    # Esegui tutti i microstep
    check_python_environment()
    check_server_startup()
    check_database_connection()
    check_api_routes()
    check_middlewares()
    check_performance()
    
    # Genera report finale
    report_path = generate_final_report()
    
    print(f"\n[OK] Diagnostica completata! Report salvato in: {report_path}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Diagnostica interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore durante diagnostica: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

