# 🔄 Geko AI Core – Interfacce Dati e Flussi Interni

**Versione:** 1.0  
**Data:** 2025-11-02  
**Stato:** Definizione Tecnica - Fase 1.4 Microstep 2  
**Prerequisito:** [Architettura Modulare Completa](geko-ai-core-architecture.md)

---

## 🎯 Scopo del Documento

Questo documento definisce in dettaglio le **interfacce dati interne** e i **flussi informativi** tra i 5 moduli principali di **Geko AI Core**. Fornisce una mappa logico-funzionale che mostra come i dati vengono scambiati, trasformati e verificati all'interno del sistema.

L'obiettivo è garantire:
- **Interoperabilità** tra moduli
- **Tracciabilità** completa dei dati
- **Sicurezza** end-to-end
- **Performance** ottimizzate
- **Manutenibilità** del codice

---

## 📘 Contesto e Assunzioni

Geko AI Core è strutturato in 5 moduli principali (definiti nel Microstep 1):
1. **Perception Layer** - Raccolta e normalizzazione dati
2. **Reasoning Engine** - Inferenza e ragionamento
3. **Learning Pipeline** - Apprendimento continuo
4. **Action Layer** - Generazione azioni operative
5. **Interface Layer** - Interfacce esterne

Questo documento specifica:
- **Tipi di dati** scambiati tra moduli
- **Formati e strutture** standardizzate (JSON Schema)
- **Protocolli di comunicazione** (sincroni/asincroni)
- **Regole di validazione** e trasformazione
- **Meccanismi di logging** e audit
- **Sicurezza** e integrità dei dati

---

## 🧩 Flussi Inter-Modulari Principali

### 1️⃣ Flusso Perception → Reasoning

**Descrizione:**  
Il Perception Layer invia dati strutturati e normalizzati al Reasoning Engine per l'elaborazione cognitiva. Questo è il flusso primario di alimentazione dati del sistema.

