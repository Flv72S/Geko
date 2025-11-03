import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse

# Carica .env dalla root del progetto
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

db_url = os.getenv("DATABASE_URL")

print(f"[*] Testing database connection to: {db_url.split('@')[1] if '@' in db_url else 'configurato'}")

try:
    # Converte URL SQLAlchemy in DSN per psycopg2
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://')
    
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:] if parsed.path.startswith('/') else parsed.path,
        user=parsed.username,
        password=parsed.password
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"[OK] Connection OK - PostgreSQL version: {version[0][:60]}...")
    
    # Verifica tabelle
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"[OK] Tabelle trovate ({len(tables)}): {', '.join(tables)}")
    
    cur.close()
    conn.close()
    print("[OK] Test connessione database completato con successo!")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
