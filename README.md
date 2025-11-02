# 🚀 Geko - Progetto di Analisi e Processing

## Descrizione
Geko è un progetto di analisi e processing di documenti con backend FastAPI e frontend React.

## Struttura del Progetto

```
Geko/
├── backend/          # Backend FastAPI
├── frontend/         # Frontend React + Vite
├── docs/             # Documentazione
├── data/             # Database e file di dati
└── docker-compose.yml # Configurazione Docker
```

## Setup Ambiente di Sviluppo

### Prerequisiti
- Python 3.8+
- Node.js 18+
- Git

### Backend

1. Crea e attiva l'ambiente virtuale:
```bash
python -m venv .venv_geko
.venv_geko\Scripts\activate  # Windows
```

2. Installa le dipendenze:
```bash
pip install -r backend/requirements.txt
```

3. Avvia il server:
```bash
uvicorn app.main:app --reload
```

Il backend sarà disponibile su `http://localhost:8000`

### Frontend

1. Installa le dipendenze:
```bash
cd frontend
npm install
```

2. Avvia il server di sviluppo:
```bash
npm run dev
```

Il frontend sarà disponibile su `http://localhost:3000`

## Variabili d'Ambiente

Copia `.env.example` in `.env` e configura le variabili necessarie.

## Licenza
[Da definire]