**Origine:** `PerceptionLayer.Output`  
**Destinazione:** `ReasoningEngine.Input`  
**Tipo di Dati:** Dataset strutturato JSON con metadata  
**Frequenza:** Event-driven (triggered on data ingestion)  
**Volume Stimato:** 1000-10000 eventi/giorno

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["timestamp", "source", "content", "entities", "confidence"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp dell'evento"
    },
    "source": {
      "type": "string",
      "enum": [
        "LinkedIn_Crawl4AI",
        "WebScraper_Generic",
        "API_Salesforce",
        "API_HubSpot",
        "Sensor_IoT",
        "File_PDF",
        "Database_Query",
        "Email_IMAP",
        "RSS_Feed"
      ],
      "description": "Identificativo della fonte dati"
    },
    "source_id": {
      "type": "string",
      "description": "ID univoco della sorgente (es. account_id, sensor_id)"
    },
    "content": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100000,
      "description": "Contenuto testuale principale normalizzato (UTF-8)"
    },
    "content_type": {
      "type": "string",
      "enum": ["text", "html", "markdown", "structured"],
      "description": "Tipo di contenuto"
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Lista di entità nominate estratte (NER)"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Tag semantici applicati"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "language": {
          "type": "string",
          "pattern": "^[a-z]{2}(-[A-Z]{2})?$"
        },
        "author": {
          "type": "string"
        },
        "url": {
          "type": "string",
          "format": "uri"
        },
        "location": {
          "type": "object",
          "properties": {
            "country": {"type": "string"},
            "city": {"type": "string"},
            "coordinates": {
              "type": "object",
              "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"}
              }
            }
          }
        }
      }
    },
    "features": {
      "type": "object",
      "properties": {
        "embedding": {
          "type": "array",
          "items": {"type": "number"},
          "description": "Vettore embedding dimensionale (es. 768-dim)"
        },
        "keywords": {
          "type": "array",
          "items": {"type": "string"}
        },
        "sentiment": {
          "type": "number",
          "minimum": -1,
          "maximum": 1
        },
        "complexity_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidenza sulla qualità e accuratezza del dato"
    },
    "processing_id": {
      "type": "string",
      "description": "UUID univoco per tracciabilità"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Versione dello schema dati (SemVer)"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "timestamp": "2025-10-25T10:45:00Z",
  "source": "LinkedIn_Crawl4AI",
  "source_id": "linkedin_account_12345",
  "content": "Nuovo bando edilizio pubblicato a Milano per la riqualificazione di aree industriali dismesse. Budget disponibile: 5M€. Scadenza presentazione: 30/11/2025.",
  "content_type": "text",
  "entities": ["azienda", "progetto", "località", "bando", "budget"],
  "tags": ["bando", "edilizia", "pubblico", "riqualificazione", "Milano"],
  "metadata": {
    "language": "it",
    "author": "Comune di Milano",
    "url": "https://www.comune.milano.it/bandi/2025/12345",
    "location": {
      "country": "Italia",
      "city": "Milano",
      "coordinates": {
        "lat": 45.4642,
        "lon": 9.1900
      }
    }
  },
  "features": {
    "embedding": [0.123, -0.456, 0.789, ...],
    "keywords": ["bando", "edilizia", "Milano", "riqualificazione", "5M€"],
    "sentiment": 0.3,
    "complexity_score": 0.65
  },
  "confidence": 0.92,
  "processing_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0.0"
}
```

#### Protocollo di Scambio

- **Metodo:** Message Queue asincrona
- **Tecnologia:** Celery + Redis (o RabbitMQ per alta disponibilità)
- **Pattern:** Producer-Consumer con acknowledgment
- **Retry Policy:** 3 tentativi con backoff esponenziale (1s, 2s, 4s)
- **Dead Letter Queue:** Gestione messaggi falliti dopo 3 retry

#### Regole di Validazione

1. **Validazione Sintattica**
   - JSON Schema validation (schema version 1.0.0)
   - Reject se `confidence < 0.5`
   - Reject se `content` vuoto o nullo

2. **Normalizzazione**
   - Encoding: UTF-8 obbligatorio
   - Rimozione caratteri speciali non stampabili (es. control characters)
   - Normalizzazione whitespace (trim, collapse multiple spaces)

3. **Sanitizzazione**
   - Escape SQL injection patterns
   - Sanitize URL per prevenire XSS
   - Limite lunghezza `content`: max 100KB

#### Logging e Tracciabilità

- **Log File:** `logs/perception-events.log`
- **Formato Log:** JSON Lines (JSONL)
- **Campi Loggati:**
  - `timestamp`, `processing_id`, `source`, `confidence`, `status` (success/failure)
- **Retention:** 90 giorni, poi archivio compresso
- **Monitoring:** Metriche su `perception.throughput`, `perception.errors`, `perception.confidence_avg`

---

### 2️⃣ Flusso Reasoning → Learning

**Descrizione:**  
Il Reasoning Engine invia dataset arricchiti con correlazioni e inferenze al Learning Pipeline per l'addestramento continuo dei modelli. Solo i dati di alta qualità vengono utilizzati per il training.

**Origine:** `ReasoningEngine.Output`  
**Destinazione:** `LearningPipeline.Input`  
**Tipo di Dati:** Dataset arricchito con entità correlate e inferenze  
**Frequenza:** Batch quotidiano + event-driven per eventi critici  
**Volume Stimato:** 500-5000 record/giorno (filtrati)

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "entity_pairs",
    "inferred_relations",
    "confidence_matrix",
    "decision_summary",
    "context_vector"
  ],
  "properties": {
    "entity_pairs": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 2,
        "maxItems": 2
      },
      "description": "Coppie di entità correlate (es. [azienda, progetto])"
    },
    "inferred_relations": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "affidatario",
          "collaboratore",
          "competitore",
          "fornitore",
          "cliente",
          "partner",
          "parent_company",
          "subsidiary"
        ]
      },
      "description": "Relazioni inferite tra le entità"
    },
    "confidence_matrix": {
      "type": "array",
      "items": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
      },
      "description": "Array di confidence scores per ogni relazione inferita"
    },
    "decision_summary": {
      "type": "string",
      "description": "Riassunto della decisione/insight generato"
    },
    "context_vector": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 128,
      "maxItems": 1024,
      "description": "Vettore contestuale per rappresentazione semantica"
    },
    "reasoning_chain": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "step": {"type": "integer"},
          "rule_applied": {"type": "string"},
          "premise": {"type": "string"},
          "conclusion": {"type": "string"}
        }
      },
      "description": "Catenella di ragionamento (explainability)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "source_processing_id": {
      "type": "string",
      "description": "Link al processing_id originale dal Perception Layer"
    },
    "model_version": {
      "type": "string",
      "description": "Versione del modello Reasoning utilizzato"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "entity_pairs": [
    ["aziendaA", "progettoX"],
    ["aziendaB", "progettoY"],
    ["aziendaC", "bando_Milano_2025"]
  ],
  "inferred_relations": ["affidatario", "collaboratore", "candidato"],
  "confidence_matrix": [0.88, 0.91, 0.85],
  "decision_summary": "Relazione rilevante per bando attivo - aziendaA ha alta probabilità di essere affidataria per progettoX basandosi su storico progetti simili (3 casi precedenti, 100% success rate)",
  "context_vector": [0.11, 0.32, 0.45, 0.67, -0.12, 0.89, ...],
  "reasoning_chain": [
    {
      "step": 1,
      "rule_applied": "historical_similarity",
      "premise": "aziendaA ha completato 3 progetti simili a progettoX negli ultimi 2 anni",
      "conclusion": "Alta probabilità di competenza per progettoX"
    },
    {
      "step": 2,
      "rule_applied": "temporal_proximity",
      "premise": "Bando scade tra 30 giorni, aziendaA è attualmente disponibile",
      "conclusion": "Timing favorevole per partecipazione"
    },
    {
      "step": 3,
      "rule_applied": "location_match",
      "premise": "aziendaA ha sede operativa a Milano (stessa città del bando)",
      "conclusion": "Vantaggio logistico per aziendaA"
    }
  ],
  "timestamp": "2025-10-25T11:00:00Z",
  "source_processing_id": "550e8400-e29b-41d4-a716-446655440000",
  "model_version": "reasoning-v2.3.1"
}
```

#### Protocollo di Scambio

- **Metodo:** Pipeline asincrona con batching
- **Tecnologia:** Apache Kafka (o AWS Kinesis per cloud-native)
- **Topic:** `reasoning-to-learning`
- **Partitioning:** Per `entity_pairs[0]` (hash-based)
- **Batching:** Accumulo 100 record o 5 minuti (whichever comes first)

#### Regole di Validazione

1. **Filtri di Qualità**
   - Accettazione solo se `min(confidence_matrix) > 0.85`
   - Reject se `entity_pairs` vuoto
   - Reject se `context_vector` ha NaN o Infinity

2. **Controlli di Coerenza**
   - `len(inferred_relations) == len(confidence_matrix)`
   - `len(entity_pairs) == len(confidence_matrix)`

3. **Deduplicazione**
   - Hash su `entity_pairs` + `inferred_relations` per evitare duplicati
   - Window deduplication: 24 ore

#### Logging e Tracciabilità

- **Log File:** `logs/reasoning-train.log`
- **Database:** Salvataggio automatico su `geko_reasoning.db` (tabelle: `reasoning_outputs`, `entity_relations`)
- **Trigger Training:** Se variazione `context_vector` > 20% rispetto alla media storica → trigger addestramento incrementale
- **Monitoring:** `reasoning.learning_queue_size`, `reasoning.filtered_out_low_confidence`

---

### 3️⃣ Flusso Learning → Reasoning (Feedback Loop)

**Descrizione:**  
Il Learning Pipeline aggiorna il Reasoning Engine con modelli e parametri ottimizzati. Questo flusso rappresenta il ciclo di auto-miglioramento continuo del sistema.

**Origine:** `LearningPipeline.Output`  
**Destinazione:** `ReasoningEngine.KnowledgeGraph`  
**Tipo di Dati:** Modelli aggiornati e metriche di performance  
**Frequenza:** Event-driven su completion training  
**Volume Stimato:** 1-5 aggiornamenti/settimana

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "model_version",
    "weights_path",
    "accuracy_gain",
    "update_type"
  ],
  "properties": {
    "model_version": {
      "type": "string",
      "pattern": "^v\\d+\\.\\d+\\.\\d+$",
      "description": "Versione semantica del modello (es. v2.3.1)"
    },
    "weights_path": {
      "type": "string",
      "pattern": "^/models/[a-z]+/[\\w-]+\\.bin$",
      "description": "Path assoluto al file dei pesi del modello"
    },
    "weights_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA256 hash del file weights per integrità"
    },
    "update_type": {
      "type": "string",
      "enum": ["full_retrain", "incremental", "fine_tune", "hotfix"],
      "description": "Tipo di aggiornamento del modello"
    },
    "accuracy_gain": {
      "type": "number",
      "description": "Miglioramento dell'accuracy rispetto alla versione precedente"
    },
    "metrics": {
      "type": "object",
      "properties": {
        "precision": {"type": "number"},
        "recall": {"type": "number"},
        "f1_score": {"type": "number"},
        "accuracy": {"type": "number"},
        "confusion_matrix": {
          "type": "array",
          "items": {
            "type": "array",
            "items": {"type": "integer"}
          }
        }
      }
    },
    "update_notes": {
      "type": "string",
      "description": "Note descrittive dell'aggiornamento (changelog)"
    },
    "rollback_path": {
      "type": "string",
      "description": "Path al modello precedente per rollback se necessario"
    },
    "validation_status": {
      "type": "string",
      "enum": ["passed", "failed", "warning"],
      "description": "Stato della validazione post-training"
    },
    "deployment_strategy": {
      "type": "string",
      "enum": ["canary", "blue_green", "full_rollout"],
      "description": "Strategia di deployment"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "model_version": "v2.3.1",
  "weights_path": "/models/reasoning/transE_v2.3.1.bin",
  "weights_hash": "a3f5d8e9c2b1a4f6e8d9c7b5a3f1e2d4c6b8a9f7e5d3c1b2a4f6e8d9c7b5a3f",
  "update_type": "incremental",
  "accuracy_gain": 0.045,
  "metrics": {
    "precision": 0.92,
    "recall": 0.88,
    "f1_score": 0.90,
    "accuracy": 0.91,
    "confusion_matrix": [[850, 50], [30, 920]]
  },
  "update_notes": "Aumentata precisione relazioni 'azienda-progetto' del 4.5% dopo training su 5000 nuovi esempi. Miglioramento particolarmente evidente per progetti edilizi in Lombardia.",
  "rollback_path": "/models/reasoning/transE_v2.3.0.bin",
  "validation_status": "passed",
  "deployment_strategy": "canary",
  "timestamp": "2025-10-25T14:30:00Z"
}
```

#### Protocollo di Scambio

- **Metodo:** API REST interna sincrona
- **Endpoint:** `POST /internal/reasoning/update-model`
- **Autenticazione:** JWT interno con scope `internal:model-update`
- **Timeout:** 30 secondi

#### Regole di Validazione

1. **Integrità File**
   - Verifica SHA256 hash del file weights
   - Controllo dimensione file (max 500MB)
   - Validazione formato file (magic bytes)

2. **Performance Requirements**
   - Deploy solo se `accuracy_gain >= 0.02` (2% miglioramento minimo)
   - Reject se `f1_score < 0.70`
   - Warning se `precision` o `recall` calano > 5%

3. **Versionamento**
   - Backup automatico modello precedente
   - Registrazione nel model registry (`/models/registry/models.json`)
   - Tag Git del commit associato

#### Logging e Tracciabilità

- **Log File:** `logs/model-update.log`
- **Database:** Tabella `model_deployments` con history completa
- **Alerting:** Notifica su Slack/Email se `validation_status == "failed"`
- **Monitoring:** `reasoning.model_version`, `reasoning.accuracy_trend`

---

### 4️⃣ Flusso Reasoning → Action

**Descrizione:**  
Il Reasoning Engine genera insight e raccomandazioni che vengono trasformate in azioni operative concrete dall'Action Layer. Questo flusso traduce l'intelligenza in risultati tangibili.

**Origine:** `ReasoningEngine.Output`  
**Destinazione:** `ActionLayer.Input`  
**Tipo di Dati:** Insight e raccomandazioni operative  
**Frequenza:** Event-driven su detection di opportunità/rischi  
**Volume Stimato:** 50-500 azioni/giorno

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "id",
    "action_type",
    "message",
    "priority",
    "timestamp"
  ],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^GEKO-ACT-\\d{4}-\\d{4}$",
      "description": "ID univoco dell'azione (es. GEKO-ACT-2025-0012)"
    },
    "action_type": {
      "type": "string",
      "enum": [
        "notifica",
        "alert",
        "task",
        "report",
        "webhook",
        "crm_update",
        "email_send"
      ],
      "description": "Tipo di azione da eseguire"
    },
    "recipient": {
      "type": "string",
      "description": "Destinatario dell'azione (user_id, email, system)"
    },
    "recipient_type": {
      "type": "string",
      "enum": ["user", "role", "group", "external_system"],
      "description": "Tipo di destinatario"
    },
    "message": {
      "type": "string",
      "maxLength": 5000,
      "description": "Messaggio principale dell'azione"
    },
    "priority": {
      "type": "string",
      "enum": ["bassa", "media", "alta", "critica"],
      "description": "Priorità dell'azione"
    },
    "next_step": {
      "type": "string",
      "description": "Suggerimento per passo successivo"
    },
    "context": {
      "type": "object",
      "properties": {
        "reasoning_id": {"type": "string"},
        "entities": {
          "type": "array",
          "items": {"type": "string"}
        },
        "confidence": {"type": "number"},
        "source_url": {"type": "string", "format": "uri"}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "expires_at": {
          "type": "string",
          "format": "date-time"
        },
        "retry_count": {"type": "integer", "default": 0},
        "max_retries": {"type": "integer", "default": 3}
      }
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "id": "GEKO-ACT-2025-0012",
  "action_type": "notifica",
  "recipient": "utente_admin",
  "recipient_type": "user",
  "message": "Nuova opportunità edilizia rilevata con affidabilità 94%. Bando: 'Riqualificazione aree industriali Milano', Budget: 5M€, Scadenza: 30/11/2025. Azienda 'EdiliziaLombarda SpA' ha match 87% con requisiti.",
  "priority": "alta",
  "next_step": "Verifica contatto azienda e preparazione proposta di collaborazione",
  "context": {
    "reasoning_id": "REASON-2025-0456",
    "entities": ["bando_Milano_2025", "azienda_EdiliziaLombarda", "progetto_riqualificazione"],
    "confidence": 0.94,
    "source_url": "https://www.comune.milano.it/bandi/2025/12345"
  },
  "metadata": {
    "expires_at": "2025-11-30T23:59:59Z",
    "retry_count": 0,
    "max_retries": 3
  },
  "timestamp": "2025-10-25T11:05:00Z"
}
```

