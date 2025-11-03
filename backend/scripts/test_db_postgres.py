#!/usr/bin/env python3
"""
Script per testare la connessione al database usando l'utente postgres
Questo script può essere eseguito dopo aver creato il database in PgAdmin
"""

import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text

def test_connection():
    """Testa connessione con utente postgres"""
    print("=" * 60)
    print("[*] Test Connessione Database con utente postgres")
    print("=" * 60)
    
    # DATABASE_URL con postgres (modifica secondo le tue credenziali)
    # Se non hai password: postgresql+psycopg2://postgres@localhost:5432/geko_db
    # Se hai password: postgresql+psycopg2://postgres:password@localhost:5432/geko_db
    
    print("\n[*] Configurazione DATABASE_URL per test:")
    print("    Modifica questo script se necessario")
    print("    User: postgres")
    print("    Database: geko_db")
    print("    Host: localhost")
    print("    Port: 5432")
    
    # Prova senza password prima
    db_urls_to_try = [
        "postgresql+psycopg2://postgres@localhost:5432/geko_db",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/geko_db",
    ]
    
    # Leggi da .env se possibile
    env_file = backend_root.parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if 'DATABASE_URL' in line and not line.strip().startswith('#') and 'postgres' in line:
                        db_url_env = line.split('=', 1)[1].strip()
                        if '@localhost:' in db_url_env or '@127.0.0.1:' in db_url_env:
                            db_urls_to_try.insert(0, db_url_env)
        except:
            pass
    
    success = False
    
    for db_url in db_urls_to_try:
        print(f"\n[*] Tentativo con: {db_url.split('@')[1] if '@' in db_url else 'configurato'}")
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                # Test query
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
                
                if tables:
                    print(f"    Tabelle trovate ({len(tables)}): {', '.join(tables)}")
                    
                    # Verifica tabelle attese
                    expected = ['users', 'aziende', 'leads', 'logs']
                    found = [t for t in expected if t in tables]
                    missing = [t for t in expected if t not in tables]
                    
                    if found:
                        print(f"    [OK] Tabelle principali trovate: {', '.join(found)}")
                    if missing:
                        print(f"    [WARN] Tabelle mancanti: {', '.join(missing)}")
                        print(f"    [INFO] Esegui init.sql in PgAdmin per crearle")
                else:
                    print(f"    [WARN] Nessuna tabella trovata")
                    print(f"    [INFO] Il database è vuoto - esegui init.sql in PgAdmin")
                
                success = True
                print(f"\n[OK] Database configurato correttamente!")
                print(f"\n[*] Aggiungi al file .env:")
                print(f"DATABASE_URL={db_url}")
                break
                
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                print(f"    [ERROR] Database 'geko_db' non esiste")
                print(f"    [INFO] Crea il database in PgAdmin prima")
            elif "authentication" in error_msg.lower() or "FATALE" in error_msg:
                print(f"    [ERROR] Autenticazione fallita")
                print(f"    [INFO] Verifica password per utente 'postgres'")
            else:
                print(f"    [ERROR] {error_msg[:100]}")
    
    if not success:
        print("\n[ERROR] Nessuna connessione riuscita")
        print("\n[*] Istruzioni:")
        print("    1. Crea il database 'geko_db' in PgAdmin")
        print("    2. Verifica credenziali utente 'postgres'")
        print("    3. Consulta: backend/scripts/ISTRUZIONI_SETUP_DB.md")
        return False
    
    return True

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

