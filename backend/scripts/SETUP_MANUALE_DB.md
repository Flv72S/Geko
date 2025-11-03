# 🗄️ Setup Manuale Database PostgreSQL

Le credenziali fornite non hanno funzionato automaticamente. Esegui questi passi manualmente in PgAdmin.

## 📋 Credenziali PostgreSQL

- **User:** postgres
- **Password:** N0nn0c4rl0!!
- **Host:** localhost
- **Port:** 5432

## 🔧 Passo 1: Verifica Connessione in PgAdmin

1. Apri **PgAdmin 4**
2. Connettiti al server PostgreSQL:
   - Clic destro su **Servers** → **Create** → **Server...**
   - Oppure se già esiste, clic destro → **Properties**
   - **General tab:**
     - Name: `Local PostgreSQL` (o qualsiasi nome)
   - **Connection tab:**
     - Host: `localhost`
     - Port: `5432`
     - Maintenance database: `postgres`
     - Username: `postgres`
     - Password: `N0nn0c4rl0!!`
   - Salva

3. Verifica che la connessione funzioni

## 🔧 Passo 2: Crea il Database

### Opzione A: Usando PgAdmin UI

1. Nel pannello sinistro, clic destro su **Databases**
2. Seleziona **Create** → **Database...**
3. Nella finestra:
   - **Database:** `geko_db`
   - Lascia le altre opzioni di default
4. Clic su **Save**

### Opzione B: Usando Query Tool

1. Seleziona il database **postgres** nel pannello sinistro
2. Apri **Query Tool** (icona SQL o clic destro → Query Tool)
3. Incolla ed esegui:

```sql
CREATE DATABASE geko_db;
```

## 🔧 Passo 3: Crea le Tabelle

1. Seleziona il database **geko_db** nel pannello sinistro
2. Apri **Query Tool**
3. Apri il file `backend/init.sql` e copia tutto il contenuto
4. Incolla nel Query Tool
5. Esegui (F5 o pulsante Execute)

Oppure esegui direttamente questo SQL:

```sql
-- Users table
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

-- Aziende table
CREATE TABLE IF NOT EXISTS aziende (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    settore VARCHAR(100),
    sito_web VARCHAR(255),
    paese VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_aziende_id ON aziende (id);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    evento VARCHAR(100),
    descrizione TEXT,
    livello VARCHAR(20) DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_logs_id ON logs (id);

-- Leads table
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

## 🔧 Passo 4: Configura .env

Aggiungi o modifica nel file `.env` nella root del progetto:

```env
DATABASE_URL=postgresql+psycopg2://postgres:N0nn0c4rl0!!@localhost:5432/geko_db
```

**Nota:** Se nella password ci sono caratteri speciali che causano problemi, prova a:
1. URL-encodare i caratteri speciali: `!` diventa `%21`
2. Oppure usare virgolette se il tuo sistema lo supporta

Versione URL-encoded:
```env
DATABASE_URL=postgresql+psycopg2://postgres:N0nn0c4rl0%21%21@localhost:5432/geko_db
```

## ✅ Verifica Setup

Dopo aver completato tutti i passi, esegui:

```bash
cd backend
python scripts/test_db_postgres.py
```

Oppure testa direttamente:

```python
from sqlalchemy import create_engine, text

db_url = "postgresql+psycopg2://postgres:N0nn0c4rl0!!@localhost:5432/geko_db"
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connessione OK!")
```

## 🔍 Troubleshooting

### Problema: Autenticazione fallita anche in PgAdmin

- Verifica che la password sia corretta
- Controlla se ci sono caratteri invisibili o spazi
- Verifica il file `pg_hba.conf` per permettere connessioni locali

### Problema: Database già esiste

- Puoi eliminarlo: `DROP DATABASE geko_db;`
- Oppure usare quello esistente (verifica che abbia le tabelle corrette)

### Problema: Errori SQL durante creazione tabelle

- Verifica che il database `geko_db` sia selezionato
- Verifica che non ci siano tabelle duplicate
- Usa `DROP TABLE IF EXISTS` prima di ricrearle se necessario

---

**Ultimo aggiornamento:** 2025-11-03