#### Protocollo di Scambio

- **Metodo:** REST call interna sincrona con dependency injection
- **Endpoint:** `POST /internal/actions/create`
- **Framework:** FastAPI internal routing
- **Timeout:** 5 secondi

#### Regole di Validazione

1. **Prioritizzazione**
   - `priority == "critica"` → immediate execution, bypass queue
   - `priority == "alta"` → push notification + email
   - `priority == "media"` → email only
   - `priority == "bassa"` → digest giornaliero

2. **Deduplicazione**
   - Hash su `action_type` + `recipient` + `message` (primi 100 chars)
   - Controllo in `pending_actions.json` (TTL: 24h)
   - Reject se duplicato trovato

3. **Expiry Management**
   - Skip se `expires_at < now()`
   - Auto-cleanup azioni scadute (cron job giornaliero)

#### Logging e Tracciabilità

- **Log File:** `logs/actions.log`
- **Database:** Tabella `actions` con stato (pending/executed/failed)
- **Push Notification:** Se `priority == "alta"` o `priority == "critica"`
- **Monitoring:** `actions.created`, `actions.executed`, `actions.failed`, `actions.avg_execution_time`

---

### 5️⃣ Flusso Action → Interface

**Descrizione:**  
L'Action Layer invia output formattati all'Interface Layer per la distribuzione esterna (API, webhook, notifiche). Questo è l'ultimo step prima della comunicazione con l'utente o sistemi esterni.

