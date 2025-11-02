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

