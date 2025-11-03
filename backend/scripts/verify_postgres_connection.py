#!/usr/bin/env python3
"""
Script per verificare la connessione PostgreSQL e testare credenziali
"""

import sys

try:
    import psycopg2
except ImportError:
    print("[ERROR] psycopg2-binary non installato")
    sys.exit(1)

def test_connection(host, port, user, password, database='postgres'):
    """Testa una connessione specifica"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, version
    except psycopg2.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    """Testa diverse configurazioni"""
    print("=" * 60)
    print("[*] Verifica Connessione PostgreSQL")
    print("=" * 60)
    
    # Credenziali da testare
    credentials = [
        {"host": "localhost", "port": 5432, "user": "postgres", "password": "N0nn0c4rl0!!", "desc": "localhost con password"},
        {"host": "127.0.0.1", "port": 5432, "user": "postgres", "password": "N0nn0c4rl0!!", "desc": "127.0.0.1 con password"},
        {"host": "localhost", "port": 5432, "user": "postgres", "password": "", "desc": "localhost senza password"},
        {"host": "127.0.0.1", "port": 5432, "user": "postgres", "password": "", "desc": "127.0.0.1 senza password"},
    ]
    
    # Prova anche con password comune
    common_passwords = ["postgres", "admin", ""]
    
    print("\n[*] Test credenziali fornite...")
    for cred in credentials[:2]:  # Testa solo quelle con password
        print(f"\n[*] Test: {cred['desc']}")
        print(f"    Host: {cred['host']}:{cred['port']}")
        print(f"    User: {cred['user']}")
        print(f"    Password: {'***' if cred['password'] else '(vuota)'}")
        
        success, result = test_connection(
            cred['host'], cred['port'], cred['user'], cred['password']
        )
        
        if success:
            print(f"    [OK] Connessione riuscita!")
            print(f"    PostgreSQL: {result[:60]}...")
            
            # Prova a creare il database
            try:
                conn = psycopg2.connect(
                    host=cred['host'],
                    port=cred['port'],
                    user=cred['user'],
                    password=cred['password'],
                    database='postgres'
                )
                conn.set_isolation_level(1)  # AUTOCOMMIT
                cursor = conn.cursor()
                
                # Verifica se esiste
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'geko_db'")
                exists = cursor.fetchone()
                
                if exists:
                    print(f"    [INFO] Database 'geko_db' esiste già")
                else:
                    cursor.execute('CREATE DATABASE geko_db')
                    print(f"    [OK] Database 'geko_db' creato!")
                
                cursor.close()
                conn.close()
                
                print(f"\n[OK] Credenziali corrette trovate!")
                print(f"\n[*] DATABASE_URL per .env:")
                db_url = f"postgresql+psycopg2://{cred['user']}:{cred['password']}@{cred['host']}:{cred['port']}/geko_db"
                print(f"DATABASE_URL={db_url}")
                return
                
            except Exception as e:
                print(f"    [ERROR] Errore creazione database: {e}")
        else:
            error_msg = result[:100]
            if "authentication" in error_msg.lower() or "FATALE" in error_msg.lower():
                print(f"    [ERROR] Autenticazione fallita")
            else:
                print(f"    [ERROR] {error_msg}")
    
    # Se arriviamo qui, le credenziali fornite non funzionano
    print("\n" + "=" * 60)
    print("[ERROR] Nessuna connessione riuscita con le credenziali fornite")
    print("=" * 60)
    print("\n[*] Possibili cause:")
    print("    1. Password non corretta per l'utente 'postgres'")
    print("    2. Server PostgreSQL diverso/configurazione diversa")
    print("    3. Caratteri speciali nella password che causano problemi")
    print("\n[*] Verifica in PgAdmin:")
    print("    1. Apri PgAdmin")
    print("    2. Prova a connetterti manualmente con:")
    print("       Host: localhost")
    print("       Port: 5432")
    print("       User: postgres")
    print("       Password: N0nn0c4rl0!!")
    print("\n[*] Se la connessione manuale funziona, verifica:")
    print("    - Che non ci siano caratteri invisibili nella password")
    print("    - Che il file pg_hba.conf permetta connessioni locali")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrotto")
        sys.exit(1)