**Origine:** `ActionLayer.Output`  
**Destinazione:** `InterfaceLayer.Input`  
**Tipo di Dati:** Messaggi, report, task formattati  
**Frequenza:** Event-driven su completion azione  
**Volume Stimato:** 50-500 messaggi/giorno

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["endpoint", "payload", "method"],
  "properties": {
    "endpoint": {
      "type": "string",
      "pattern": "^/api/v\\d+/[\\w/-]+$",
      "description": "Endpoint API target (es. /api/v1/actions/notify)"
    },
    "method": {
      "type": "string",
      "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
      "description": "HTTP method"
    },
    "payload": {
      "type": "object",
      "description": "Payload da inviare all'endpoint"
    },
    "headers": {
      "type": "object",
      "properties": {
        "Authorization": {"type": "string"},
        "Content-Type": {"type": "string", "default": "application/json"},
        "X-Request-ID": {"type": "string"}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "retry_policy": {
          "type": "object",
          "properties": {
            "max_retries": {"type": "integer", "default": 3},
            "backoff_strategy": {
              "type": "string",
              "enum": ["exponential", "linear", "fixed"]
            },
            "initial_delay": {"type": "integer", "default": 1000}
          }
        },
        "timeout": {"type": "integer", "default": 5000},
        "rate_limit": {
          "type": "object",
          "properties": {
            "max_requests": {"type": "integer"},
            "window_seconds": {"type": "integer"}
          }
        }
      }
    },
    "action_id": {
      "type": "string",
      "description": "Riferimento all'action ID originale"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "endpoint": "/api/v1/actions/notify",
  "method": "POST",
  "payload": {
    "user": "admin",
    "type": "alert",
    "title": "Nuova Opportunità Edilizia",
    "message": "Nuova opportunità edilizia rilevata con affidabilità 94%...",
    "time": "2025-10-25T11:05:00Z",
    "action_id": "GEKO-ACT-2025-0012",
    "priority": "alta",
    "action_url": "https://app.geko.ai/actions/GEKO-ACT-2025-0012"
  },
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "Content-Type": "application/json",
    "X-Request-ID": "req-550e8400-e29b-41d4-a716-446655440000"
  },
  "metadata": {
    "retry_policy": {
      "max_retries": 3,
      "backoff_strategy": "exponential",
      "initial_delay": 1000
    },
    "timeout": 5000,
    "rate_limit": {
      "max_requests": 5,
      "window_seconds": 1
    }
  },
  "action_id": "GEKO-ACT-2025-0012",
  "timestamp": "2025-10-25T11:05:00Z"
}
```

#### Protocollo di Scambio

- **Metodo:** API REST interna (FastAPI internal routing)
- **Endpoint:** Dinamico basato su `endpoint` field
- **Autenticazione:** JWT obbligatorio (header Authorization)
- **Content-Type:** `application/json`

#### Regole di Validazione

1. **Autenticazione**
   - JWT validation obbligatoria
   - Scope check: `actions:execute`
   - Rate limit: 5 richieste/secondo per utente

2. **Retry Logic**
   - Retry automatico su errori 5xx
   - Exponential backoff: 1s, 2s, 4s
   - Dead letter queue dopo 3 tentativi falliti

3. **Rate Limiting**
   - Global rate limit: 100 req/sec
   - Per-user rate limit: 10 req/sec
   - HTTP 429 (Too Many Requests) se superato

#### Logging e Tracciabilità

- **Log File:** `logs/interface-events.log`
- **Audit Trail:** Tutte le chiamate API loggate in `audit.log`
- **Metrics:** `interface.requests_total`, `interface.requests_failed`, `interface.avg_latency`
- **Tracing:** Distributed tracing con OpenTelemetry (trace_id propagation)

---

### 6️⃣ Flusso Interface → Perception (Ciclo Esterno)

**Descrizione:**  
L'Interface Layer riceve comandi esterni (da utenti o sistemi) che vengono tradotti in richieste per il Perception Layer. Questo chiude il ciclo esterno del sistema.

**Origine:** `InterfaceLayer.Input` (esterno)  
**Destinazione:** `PerceptionLayer`  
**Tipo di Dati:** Comandi utente o trigger API  
**Frequenza:** On-demand o scheduled  
**Volume Stimato:** 10-100 comandi/giorno

#### Schema Dati (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["command", "timestamp"],
  "properties": {
    "command": {
      "type": "string",
      "enum": [
        "aggiorna_fonti",
        "crawl_url",
        "import_file",
        "sync_crm",
        "refresh_data",
        "stop_crawl"
      ],
      "description": "Tipo di comando da eseguire"
    },
    "source_url": {
      "type": "string",
      "format": "uri",
      "description": "URL da processare (per comandi crawl-related)"
    },
    "source_type": {
      "type": "string",
      "enum": ["web", "api", "file", "database", "crm"],
      "description": "Tipo di sorgente"
    },
    "interval": {
      "type": "string",
      "pattern": "^\\d+[hms]$",
      "description": "Intervallo per comandi ricorrenti (es. 24h, 1h, 30m)"
    },
    "parameters": {
      "type": "object",
      "description": "Parametri aggiuntivi specifici del comando"
    },
    "user_id": {
      "type": "string",
      "description": "ID utente che ha emesso il comando"
    },
    "api_key": {
      "type": "string",
      "description": "API key per autenticazione (se da sistema esterno)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "request_id": {
      "type": "string",
      "description": "UUID per tracciabilità della richiesta"
    }
  }
}
```

