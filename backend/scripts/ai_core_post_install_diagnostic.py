#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEKO - AI Core Post-Install Diagnostic
Verifica che il modulo AI Core sia stato installato e configurato correttamente
"""

import sys
import os
import json
import importlib.util
from pathlib import Path

try:
    import requests
except ImportError:
    print("[ERROR] requests non installato. Esegui: pip install requests")
    sys.exit(1)

# Configura encoding UTF-8 per Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

backend_root = Path(__file__).parent.parent

report = {
    "phase": "AI Core post-install diagnostic",
    "timestamp": None,
    "checks": []
}

def check_library(lib_name):
    """Verifica se una libreria è installata"""
    spec = importlib.util.find_spec(lib_name)
    return spec is not None

def check_file_exists(file_path):
    """Verifica se un file esiste"""
    full_path = backend_root / file_path
    return full_path.exists()

def main():
    """Esegui diagnostica post-installazione"""
    from datetime import datetime
    report["timestamp"] = datetime.now().isoformat()
    
    print("=" * 60)
    print("[*] AI Core Post-Install Diagnostic")
    print("=" * 60)
    print(f"Data/ora: {report['timestamp']}\n")
    
    # 1. Check librerie AI
    print("[1] Verifica librerie AI...")
    ai_libraries = {
        "torch": "PyTorch",
        "transformers": "Hugging Face Transformers",
        "sklearn": "scikit-learn"
    }
    
    for lib, name in ai_libraries.items():
        installed = check_library(lib)
        status = "OK" if installed else "Missing"
        report["checks"].append({lib: status})
        
        if installed:
            print(f"    [OK] {name} installato")
        else:
            print(f"    [ERROR] {name} non installato")
    
    # 2. Check struttura file
    print("\n[2] Verifica struttura file...")
    paths_to_check = [
        "app/ai_core/core_ai.py",
        "app/ai_core/model_loader.py",
        "app/ai_core/pipeline_manager.py",
        "app/ai_core/ai_routes.py",
        "app/ai_core/__init__.py",
    ]
    
    all_exist = all(check_file_exists(p) for p in paths_to_check)
    
    for path in paths_to_check:
        exists = check_file_exists(path)
        if exists:
            print(f"    [OK] {path}")
        else:
            print(f"    [ERROR] {path} mancante")
    
    report["checks"].append({
        "file_structure": "OK" if all_exist else "Incomplete"
    })
    
    # 3. Test endpoint /ai/test
    print("\n[3] Test endpoint /ai/test...")
    api_url = "http://127.0.0.1:8000/ai/test"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            report["api_status"] = {
                "status": "OK",
                "response": api_data,
                "status_code": response.status_code
            }
            print(f"    [OK] Endpoint risponde correttamente")
            print(f"    Response: {json.dumps(api_data, indent=2)}")
        else:
            report["api_status"] = {
                "status": "ERROR",
                "status_code": response.status_code,
                "error": f"Status code: {response.status_code}"
            }
            print(f"    [ERROR] Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        report["api_status"] = {
            "status": "ERROR",
            "error": "Server non raggiungibile - avviare con: uvicorn app.main:app --reload"
        }
        print("    [ERROR] Server non raggiungibile")
        print("    [INFO] Avvia il server con: uvicorn app.main:app --reload")
    except Exception as e:
        report["api_status"] = {
            "status": "ERROR",
            "error": str(e)
        }
        print(f"    [ERROR] {e}")
    
    # 4. Salva report
    print("\n[4] Generazione report...")
    diagnostics_dir = backend_root / "diagnostics"
    diagnostics_dir.mkdir(exist_ok=True)
    
    report_path = diagnostics_dir / "ai_core_validation.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"    [OK] Report salvato in: {report_path}")
    
    # 5. Riepilogo
    print("\n" + "=" * 60)
    print("[*] RIEPILOGO")
    print("=" * 60)
    
    libs_ok = all(check["torch"] == "OK" or check.get("transformers") == "OK" or check.get("sklearn") == "OK" 
                  for check in report["checks"] if isinstance(check, dict) and any(k in check for k in ["torch", "transformers", "sklearn"]))
    files_ok = report["checks"][-1].get("file_structure") == "OK"
    api_ok = report.get("api_status", {}).get("status") == "OK"
    
    print(f"Librerie AI: {'[OK]' if libs_ok else '[ERROR]'}")
    print(f"Struttura file: {'[OK]' if files_ok else '[ERROR]'}")
    print(f"API endpoint: {'[OK]' if api_ok else '[ERROR]'}")
    
    if libs_ok and files_ok and api_ok:
        print("\n[OK] Tutti i check sono passati! AI Core è operativo.")
        return 0
    else:
        print("\n[ERROR] Alcuni check non sono passati. Verifica i dettagli sopra.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Diagnostica interrotta")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

