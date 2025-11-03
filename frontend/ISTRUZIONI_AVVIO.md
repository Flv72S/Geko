# 🚀 Istruzioni Avvio Frontend Geko

## ✅ Risultato Diagnostica

La diagnostica completa ha verificato che:
- ✅ Node.js v20.12.2 installato
- ✅ npm 10.5.0 installato
- ✅ Tutte le dipendenze installate
- ✅ Build funzionante
- ✅ Struttura file completa
- ✅ Porta 5173 disponibile

## 🔧 Come Avviare il Server

### Metodo 1: Terminale PowerShell

```powershell
cd C:\Users\flavi\Geko\frontend
npm run dev
```

### Metodo 2: Script PowerShell

```powershell
cd C:\Users\flavi\Geko\frontend
.\avvia-server.ps1
```

### Metodo 3: Cursor Terminal

1. Apri il terminale integrato in Cursor (Ctrl + `)
2. Naviga nella cartella frontend:
   ```bash
   cd frontend
   ```
3. Avvia il server:
   ```bash
   npm run dev
   ```

## 📋 Output Atteso

Dopo l'avvio, dovresti vedere:

```
  VITE v5.4.21  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 🌐 Apri nel Browser

Una volta avviato il server, apri:
- **http://localhost:5173**

Dovresti vedere la pagina di login di Geko.

## ⚠️ Se il Server Non Si Avvia

1. **Verifica che non ci siano altri processi sulla porta 5173:**
   ```powershell
   netstat -ano | findstr :5173
   ```

2. **Se la porta è occupata, termina il processo:**
   ```powershell
   Stop-Process -Id <PID> -Force
   ```

3. **Rimuovi node_modules e reinstalla:**
   ```powershell
   Remove-Item -Recurse -Force node_modules
   npm install
   ```

4. **Riesegui la diagnostica:**
   ```powershell
   node scripts/frontend_diagnostic.js
   ```

## 📝 Note

- Il server dev deve rimanere in esecuzione per vedere le modifiche
- Non chiudere il terminale mentre il server è attivo
- Premi `CTRL+C` nel terminale per fermare il server

---

**Ultimo controllo:** 2025-11-03
**Stato diagnostica:** ✅ Tutti i test passati