#### Esempio Dato Reale

```json
{
  "command": "aggiorna_fonti",
  "source_url": "https://example.com/bandi",
  "source_type": "web",
  "interval": "24h",
  "parameters": {
    "crawl_depth": 3,
    "respect_robots_txt": true,
    "user_agent": "GekoBot/1.0",
    "extract_patterns": ["bando", "gara", "appalto"]
  },
  "user_id": "user_admin_123",
  "api_key": null,
  "timestamp": "2025-10-25T12:00:00Z",
  "request_id": "req-660e8400-e29b-41d4-a716-446655440001"
}
```

#### Protocollo di Scambio

- **Metodo:** Webhook o API POST
- **Endpoint:** `POST /api/v1/perception/trigger`
- **Autenticazione:** JWT (utenti) o API Key (sistemi esterni)
- **Header Richiesto:** `X-Token` per validazione sicurezza

#### Regole di Validazione

1. **Sicurezza**
   - Validazione `X-Token` header (HMAC-SHA256)
   - Rate limiting: 10 comandi/minuto per utente
   - Sanitizzazione `source_url` (whitelist domini permessi)

2. **Audit e Compliance**
   - Log comando in `audit.log` con `user_id` e `timestamp`
   - Tracciabilità completa per compliance (GDPR, SOC2)

