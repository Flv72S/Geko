#!/usr/bin/env python3
"""
Script per creare il database Geko usando l'utente postgres
Connettiti al database PostgreSQL e crea il database geko_db se non esiste
"""

import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("[ERROR] psycopg2-binary non installato. Esegui: pip install psycopg2-binary")
    sys.exit(1)

def create_database():
    """Crea il database geko_db se non esiste"""
    print("=" * 60)
    print("[*] Setup Database PostgreSQL - Geko")
    print("=" * 60)
    
    # Parametri di connessione (default per PostgreSQL locale)
    print("\n[*] Connessione a PostgreSQL come utente 'postgres'...")
    print("    [INFO] Assicurati che PostgreSQL sia in esecuzione")
    print("    [INFO] User: postgres")
    print("    [INFO] Password: (ti verrà chiesta se necessaria)")
    
    # Chiedi password se necessario (opzionale)
    password = input("\nPassword per utente postgres (lascia vuoto se non serve): ").strip()
    if not password:
        # Prova senza password
        password = None
    
    try:
        # Connetti al database 'postgres' di default (non geko_db)
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'database': 'postgres'  # Database di default per creare altri DB
        }
        
        if password:
            conn_params['password'] = password
        
        print("\n[*] Tentativo connessione...")
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("    [OK] Connesso a PostgreSQL")
        
        # Verifica se il database esiste già
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = 'geko_db'
        """)
        exists = cursor.fetchone()
        
        if exists:
            print("\n[*] Database 'geko_db' esiste già")
            response = input("    Vuoi ricrearlo? (s/N): ").strip().lower()
            if response == 's':
                # Termina connessioni attive
                cursor.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'geko_db'
                      AND pid <> pg_backend_pid();
                """)
                cursor.execute('DROP DATABASE IF EXISTS geko_db')
                print("    [OK] Database eliminato")
                cursor.execute('CREATE DATABASE geko_db')
                print("    [OK] Database 'geko_db' creato")
            else:
                print("    [INFO] Database esistente, non modificato")
        else:
            # Crea il database
            cursor.execute('CREATE DATABASE geko_db')
            print("\n[OK] Database 'geko_db' creato con successo!")
        
        # Chiudi connessione
        cursor.close()
        conn.close()
        
        # Test connessione al nuovo database
        print("\n[*] Test connessione al database 'geko_db'...")
        test_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'database': 'geko_db'
        }
        if password:
            test_params['password'] = password
        
        test_conn = psycopg2.connect(**test_params)
        test_cursor = test_conn.cursor()
        test_cursor.execute('SELECT version();')
        version = test_cursor.fetchone()[0]
        test_cursor.close()
        test_conn.close()
        
        print(f"    [OK] Connessione al database 'geko_db' riuscita!")
        print(f"    PostgreSQL version: {version[:60]}...")
        
        # Genera DATABASE_URL suggerito
        print("\n" + "=" * 60)
        print("[*] Configurazione suggerita per .env")
        print("=" * 60)
        
        db_url = "postgresql+psycopg2://postgres"
        if password:
            db_url += f":{password}"
        db_url += "@localhost:5432/geko_db"
        
        print("\nDATABASE_URL per FastAPI:")
        print(f"DATABASE_URL={db_url}")
        print("\n[INFO] Aggiungi questa riga al file .env nella root del progetto")
        
        print("\n[*] Setup completato!")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "FATALE" in error_msg:
            print(f"\n[ERROR] Errore di autenticazione: {error_msg}")
            print("\n[INFO] Possibili soluzioni:")
            print("    1. Verifica la password per l'utente 'postgres'")
            print("    2. Se non hai impostato password, potrebbe essere richiesta")
            print("    3. Verifica che PostgreSQL sia in esecuzione")
            print("    4. Controlla pg_hba.conf se necessario")
        else:
            print(f"\n[ERROR] Errore connessione: {error_msg}")
            print("\n[INFO] Verifica che:")
            print("    - PostgreSQL sia installato e in esecuzione")
            print("    - La porta 5432 sia disponibile")
            print("    - L'utente 'postgres' esista e abbia i permessi")
        return False
    except Exception as e:
        print(f"\n[ERROR] Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Esegui setup database"""
    try:
        success = create_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Setup interrotto dall'utente")
        sys.exit(1)

if __name__ == "__main__":
    main()

