#!/usr/bin/env python3
"""
Script per testare le API routes del backend
Esegue richieste HTTP alle principali route
"""

import requests
import sys
import time
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"

def test_route(method: str, path: str, expected_status: int = 200) -> Dict:
    """Testa una singola route"""
    url = f"{API_BASE_URL}{path}"
    result = {
        "path": path,
        "method": method,
        "status_code": None,
        "response_time_ms": None,
        "success": False,
        "error": None
    }
    
    try:
        start_time = time.time()
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.request(method.upper(), url, timeout=5)
        
        response_time = (time.time() - start_time) * 1000
        
        result["status_code"] = response.status_code
        result["response_time_ms"] = round(response_time, 2)
        result["success"] = response.status_code == expected_status
        
        if response.status_code == expected_status:
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text[:100]
        else:
            result["error"] = f"Expected {expected_status}, got {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        result["error"] = "Server non raggiungibile (verificare che sia in esecuzione)"
        result["success"] = False
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
    
    return result

def main():
    """Esegui test su tutte le route principali"""
    print("=" * 60)
    print("[*] Test API Routes - Backend Geko")
    print("=" * 60)
    print(f"Base URL: {API_BASE_URL}")
    print()
    
    # Route da testare
    routes_to_test = [
        ("GET", "/", 200),
        ("GET", "/health", 200),
        ("GET", "/test-db", 200),
        ("GET", "/docs", 200),
        ("GET", "/openapi.json", 200),
    ]
    
    results = []
    
    for method, path, expected_status in routes_to_test:
        print(f"Testing {method} {path}...", end=" ")
        result = test_route(method, path, expected_status)
        results.append(result)
        
        if result["success"]:
            print(f"[OK] {result['status_code']} ({result['response_time_ms']}ms)")
        else:
            print(f"[ERROR] {result['error']}")
    
    # Statistiche
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    avg_time = sum(r["response_time_ms"] or 0 for r in results) / total if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("[*] Riepilogo Test")
    print("=" * 60)
    print(f"Route testate: {total}")
    print(f"Successi: {successful}")
    print(f"Errori: {total - successful}")
    print(f"Tempo medio risposta: {avg_time:.2f}ms")
    
    if successful == total:
        print("\n[OK] Tutti i test sono passati!")
        return 0
    else:
        print(f"\n[ERROR] {total - successful} test falliti")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrotti dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore durante i test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

