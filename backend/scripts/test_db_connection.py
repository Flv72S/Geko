#!/usr/bin/env python3
"""
Script per testare la connessione al database PostgreSQL
Prova sia con localhost che con 'db' hostname
"""

import sys
from pathlib import Path

# Aggiungi backend al path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text

def test_connection(db_url: str, description: str):
    """Testa una connessione database"""
    print(f"\n[*] Test connessione: {description}")
    print(f"    URL: {db_url.split('@')[1] if '@' in db_url else 'configurato'}")
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"    [OK] Connessione riuscita!")
            print(f"    PostgreSQL version: {version[:50]}...")
            
            # Test query tabella
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5
            """))
            tables = [row[0] for row in result]
            if tables:
                print(f"    Tabelle trovate: {len(tables)} ({', '.join(tables[:3])}...)")
            else:
                print(f"    Tabelle: nessuna trovata (database vuoto)")
            
            return True
    except Exception as e:
        error_msg = str(e)
        print(f"    [ERROR] {error_msg[:150]}")
        # Mostra dettagli completi per errori di autenticazione
        if "FATALE" in error_msg or "autenticazione" in error_msg.lower() or "authentication" in error_msg.lower():
            print(f"    [INFO] Possibile problema di autenticazione - verifica username/password")
        return False

def main():
    """Esegui test connessioni"""
    print("=" * 60)
    print("[*] Test Connessione Database PostgreSQL")
    print("=" * 60)
    
    # Leggi DATABASE_URL dal .env se possibile
    env_file = backend_root.parent / ".env"
    db_url_original = None
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        db_url_original = line.split('=', 1)[1].strip()
                        break
        except Exception as e:
            print(f"[WARN] Errore lettura .env: {e}")
    
    # Test 1: Con DATABASE_URL da config (usa 'db')
    print("\n[*] Test 1: DATABASE_URL da configurazione")
    try:
        from app.core.config import settings
        test_connection(settings.DATABASE_URL, "Configurazione app (da .env)")
    except Exception as e:
        print(f"[ERROR] Impossibile caricare configurazione: {e}")
    
    # Test 2: Con localhost se DATABASE_URL usa 'db'
    if db_url_original and '@db:' in db_url_original:
        db_url_localhost = db_url_original.replace('@db:', '@localhost:')
        test_connection(db_url_localhost, "Localhost (modificato da 'db')")
    
    print("\n" + "=" * 60)
    print("[*] Test completati")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrotti")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