3. **Execution**
   - Trigger `crawl_manager.start(source_url)` per comandi crawl
   - Scheduling automatico se `interval` specificato
   - Confirmation response con `job_id` per tracking

#### Logging e Tracciabilità

- **Log File:** `logs/audit.log` (immutable, append-only)
- **Database:** Tabella `user_commands` con history completa
- **Alerting:** Notifica admin su comandi `stop_crawl` o errori critici
- **Monitoring:** `interface.commands_total`, `interface.commands_failed`

---

## 📊 Mappatura Completa dei Flussi

### Tabella Flussi Inter-Modulari

| Origine | Destinazione | Tipo Dati | Metodo | Log File | Trigger/Condizioni | Volume/Giorno |
|---------|--------------|-----------|--------|----------|---------------------|---------------|
| **Perception** | **Reasoning** | JSON Dataset | Queue (Celery/Redis) | `perception-events.log` | On data ingestion | 1K-10K |
| **Reasoning** | **Learning** | JSON Enriched | Pipeline (Kafka) | `reasoning-train.log` | `confidence > 0.85` | 500-5K |
| **Learning** | **Reasoning** | Model file | API REST | `model-update.log` | `accuracy_gain > 0.02` | 1-5/settimana |
| **Reasoning** | **Action** | JSON Insight | REST internal | `actions.log` | `priority == "alta"` | 50-500 |
| **Action** | **Interface** | JSON Message | API REST | `interface-events.log` | Always | 50-500 |
| **Interface** | **Perception** | JSON Command | Webhook/API | `audit.log` | On user command | 10-100 |

