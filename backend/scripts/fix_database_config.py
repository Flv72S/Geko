#!/usr/bin/env python3
"""
Script per aiutare a configurare correttamente la connessione database
Verifica le opzioni disponibili e suggerisce la configurazione corretta
"""

import sys
from pathlib import Path
import subprocess
import socket

backend_root = Path(__file__).parent.parent
project_root = backend_root.parent

def check_port_open(host: str, port: int):
    """Verifica se una porta è aperta"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def check_docker_running():
    """Verifica se Docker è in esecuzione"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def main():
    """Analizza situazione database e fornisce suggerimenti"""
    print("=" * 60)
    print("[*] Analisi Configurazione Database")
    print("=" * 60)
    
    # 1. Verifica Docker
    print("\n[1] Verifica Docker:")
    docker_running = check_docker_running()
    if docker_running:
        print("    [OK] Docker è in esecuzione")
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=geko_db", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                print(f"    [OK] Container geko_db trovato: {result.stdout.strip()}")
            else:
                print("    [INFO] Container geko_db non trovato - avviare con: docker-compose up -d")
        except:
            print("    [WARN] Impossibile verificare container Docker")
    else:
        print("    [ERROR] Docker non è in esecuzione")
        print("    [INFO] Avviare Docker Desktop prima di continuare")
    
    # 2. Verifica porta 5432
    print("\n[2] Verifica porta 5432:")
    port_open_localhost = check_port_open("localhost", 5432)
    if port_open_localhost:
        print("    [OK] Porta 5432 aperta su localhost")
        print("    [INFO] C'è un database PostgreSQL in ascolto")
    else:
        print("    [WARN] Porta 5432 non aperta su localhost")
        print("    [INFO] Il database potrebbe non essere avviato")
    
    # 3. Leggi configurazione attuale
    print("\n[3] Configurazione attuale:")
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'DATABASE_URL' in line and not line.strip().startswith('#'):
                        # Nascondi password
                        safe_line = line.strip()
                        if '@' in safe_line and ':' in safe_line:
                            parts = safe_line.split('@')
                            if len(parts) == 2:
                                user_pass = parts[0].split('//')[-1]
                                if ':' in user_pass:
                                    user = user_pass.split(':')[0]
                                    safe_line = safe_line.replace(user_pass.split(':')[1], '***')
                        print(f"    {safe_line}")
                        break
        except Exception as e:
            print(f"    [ERROR] Errore lettura .env: {e}")
    else:
        print("    [ERROR] File .env non trovato")
    
    # 4. Suggerimenti
    print("\n[4] Suggerimenti:")
    
    if not docker_running:
        print("    - Avviare Docker Desktop")
        print("    - Poi eseguire: docker-compose up -d")
    elif not port_open_localhost:
        print("    - Il container database potrebbe non essere avviato")
        print("    - Eseguire: docker-compose up -d")
    else:
        print("    - Database raggiungibile su localhost:5432")
        print("    - Verificare credenziali nel DATABASE_URL:")
        print("      * Username: geko_user")
        print("      * Password: geko_pass (da docker-compose.yml)")
        print("      * Database: geko_db")
        print("    - Se le credenziali sono diverse, aggiornare .env")
    
    # 5. Test connessione suggerita
    print("\n[5] Test connessione suggerita:")
    if port_open_localhost:
        test_url = "postgresql+psycopg2://geko_user:geko_pass@localhost:5432/geko_db"
        print(f"    URL: postgresql+psycopg2://geko_user:***@localhost:5432/geko_db")
        print(f"    Esegui: python scripts/test_db_connection.py")
        print(f"    Oppure testa direttamente con:")
        print(f"      psql -h localhost -U geko_user -d geko_db")
    else:
        print("    Prima avviare il database")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Analisi interrotta")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

