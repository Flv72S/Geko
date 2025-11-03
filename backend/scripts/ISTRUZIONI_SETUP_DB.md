# 🗄️ Istruzioni Setup Database PostgreSQL

## Opzione 1: Creare database in PgAdmin (CONSIGLIATO)

### Passo 1: Apri PgAdmin

1. Avvia PgAdmin 4
2. Connettiti al server PostgreSQL locale (di default su porta 5432)
3. Usa le credenziali dell'utente `postgres`

### Passo 2: Crea il Database

1. Fai clic destro su **Databases** nel pannello sinistro
2. Seleziona **Create** > **Database...**
3. Nella finestra che si apre:
   - **Database name:** `geko_db`
   - Lascia le altre impostazioni di default
4. Fai clic su **Save**

### Passo 3: Crea le Tabelle

1. Seleziona il database `geko_db` nel pannello sinistro
2. Apri **Query Tool** (icona SQL o tasto destro > **Query Tool**)
3. Apri il file `backend/init.sql` oppure incolla questo SQL:

```sql
-- Script SQL per inizializzare il database Geko

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);

CREATE TABLE IF NOT EXISTS aziende (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    settore VARCHAR(100),
    sito_web VARCHAR(255),
    paese VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_aziende_id ON aziende (id);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    evento VARCHAR(100),
    descrizione TEXT,
    livello VARCHAR(20) DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_logs_id ON logs (id);

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    azienda_id INTEGER REFERENCES aziende(id),
    nome_contatto VARCHAR(100),
    ruolo VARCHAR(100),
    email VARCHAR(100),
    telefono VARCHAR(50),
    punteggio FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_leads_id ON leads (id);
```

4. Esegui la query (F5 o pulsante Execute)

### Passo 4: Aggiorna .env

Aggiungi o modifica nel file `.env` nella root del progetto:

```env
DATABASE_URL=postgresql+psycopg2://postgres:TUA_PASSWORD@localhost:5432/geko_db
```

Sostituisci `TUA_PASSWORD` con la password dell'utente `postgres`.

Se non hai impostato password per postgres, usa:
```env
DATABASE_URL=postgresql+psycopg2://postgres@localhost:5432/geko_db
```

### Passo 5: Test Connessione

Esegui:
```bash
cd backend
python scripts/test_db_connection.py
```

---

## Opzione 2: Usare lo script Python (richiede password)

Se preferisci automatizzare, puoi modificare lo script `setup_database_postgres.py` aggiungendo la password direttamente nel codice (ATTENZIONE: solo per sviluppo locale).

---

## Opzione 3: Usare Docker (alternativa)

Se preferisci usare Docker invece di PostgreSQL locale:

```bash
docker-compose up -d db
```

Questo creerà il database con:
- User: `geko_user`
- Password: `geko_pass`
- Database: `geko_db`

E il DATABASE_URL sarà:
```env
DATABASE_URL=postgresql+psycopg2://geko_user:geko_pass@localhost:5432/geko_db
```

---

## Verifica Setup

Dopo aver configurato il database, verifica:

1. **Test connessione:**
   ```bash
   cd backend
   python scripts/test_db_connection.py
   ```

2. **Test dal backend:**
   ```bash
   python scripts/backend_diagnostic.py
   ```

3. **Avvia server e testa endpoint:**
   ```bash
   uvicorn app.main:app --reload
   # In altro terminale:
   curl http://localhost:8000/test-db
   ```

---

## Troubleshooting

### Errore: "authentication failed"
- Verifica password nel DATABASE_URL
- Verifica che l'utente `postgres` esista
- Controlla `pg_hba.conf` se necessario

### Errore: "database does not exist"
- Verifica che il database `geko_db` sia stato creato
- Verifica il nome nel DATABASE_URL

### Errore: "could not translate host name"
- Se usi Docker, assicurati che Docker Desktop sia avviato
- Se usi PostgreSQL locale, usa `localhost` invece di `db`

---

**Ultimo aggiornamento:** 2025-11-03

