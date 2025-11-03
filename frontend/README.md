# Geko Frontend

Frontend React + Vite + TailwindCSS per il progetto Geko AI Core.

## 🚀 Setup

### Installazione dipendenze

```bash
npm install
```

### Variabili d'ambiente

Crea un file `.env` nella root del frontend:

```
VITE_API_URL=http://localhost:8000
```

### Avvio sviluppo

```bash
npm run dev
```

L'applicazione sarà disponibile su `http://localhost:5173`

## 📁 Struttura

```
src/
├── components/     # Componenti riutilizzabili
├── pages/          # Pagine dell'applicazione
├── store/          # Store Zustand per gestione stato
├── services/       # Client API e servizi
└── App.jsx         # Componente principale con routing
```

## 🔐 Autenticazione

L'applicazione utilizza JWT per l'autenticazione:
- Login: `/login`
- Registrazione: `/register`
- Dashboard protetta: `/dashboard`

Il token viene salvato in `localStorage` e aggiunto automaticamente a tutte le richieste API tramite axios interceptors.

## 🛣️ Routing

- `/login` - Pagina pubblica di login
- `/register` - Pagina pubblica di registrazione
- `/dashboard` - Dashboard principale (protetta)
- `/profile` - Profilo utente (protetta)
- `/settings` - Impostazioni (protetta)

## 🎨 Stack Tecnologico

- **React 18** - Framework UI
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router DOM** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Framer Motion** - Animazioni
- **Lucide React** - Icone

## 📦 Build produzione

```bash
npm run build
```

Il build sarà disponibile in `dist/`