### Flussi Secondari e Cross-Module

1. **Action → Learning (Feedback Implicito)**
   - Metriche di successo/fallimento azioni
   - Formato: `{action_id, success, metrics, timestamp}`
   - Metodo: Event stream (Kafka topic: `action-feedback`)

2. **Interface → Reasoning (Direct Query)**
   - Query dirette per insight on-demand
   - Formato: GraphQL query
   - Metodo: GraphQL API sincrona

3. **Perception → Learning (Raw Data)**
   - Dataset raw per training unsupervised
   - Formato: Parquet/JSON Lines
   - Metodo: Batch upload (S3/MinIO) settimanale

---

## 🔐 Sicurezza e Tracciabilità

### Autenticazione e Autorizzazione

1. **Comunicazioni Interne**
   - JWT tokens con scope-specific (`internal:*`)
   - Rotazione token: 24 ore
   - Service-to-service authentication via mTLS (opzionale)

2. **Comunicazioni Esterne**
   - OAuth 2.0 + JWT per utenti
   - API Keys per sistemi esterni (rotazione ogni 90 giorni)
   - Rate limiting per prevenire abuse

### Integrità Dati

1. **Firma Digitale**
   - Flussi asincroni firmati con HMAC-SHA256
   - Header `X-Signature` su tutti i messaggi Kafka/Celery
   - Validazione automatica prima del processing

2. **Checksum Modelli**
   - Tutti i modelli AI con SHA256 hash
   - Verifica hash prima del deployment
   - Registrazione hash nel model registry

### Audit e Compliance

1. **Logging Immutabile**
   - Tutti i log in formato append-only
   - Timestamp UTC con nanosecond precision
   - Correlation ID per tracciabilità end-to-end

2. **Archiviazione**
   - Rotazione log settimanale
   - Compressione ZIP dopo 30 giorni
   - Retention: 90 giorni (hot), 2 anni (cold storage)

3. **Compliance**
   - GDPR: Pseudonimizzazione dati personali nei log
   - SOC2: Audit trail completo per controlli
   - HIPAA: Encryption at-rest per dati sanitari (se applicabile)

---

## 🧱 Diagramma ASCII Flussi Inter-Modulari

