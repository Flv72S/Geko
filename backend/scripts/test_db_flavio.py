#!/usr/bin/env python3
"""
Test connessione database con credenziali flavio
"""

import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text

def test_connection():
    """Testa connessione con credenziali flavio"""
    print("=" * 60)
    print("[*] Test Connessione Database - Credenziali flavio")
    print("=" * 60)
    
    # DATABASE_URL con credenziali flavio
    db_url = "postgresql+psycopg2://flavio:flavio@localhost:5432/geko_db"
    
    print(f"\n[*] DATABASE_URL: postgresql+psycopg2://flavio:***@localhost:5432/geko_db")
    
    try:
        engine = create_engine(db_url)
        print("[*] Tentativo connessione...")
        
        with engine.connect() as conn:
            # Test query versione
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"    [OK] Connessione riuscita!")
            print(f"    PostgreSQL: {version[:60]}...")
            
            # Verifica tabelle
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"\n[*] Tabelle trovate ({len(tables)}):")
            for table in tables:
                print(f"    - {table}")
            
            # Verifica tabelle attese
            expected = ['users', 'aziende', 'leads', 'logs']
            found = [t for t in expected if t in tables]
            missing = [t for t in expected if t not in tables]
            
            if len(found) == len(expected):
                print(f"\n[OK] Tutte le tabelle principali sono presenti!")
            elif missing:
                print(f"\n[WARN] Tabelle mancanti: {', '.join(missing)}")
            
            # Test query semplice
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.fetchone()[0]
            print(f"\n[*] Test query: users table ha {count} recordi")
            
            print(f"\n[OK] Database configurato e funzionante correttamente!")
            print(f"\n[*] DATABASE_URL per .env:")
            print(f"DATABASE_URL={db_url}")
            
            return True
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] {error_msg[:150]}")
        
        if "does not exist" in error_msg.lower():
            print(f"\n[INFO] Database 'geko_db' non esiste - esegui create_db_with_credentials.py")
        elif "authentication" in error_msg.lower() or "FATALE" in error_msg:
            print(f"\n[INFO] Problema autenticazione - verifica credenziali")
        else:
            print(f"\n[INFO] Errore generico - verifica configurazione")
        
        return False

if __name__ == "__main__":
    try:
        sys.exit(0 if test_connection() else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrotto")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

