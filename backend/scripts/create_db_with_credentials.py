#!/usr/bin/env python3
"""
Script per creare il database Geko usando credenziali specifiche
"""

import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("[ERROR] psycopg2-binary non installato. Esegui: pip install psycopg2-binary")
    sys.exit(1)

# Credenziali PostgreSQL
POSTGRES_USER = "flavio"
POSTGRES_PASSWORD = "flavio"
POSTGRES_HOST = "127.0.0.1"  # Usa IPv4 invece di localhost
POSTGRES_PORT = 5432
DB_NAME = "geko_db"

def create_database():
    """Crea il database geko_db se non esiste"""
    print("=" * 60)
    print("[*] Setup Database PostgreSQL - Geko")
    print("=" * 60)
    print(f"\n[*] Credenziali:")
    print(f"    Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
    print(f"    User: {POSTGRES_USER}")
    print(f"    Database: {DB_NAME}")
    
    try:
        # Connetti al database 'postgres' di default per creare altri DB
        print(f"\n[*] Connessione a PostgreSQL...")
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database='postgres'  # Database di default
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("    [OK] Connesso a PostgreSQL")
        
        # Verifica se il database esiste già
        cursor.execute(f"""
            SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'
        """)
        exists = cursor.fetchone()
        
        if exists:
            print(f"\n[*] Database '{DB_NAME}' esiste già")
            print("    [INFO] Eliminazione e ricreazione...")
            
            # Termina connessioni attive al database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_NAME}'
                  AND pid <> pg_backend_pid();
            """)
            
            # Elimina e ricrea
            cursor.execute(f'DROP DATABASE IF EXISTS {DB_NAME}')
            print("    [OK] Database eliminato")
            
        # Crea il database
        cursor.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"    [OK] Database '{DB_NAME}' creato con successo!")
        
        # Chiudi connessione
        cursor.close()
        conn.close()
        
        # Test connessione al nuovo database
        print(f"\n[*] Test connessione al database '{DB_NAME}'...")
        test_conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=DB_NAME
        )
        test_cursor = test_conn.cursor()
        test_cursor.execute('SELECT version();')
        version = test_cursor.fetchone()[0]
        test_cursor.close()
        test_conn.close()
        
        print(f"    [OK] Connessione al database '{DB_NAME}' riuscita!")
        print(f"    PostgreSQL version: {version[:60]}...")
        
        # Genera DATABASE_URL
        db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DB_NAME}"
        
        print("\n" + "=" * 60)
        print("[*] Database creato con successo!")
        print("=" * 60)
        print("\n[*] Configurazione DATABASE_URL per .env:")
        print(f"DATABASE_URL={db_url}")
        print("\n[INFO] Aggiungi questa riga al file .env nella root del progetto")
        
        return True, db_url
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "FATALE" in error_msg:
            print(f"\n[ERROR] Errore di autenticazione: {error_msg}")
            print(f"\n[INFO] Verifica credenziali:")
            print(f"    User: {POSTGRES_USER}")
            print(f"    Password: {POSTGRES_PASSWORD}")
        else:
            print(f"\n[ERROR] Errore connessione: {error_msg}")
        return False, None
    except Exception as e:
        print(f"\n[ERROR] Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def create_tables(db_url):
    """Crea le tabelle usando init.sql"""
    print("\n" + "=" * 60)
    print("[*] Creazione Tabelle")
    print("=" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(db_url)
        
        # Leggi init.sql
        init_sql_path = Path(__file__).parent.parent / "init.sql"
        
        if not init_sql_path.exists():
            print(f"[WARN] File init.sql non trovato in {init_sql_path}")
            print("[INFO] Le tabelle devono essere create manualmente o tramite Alembic")
            return False
        
        print(f"[*] Lettura {init_sql_path.name}...")
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Rimuovi IF NOT EXISTS per CREATE TABLE (PostgreSQL lo supporta)
        # Esegui le query
        print("[*] Esecuzione script SQL...")
        with engine.connect() as conn:
            # Esegui tutto lo script
            conn.execute(text(sql_content))
            conn.commit()
        
        print("[OK] Tabelle create con successo!")
        
        # Verifica tabelle create
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"\n[*] Tabelle create ({len(tables)}):")
            for table in tables:
                print(f"    - {table}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Errore creazione tabelle: {e}")
        import traceback
        traceback.print_exc()
        print("\n[INFO] Puoi creare le tabelle manualmente in PgAdmin usando init.sql")
        return False

def main():
    """Esegui setup completo"""
    try:
        # Crea database
        success, db_url = create_database()
        
        if not success:
            print("\n[ERROR] Impossibile creare il database")
            sys.exit(1)
        
        # Crea tabelle
        if db_url:
            create_tables(db_url)
        
        print("\n" + "=" * 60)
        print("[*] Setup Completato!")
        print("=" * 60)
        print(f"\n[OK] Database '{DB_NAME}' pronto all'uso")
        print(f"\n[*] Prossimi passi:")
        print(f"    1. Aggiungi DATABASE_URL al file .env")
        print(f"    2. Esegui: python scripts/test_db_postgres.py")
        print(f"    3. Avvia server: uvicorn app.main:app --reload")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

