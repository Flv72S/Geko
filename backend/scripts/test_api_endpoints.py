#!/usr/bin/env python3
"""
Test degli endpoint API del backend
"""

import sys
import requests
import time

API_BASE = "http://127.0.0.1:8000"

def test_endpoint(path, expected_status=200):
    """Testa un endpoint"""
    url = f"{API_BASE}{path}"
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = (time.time() - start) * 1000
        
        status = "OK" if response.status_code == expected_status else "ERROR"
        print(f"[{status}] {path:20} → {response.status_code} ({elapsed:.0f}ms)")
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                return True, data
            except:
                return True, response.text[:50]
        else:
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] {path:20} → Server non raggiungibile")
        return False, None
    except Exception as e:
        print(f"[ERROR] {path:20} → {str(e)[:50]}")
        return False, None

def main():
    """Testa tutti gli endpoint principali"""
    print("=" * 60)
    print("[*] Test Endpoint API Backend")
    print("=" * 60)
    print(f"\n[*] Base URL: {API_BASE}")
    print("[*] Assicurati che il server sia avviato: uvicorn app.main:app --reload")
    print()
    
    endpoints = [
        ("/", 200),
        ("/health", 200),
        ("/test-db", 200),
        ("/docs", 200),
        ("/openapi.json", 200),
    ]
    
    results = []
    for path, status in endpoints:
        success, data = test_endpoint(path, status)
        results.append(success)
    
    print("\n" + "=" * 60)
    success_count = sum(results)
    print(f"[*] Risultati: {success_count}/{len(results)} test passati")
    
    if success_count == len(results):
        print("[OK] Tutti gli endpoint funzionano correttamente!")
        return 0
    else:
        print("[ERROR] Alcuni endpoint non rispondono correttamente")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrotti")
        sys.exit(1)

