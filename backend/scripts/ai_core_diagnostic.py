#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEKO - Fase 1.4 Diagnostica Completa AI Core
Verifica integrità, dipendenze, configurazione e funzionalità del modulo AI Core
"""

import sys
import os
import json
import subprocess
import time
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configura encoding UTF-8 per Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Aggiungi backend al path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Risultati diagnostica
diagnostic_results = {
    "ai_core_diagnostics_phase_1_4": {
        "timestamp": datetime.now().isoformat(),
        "environment": {},
        "file_structure": {},
        "model_loading": {},
        "api_inference": {},
        "pipeline": {},
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

def log_warning(key: str, message: str):
    """Registra un avviso"""
    print(f"[WARN] {key}: {message}")

def check_python_version():
    """Verifica versione Python"""
    version = sys.version_info
    return {
        "version": f"{version.major}.{version.minor}.{version.micro}",
        "major": version.major,
        "minor": version.minor,
        "meets_requirement": version.major >= 3 and version.minor >= 10
    }

def check_ai_dependencies():
    """Microstep 1: Validazione Ambiente AI"""
    log_section("MICROSTEP 1: Validazione Ambiente AI")
    
    results = {}
    
    # Verifica Python
    py_info = check_python_version()
    results["python"] = py_info
    if py_info["meets_requirement"]:
        log_result("Python", f"{py_info['version']} (>= 3.10 OK)")
    else:
        log_error("Python", f"{py_info['version']} - Richiesto >= 3.10")
    
    # Dipendenze AI critiche
    ai_dependencies = {
        "torch": "PyTorch",
        "transformers": "Hugging Face Transformers",
        "scikit-learn": "scikit-learn",
        "numpy": "NumPy",
        "pandas": "pandas",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
    }
    
    installed = []
    missing = []
    versions = {}
    
    for module, name in ai_dependencies.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            versions[module] = version
            installed.append(module)
            log_result(f"{name}", f"v{version}")
        except ImportError:
            missing.append(module)
            log_error(f"{name}", "non installato")
    
    results["installed"] = installed
    results["missing"] = missing
    results["versions"] = versions
    
    # Verifica CUDA (opzionale)
    try:
        import torch
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            results["cuda"] = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "device_name": torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
            }
            log_result("CUDA", f"Disponibile ({torch.cuda.device_count()} device)")
        else:
            results["cuda"] = {"available": False}
            log_warning("CUDA", "Non disponibile (CPU mode)")
    except ImportError:
        results["cuda"] = {"available": False, "note": "PyTorch non installato"}
    
    # Genera ai_env_check.json
    env_check_path = backend_root / "ai_core" / "ai_env_check.json"
    if not env_check_path.parent.exists():
        env_check_path = backend_root / "ai_env_check.json"
    
    env_check = {
        "python_version": py_info["version"],
        "python_meets_requirement": py_info["meets_requirement"],
        "libraries": {
            lib: {
                "installed": lib in installed,
                "version": versions.get(lib, None)
            }
            for lib in ai_dependencies.keys()
        },
        "missing_packages": missing,
        "cuda": results.get("cuda", {})
    }
    
    try:
        env_check_path.parent.mkdir(exist_ok=True)
        with open(env_check_path, 'w', encoding='utf-8') as f:
            json.dump(env_check, f, indent=2, ensure_ascii=False)
        log_result("ai_env_check.json", f"generato in {env_check_path}")
    except Exception as e:
        log_warning("ai_env_check.json", f"non generato: {e}")
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["environment"] = results
    
    if missing:
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            f"Installare dipendenze mancanti: pip install {' '.join(missing)}"
        )
    
    return len(missing) == 0

def check_file_structure():
    """Microstep 2: Validazione File e Struttura"""
    log_section("MICROSTEP 2: Validazione File e Struttura")
    
    results = {}
    
    ai_core_path = backend_root / "app" / "ai_core"
    results["ai_core_path"] = str(ai_core_path)
    results["exists"] = ai_core_path.exists()
    
    if not ai_core_path.exists():
        log_warning("ai_core/", "Directory non trovata")
        results["status"] = "NOT_FOUND"
        results["expected_files"] = [
            "__init__.py",
            "core_ai.py",
            "model_loader.py",
            "pipeline_manager.py",
            "ai_routes.py",
        ]
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            "Creare struttura ai_core/ con i file necessari secondo l'architettura definita"
        )
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["file_structure"] = results
        return False
    
    log_result("ai_core/", "directory trovata")
    
    # File attesi
    expected_files = {
        "__init__.py": "File inizializzazione modulo",
        "core_ai.py": "Modulo principale AI Core",
        "main_ai.py": "Alternativa a core_ai.py",
        "model_loader.py": "Caricatore modelli",
        "pipeline_manager.py": "Gestore pipeline",
        "ai_routes.py": "Route API AI",
    }
    
    found_files = {}
    missing_files = []
    
    for file_name, description in expected_files.items():
        file_path = ai_core_path / file_name
        if file_path.exists():
            found_files[file_name] = {
                "exists": True,
                "path": str(file_path),
                "size": file_path.stat().st_size
            }
            log_result(f"{file_name}", f"trovato ({description})")
        else:
            missing_files.append(file_name)
            log_warning(f"{file_name}", f"non trovato ({description})")
    
    results["found_files"] = found_files
    results["missing_files"] = missing_files
    
    # Verifica __init__.py
    if "__init__.py" in found_files:
        try:
            init_path = ai_core_path / "__init__.py"
            with open(init_path, 'r', encoding='utf-8') as f:
                init_content = f.read()
            
            # Verifica import
            imports_ok = True
            import_errors = []
            
            # Prova import
            try:
                sys.path.insert(0, str(ai_core_path.parent))
                import importlib
                spec = importlib.util.spec_from_file_location("ai_core", init_path)
                if spec and spec.loader:
                    # Non carichiamo per evitare errori, solo verifichiamo sintassi
                    compile(init_content, str(init_path), 'exec')
                    results["__init__syntax"] = "OK"
                    log_result("__init__.py", "sintassi valida")
            except SyntaxError as e:
                results["__init__syntax"] = "ERROR"
                results["__init__error"] = str(e)
                log_error("__init__.py", f"errore sintassi: {e}")
            
        except Exception as e:
            log_error("__init__.py", f"errore lettura: {e}")
    
    results["status"] = "PARTIAL" if missing_files else "COMPLETE"
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["file_structure"] = results
    
    if missing_files:
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            f"Creare file mancanti: {', '.join(missing_files)}"
        )
    
    return len(missing_files) == 0

def check_model_loading():
    """Microstep 3: Test Caricamento Modelli"""
    log_section("MICROSTEP 3: Test Caricamento Modelli")
    
    results = {}
    
    ai_core_path = backend_root / "app" / "ai_core"
    models_path = backend_root / "models" or ai_core_path / "models"
    
    results["models_directory"] = str(models_path)
    results["models_directory_exists"] = models_path.exists()
    
    if not models_path.exists():
        log_warning("models/", "Directory modelli non trovata")
        results["models_found"] = []
        results["status"] = "NO_MODELS_DIRECTORY"
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            "Creare directory models/ per i modelli AI"
        )
    else:
        log_result("models/", "directory trovata")
        
        # Cerca file modello
        model_extensions = ['.pt', '.pth', '.bin', '.onnx', '.h5', '.pkl']
        models_found = []
        
        for ext in model_extensions:
            for model_file in models_path.rglob(f"*{ext}"):
                size_mb = model_file.stat().st_size / (1024 * 1024)
                models_found.append({
                    "name": model_file.name,
                    "path": str(model_file.relative_to(backend_root)),
                    "size_mb": round(size_mb, 2),
                    "extension": ext
                })
        
        results["models_found"] = models_found
        
        if models_found:
            log_result("Modelli trovati", f"{len(models_found)}")
            for model in models_found[:5]:  # Mostra primi 5
                print(f"    - {model['name']} ({model['size_mb']} MB)")
        else:
            log_warning("Modelli", "Nessun modello trovato")
            results["status"] = "NO_MODELS"
            diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
                "Aggiungere modelli AI nella directory models/"
            )
    
    # Test caricamento (se possibile)
    results["loading_test"] = "NOT_IMPLEMENTED"
    results["note"] = "Test caricamento richiede implementazione model_loader.py"
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["model_loading"] = results
    return True

def check_api_inference():
    """Microstep 4: Test API di Inferenza"""
    log_section("MICROSTEP 4: Test API di Inferenza")
    
    results = {}
    
    # Verifica se ai_routes esiste
    ai_core_path = backend_root / "app" / "ai_core"
    ai_routes_path = ai_core_path / "ai_routes.py"
    
    if not ai_routes_path.exists():
        log_warning("ai_routes.py", "Non trovato - API AI non implementate")
        results["status"] = "NOT_IMPLEMENTED"
        results["endpoints"] = []
        results["note"] = "Endpoint API AI richiedono implementazione ai_routes.py"
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            "Implementare ai_routes.py con endpoint /ai/predict, /ai/analyze, /ai/test"
        )
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["api_inference"] = results
        return False
    
    # Se esiste, verifica endpoint nel main.py
    try:
        main_path = backend_root / "app" / "main.py"
        with open(main_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        if "ai_routes" in main_content or "ai_core" in main_content:
            results["registered"] = True
            log_result("API AI", "registrate in main.py")
        else:
            results["registered"] = False
            log_warning("API AI", "non registrate in main.py")
    except Exception as e:
        log_error("Verifica registrazione", str(e))
    
    # Test endpoint (richiede server in esecuzione)
    results["endpoint_tests"] = "REQUIRES_SERVER"
    results["note"] = "Test endpoint richiedono server FastAPI in esecuzione"
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["api_inference"] = results
    return True

def check_pipeline():
    """Microstep 5: Diagnostica Pipeline Interna"""
    log_section("MICROSTEP 5: Diagnostica Pipeline Interna")
    
    results = {}
    
    ai_core_path = backend_root / "app" / "ai_core"
    pipeline_path = ai_core_path / "pipeline_manager.py"
    
    if not pipeline_path.exists():
        log_warning("pipeline_manager.py", "Non trovato")
        results["status"] = "NOT_IMPLEMENTED"
        results["modules"] = {
            "preprocessing": "NOT_FOUND",
            "inference": "NOT_FOUND",
            "postprocessing": "NOT_FOUND"
        }
        diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"].append(
            "Implementare pipeline_manager.py con moduli pre-processing, inference, post-processing"
        )
    else:
        log_result("pipeline_manager.py", "trovato")
        results["status"] = "FOUND"
        # Verifica contenuto
        try:
            with open(pipeline_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modules = {
                "preprocessing": "preprocessing" in content.lower() or "pre_process" in content.lower(),
                "inference": "inference" in content.lower() or "predict" in content.lower(),
                "postprocessing": "postprocessing" in content.lower() or "post_process" in content.lower()
            }
            
            results["modules"] = modules
            
            for module, found in modules.items():
                if found:
                    log_result(f"Modulo {module}", "presente")
                else:
                    log_warning(f"Modulo {module}", "non rilevato")
        except Exception as e:
            log_error("Lettura pipeline", str(e))
    
    results["end_to_end_test"] = "NOT_IMPLEMENTED"
    results["note"] = "Test end-to-end richiede implementazione completa pipeline"
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["pipeline"] = results
    return True

def check_performance():
    """Microstep 6: Monitoraggio Performance e Memoria"""
    log_section("MICROSTEP 6: Monitoraggio Performance e Memoria")
    
    results = {}
    
    # Info sistema
    results["system"] = {
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
    }
    
    log_result("CPU cores", results["system"]["cpu_count"])
    log_result("RAM totale", f"{results['system']['memory_total_gb']} GB")
    log_result("RAM disponibile", f"{results['system']['memory_available_gb']} GB")
    
    # Benchmark (simulato - richiede implementazione)
    results["benchmark"] = {
        "status": "NOT_IMPLEMENTED",
        "note": "Benchmark richiede modelli e pipeline implementati"
    }
    
    results["recommendations"] = [
        "Eseguire benchmark dopo implementazione modelli",
        "Monitorare utilizzo GPU se disponibile",
        "Ottimizzare batch size per performance"
    ]
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["performance"] = results
    return True

def generate_final_report():
    """Microstep 7: Generazione Report Finale"""
    log_section("MICROSTEP 7: Generazione Report Finale")
    
    # Calcola status complessivo
    env_ok = len(diagnostic_results["ai_core_diagnostics_phase_1_4"]["environment"].get("missing", [])) == 0
    structure_ok = diagnostic_results["ai_core_diagnostics_phase_1_4"]["file_structure"].get("status") == "COMPLETE"
    
    if env_ok and structure_ok:
        status = "OK"
    elif env_ok:
        status = "PARTIAL"
    else:
        status = "NOT_READY"
    
    diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["status"] = status
    
    # Salva report JSON
    report_path = backend_root / "ai_core" / "diagnostic_phase_1_4.json"
    if not report_path.parent.exists():
        report_path = backend_root / "diagnostic_phase_1_4.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(diagnostic_results, f, indent=2, ensure_ascii=False)
    
    log_result("Report generato", str(report_path))
    
    # Stampa riepilogo
    print("\n" + "=" * 60)
    print("[*] RIEPILOGO DIAGNOSTICA AI CORE")
    print("=" * 60)
    print(f"Status: {status}")
    print(f"\nAmbiente: {'[OK]' if env_ok else '[ERROR]'}")
    print(f"Struttura: {'[OK]' if structure_ok else '[PARTIAL]'}")
    
    if diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"]:
        print("\n[*] Raccomandazioni:")
        for rec in diagnostic_results["ai_core_diagnostics_phase_1_4"]["summary"]["recommendations"]:
            print(f"   - {rec}")
    
    print("\n" + "=" * 60)
    
    return report_path

def main():
    """Esegui tutti i microstep diagnostici"""
    print("=" * 60)
    print("[*] DIAGNOSTICA COMPLETA AI CORE GEKO - FASE 1.4")
    print("=" * 60)
    print(f"Data/ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend root: {backend_root}")
    
    # Esegui tutti i microstep
    check_ai_dependencies()
    check_file_structure()
    check_model_loading()
    check_api_inference()
    check_pipeline()
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