```
╔══════════════════════════════════════════════════════════════════════╗
║                  GEKO AI CORE - DATA FLOW DIAGRAM                    ║
╚══════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────┐
│                    5️⃣ INTERFACE LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  External API / Webhook / User Commands                        │ │
│  └───────────────────┬──────────────────────────────────────────┘ │
│                      │                                              │
│                      │ [6] Command JSON                             │
│                      │ (Webhook/API POST)                           │
│                      ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Security Gateway (JWT/API Key validation)                   │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────┬──────────────────────────────┬─────────────┘
                        │                              │
                        │                              │
                        │ [5] Message JSON             │ [5] Response JSON
                        │ (REST API)                   │ (HTTP Response)
                        │                              │
                        ▼                              │
┌────────────────────────────────────────────────────────────────────┐
│                    4️⃣ ACTION LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Action Generator → Automation Dispatcher                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────┬────────────────────────────────────────────┘
                        │
                        │ [4] Insight JSON
                        │ (REST internal)
                        │
                        ▼
┌────────────────────────────────────────────────────────────────────┐
│                    2️⃣ REASONING ENGINE                            │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Rule-Based Logic → Knowledge Graph → Inference Engine      │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────┬──────────────────────────┬───────────────────────────────┘
        │                          │
        │                          │
        │ [1] Dataset JSON          │ [2] Enriched Dataset JSON
        │ (Celery Queue)           │ (Kafka Pipeline)
        │                          │
        ▼                          ▼
┌────────────────────────────────────────────────────────────────────┐
│                    1️⃣ PERCEPTION LAYER                            │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Data Collector → Normalizer → Feature Extractor             │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                        ▲
                        │
                        │ [6] Command JSON
                        │ (Internal routing)
                        │
        ┌───────────────┴───────────────┐
        │                               │
        │                               │
        │ [3] Model Update JSON         │ [3] Feedback Metrics
        │ (REST API)                   │ (Event Stream)
        │                               │
        ▼                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                    3️⃣ LEARNING PIPELINE                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Training Orchestrator → Model Evaluator → Model Updater    │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════╗
║                         LEGENDA FLUSSI                               ║
╚══════════════════════════════════════════════════════════════════════╝

[1] Perception → Reasoning: Dataset strutturato (JSON)
    Metodo: Celery Queue asincrona
    Volume: 1K-10K eventi/giorno

[2] Reasoning → Learning: Dataset arricchito (JSON)
    Metodo: Kafka Pipeline asincrona
    Filtro: confidence > 0.85
    Volume: 500-5K eventi/giorno

[3] Learning → Reasoning: Model update (JSON + Binary)
    Metodo: REST API sincrona
    Trigger: accuracy_gain > 0.02
    Volume: 1-5/settimana

[4] Reasoning → Action: Insight e raccomandazioni (JSON)
    Metodo: REST internal sincrona
    Trigger: priority-based
    Volume: 50-500/giorno

[5] Action → Interface: Messaggi formattati (JSON)
    Metodo: REST API
    Volume: 50-500/giorno

[6] Interface → Perception: Comandi utente (JSON)
    Metodo: Webhook/API POST
    Volume: 10-100/giorno

═══════════════════════════════════════════════════════════════════════

🔄 FEEDBACK LOOPS (Bidirectional):

  Reasoning ◄──► Learning  (Continuous optimization loop)
  Action ──► Learning       (Implicit feedback from action outcomes)

═══════════════════════════════════════════════════════════════════════

🔐 SICUREZZA (Applied to all flows):

  ✓ JWT Authentication (internal communications)
  ✓ HMAC-SHA256 Signatures (async flows)
  ✓ SHA256 Checksums (model files)
  ✓ Audit Logging (all operations)
  ✓ Rate Limiting (API endpoints)

═══════════════════════════════════════════════════════════════════════
```

---

## 📋 Checklist Validazione Interfacce

### Per Ogni Flusso Implementato

- [ ] Schema JSON validato con JSON Schema Draft 7
- [ ] Esempio dati reale documentato
- [ ] Protocollo di scambio specificato (sync/async)
- [ ] Regole di validazione implementate
- [ ] Logging e tracciabilità configurati
- [ ] Sicurezza applicata (JWT/HMAC/checksum)
- [ ] Monitoring e alerting configurati
- [ ] Test unitari e di integrazione scritti
- [ ] Documentazione API aggiornata

---

## ✅ Conclusioni

Questo documento fornisce la **specifica completa** delle interfacce dati e flussi interni di Geko AI Core, garantendo:

✅ **Interoperabilità** tra moduli tramite formati standardizzati  
✅ **Tracciabilità** end-to-end con correlation IDs  
✅ **Sicurezza** multi-livello (auth, integrity, encryption)  
✅ **Scalabilità** attraverso pattern asincroni e queue  
✅ **Manutenibilità** con schema versioning e backward compatibility  
✅ **Osservabilità** tramite logging strutturato e metrics  

La prossima fase (Microstep 3) definirà lo **Schema Database** e il **Storage Layer** per la persistenza dei dati strutturati.

---

**Documento redatto per:** Fase 1.4 - Microstep 2  
**Prossimo step:** Schema Database + Storage Layer (Microstep 3)  
**Mantenuto da:** Team Geko AI  
**Versionamento:** [SemVer](https://semver.org/)

