# 🔄 AI SIEM - Flow Diagram

## 📊 Diagram Przepływu Danych

```mermaid
flowchart TB
    %% ============ AI Applications Layer ============
    subgraph AI_Apps["🤖 AI Applications Layer"]
        OpenAI["OpenAI<br/>(GPT-3.5, GPT-4)"]
        Anthropic["Anthropic<br/>(Claude)"]
        Gemini["Google Gemini<br/>(Gemini Pro)"]
        Ollama["Ollama<br/>(llama2, mistral)"]
        LMStudio["LM Studio<br/>(Local Models)"]
        LocalAI["LocalAI<br/>(Local Server)"]
    end

    %% ============ Collectors Layer ============
    subgraph Collectors["🎯 Collectors Layer - API Interception"]
        OpenAICol["OpenAICollector"]
        AnthropicCol["AnthropicCollector"]
        GeminiCol["GeminiCollector"]
        OllamaCol["OllamaCollector"]
        LMStudioCol["LMStudioCollector"]
        LocalAICol["LocalAICollector"]
    end

    %% ============ Event Creation ============
    subgraph EventGen["📝 Event Generation"]
        CreateEvent["Create AIEvent<br/>- Request ID<br/>- Timestamp<br/>- Provider & Model<br/>- Prompt & Response<br/>- Latency<br/>- Tokens<br/>- Cost"]
    end

    %% ============ Processing Layer ============
    subgraph Processing["⚙️ Processing Layer"]
        EventProc["EventProcessor"]

        subgraph Security["🔒 Security Analysis"]
            PIIDetect["PII Detection<br/>- Email<br/>- Phone<br/>- SSN<br/>- Credit Cards<br/>- IP Addresses"]
            InjectionDetect["Injection Detection<br/>- Prompt Injection<br/>- System Prompts<br/>- Instruction Override"]
        end

        RiskCalc["Risk Level Calculation<br/>- Failed Requests: +3<br/>- Injection: +4<br/>- PII: +2<br/>- High Latency: +1<br/>- High Tokens: +1<br/>- High Cost: +2"]

        EventAgg["EventAggregator<br/>- Metrics Calculation<br/>- Time Windows<br/>- Provider Stats<br/>- Model Stats"]
    end

    %% ============ Analysis Layer ============
    subgraph Analysis["🔍 Analysis Layer"]
        AnomalyDet["AnomalyDetector"]

        subgraph Checks["Anomaly Checks"]
            CostCheck["Cost Anomalies<br/>- High Cost (>$0.50)<br/>- Cost Spike (3x avg)"]
            LatencyCheck["Latency Anomalies<br/>- High Latency (>5000ms)<br/>- Latency Spike (3x avg)"]
            ErrorCheck["Error Detection<br/>- Request Failures<br/>- High Error Rate (>10%)<br/>- Model-specific Errors"]
            SecurityCheck["Security Threats<br/>- Prompt Injection (CRITICAL)<br/>- PII Detected (HIGH)"]
            PatternCheck["Pattern Analysis<br/>- High Request Rate<br/>- Cost Accumulation<br/>- Unusual Activity"]
        end

        CreateAnomaly["Create Anomaly Objects<br/>- Severity Level<br/>- Description<br/>- Recommended Action"]
    end

    %% ============ Storage Layer ============
    subgraph Storage["💾 Storage Layer"]
        EventStorage["EventStorage<br/>(SQLite)"]

        subgraph Tables["Database Tables"]
            EventsTable["events table<br/>- Request Data<br/>- Response Data<br/>- Metrics<br/>- Security Flags"]
            AnomaliesTable["anomalies table<br/>- Anomaly Type<br/>- Severity<br/>- Details<br/>- Actions"]
        end

        Indexes["Indexes<br/>- Timestamp<br/>- Provider<br/>- Model<br/>- Risk Level<br/>- Severity"]
    end

    %% ============ Presentation Layer ============
    subgraph Presentation["📊 Presentation Layer"]
        CLI["CLI Dashboard"]

        subgraph Views["Dashboard Views"]
            Stats["Statistics<br/>- Total Requests<br/>- Success Rate<br/>- Cost Summary<br/>- Token Usage"]
            RecentEvents["Recent Events<br/>- Latest Requests<br/>- Response Times<br/>- Risk Levels"]
            AnomaliesList["Anomalies List<br/>- Security Incidents<br/>- Cost Alerts<br/>- Performance Issues"]
            Alerts["Real-time Alerts<br/>- Critical Threats<br/>- High Costs<br/>- System Errors"]
        end
    end

    %% ============ Main Flow Connections ============
    OpenAI --> OpenAICol
    Anthropic --> AnthropicCol
    Gemini --> GeminiCol
    Ollama --> OllamaCol
    LMStudio --> LMStudioCol
    LocalAI --> LocalAICol

    OpenAICol --> CreateEvent
    AnthropicCol --> CreateEvent
    GeminiCol --> CreateEvent
    OllamaCol --> CreateEvent
    LMStudioCol --> CreateEvent
    LocalAICol --> CreateEvent

    CreateEvent --> EventProc

    EventProc --> PIIDetect
    EventProc --> InjectionDetect
    PIIDetect --> RiskCalc
    InjectionDetect --> RiskCalc

    RiskCalc --> EventAgg
    EventAgg --> AnomalyDet

    AnomalyDet --> CostCheck
    AnomalyDet --> LatencyCheck
    AnomalyDet --> ErrorCheck
    AnomalyDet --> SecurityCheck
    AnomalyDet --> PatternCheck

    CostCheck --> CreateAnomaly
    LatencyCheck --> CreateAnomaly
    ErrorCheck --> CreateAnomaly
    SecurityCheck --> CreateAnomaly
    PatternCheck --> CreateAnomaly

    EventProc --> EventStorage
    CreateAnomaly --> EventStorage

    EventStorage --> EventsTable
    EventStorage --> AnomaliesTable
    EventsTable --> Indexes
    AnomaliesTable --> Indexes

    EventStorage --> CLI
    CLI --> Stats
    CLI --> RecentEvents
    CLI --> AnomaliesList
    CLI --> Alerts

    %% ============ Styling ============
    classDef appLayer fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef collectorLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef processLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef analysisLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef storageLayer fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef presentLayer fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    class OpenAI,Anthropic,Gemini,Ollama,LMStudio,LocalAI appLayer
    class OpenAICol,AnthropicCol,GeminiCol,OllamaCol,LMStudioCol,LocalAICol collectorLayer
    class EventProc,PIIDetect,InjectionDetect,RiskCalc,EventAgg processLayer
    class AnomalyDet,CostCheck,LatencyCheck,ErrorCheck,SecurityCheck,PatternCheck,CreateAnomaly analysisLayer
    class EventStorage,EventsTable,AnomaliesTable,Indexes storageLayer
    class CLI,Stats,RecentEvents,AnomaliesList,Alerts presentLayer
```

## 🔄 Szczegółowy Przepływ Procesu

### 1️⃣ Faza Przechwytywania (Interception Phase)

```mermaid
sequenceDiagram
    participant App as Aplikacja
    participant Collector as Collector
    participant LLM as LLM API
    participant EventGen as Event Generator

    App->>Collector: Wywołanie API (prompt)
    Note over Collector: Start Timer
    Collector->>LLM: Przekazanie zapytania
    LLM-->>Collector: Odpowiedź + metadata
    Note over Collector: Stop Timer<br/>Oblicz latencję
    Collector->>EventGen: Utwórz AIEvent
    Note over EventGen: Wyodrębnienie:<br/>- Prompt & Response<br/>- Tokens (prompt/completion)<br/>- Cost (provider-specific)<br/>- Latency<br/>- Metadata
    EventGen-->>Collector: AIEvent object
    Collector->>App: Zwróć odpowiedź
```

### 2️⃣ Faza Przetwarzania (Processing Phase)

```mermaid
flowchart LR
    Event[AIEvent] --> Processor[EventProcessor]

    Processor --> PII[PII Detection]
    PII --> Email[Email Regex]
    PII --> Phone[Phone Regex]
    PII --> SSN[SSN Regex]
    PII --> CC[Credit Card Regex]
    PII --> IP[IP Address Regex]

    Processor --> Injection[Injection Detection]
    Injection --> Pattern1["'ignore previous instructions'"]
    Injection --> Pattern2["'disregard all prior'"]
    Injection --> Pattern3["'new instructions:'"]
    Injection --> Pattern4["System prompt override"]

    Email & Phone & SSN & CC & IP --> SetPII[Set has_pii flag]
    Pattern1 & Pattern2 & Pattern3 & Pattern4 --> SetInj[Set injection_detected flag]

    SetPII & SetInj --> RiskCalc[Risk Level Calculator]

    RiskCalc --> Score{Calculate<br/>Risk Score}
    Score -->|Score >= 5| Critical[CRITICAL]
    Score -->|Score >= 3| High[HIGH]
    Score -->|Score >= 1| Medium[MEDIUM]
    Score -->|Score < 1| Low[LOW]

    Critical & High & Medium & Low --> EnrichedEvent[Enriched AIEvent]
```

### 3️⃣ Faza Analizy Anomalii (Anomaly Detection Phase)

```mermaid
flowchart TB
    Event[Enriched Event] --> Analyzer[AnomalyDetector]
    Historical[Historical Events] --> Analyzer

    Analyzer --> ThresholdChecks[Threshold Checks]
    Analyzer --> SpikeDetection[Spike Detection]
    Analyzer --> PatternAnalysis[Pattern Analysis]

    ThresholdChecks --> T1{Cost > $0.50?}
    ThresholdChecks --> T2{Latency > 5000ms?}
    ThresholdChecks --> T3{Tokens > 8000?}
    ThresholdChecks --> T4{Error Rate > 10%?}

    SpikeDetection --> S1{Cost > 3x avg?}
    SpikeDetection --> S2{Latency > 3x avg?}

    PatternAnalysis --> P1{Request Rate > 50/min?}
    PatternAnalysis --> P2{Hourly Cost > $10?}
    PatternAnalysis --> P3{Model-specific errors?}

    T1 & T2 & T3 & T4 & S1 & S2 & P1 & P2 & P3 --> CreateAnomalies[Create Anomaly Objects]

    CreateAnomalies --> Severity{Assign<br/>Severity}
    Severity --> CRIT[CRITICAL<br/>Prompt Injection<br/>High Error Rate]
    Severity --> HIGH[HIGH<br/>Request Failure<br/>Cost Spike<br/>PII Detected]
    Severity --> MED[MEDIUM<br/>High Latency<br/>High Tokens<br/>Latency Spike]

    CRIT & HIGH & MED --> Actions[Recommended Actions]
    Actions --> AnomalyList[List of Anomalies]
```

### 4️⃣ Faza Przechowywania (Storage Phase)

```mermaid
flowchart LR
    EnrichedEvent[Enriched Event] --> Storage[EventStorage]
    Anomalies[Anomaly List] --> Storage

    Storage --> Parse[Parse to SQL]
    Parse --> InsertEvent[INSERT INTO events]
    Parse --> InsertAnomaly[INSERT INTO anomalies]

    InsertEvent --> EventRecord[Event Record<br/>- id, timestamp<br/>- provider, model<br/>- prompt, response<br/>- latency, tokens, cost<br/>- success, error<br/>- has_pii, injection<br/>- risk_level<br/>- metadata]

    InsertAnomaly --> AnomalyRecord[Anomaly Record<br/>- id, event_id<br/>- timestamp<br/>- anomaly_type<br/>- severity<br/>- description<br/>- details<br/>- recommended_action]

    EventRecord --> Index1[Index: timestamp]
    EventRecord --> Index2[Index: provider]
    EventRecord --> Index3[Index: model]
    EventRecord --> Index4[Index: risk_level]

    AnomalyRecord --> Index5[Index: timestamp]
    AnomalyRecord --> Index6[Index: severity]

    Index1 & Index2 & Index3 & Index4 & Index5 & Index6 --> DB[(SQLite Database)]
```

### 5️⃣ Faza Prezentacji (Presentation Phase)

```mermaid
flowchart TB
    DB[(Database)] --> Query[Query Engine]

    Query --> Stats[get_statistics<br/>hours=24]
    Query --> Recent[get_recent_events<br/>limit=100]
    Query --> Anom[get_recent_anomalies<br/>limit=50]
    Query --> Risk[get_events_by_risk<br/>risk_level]

    Stats --> Calculate[Calculate Metrics]
    Calculate --> M1[Total Requests<br/>Success Rate]
    Calculate --> M2[Total Tokens<br/>Avg Tokens/Request]
    Calculate --> M3[Avg/Max Latency]
    Calculate --> M4[Total Cost<br/>Avg Cost/Request]
    Calculate --> M5[PII Detections<br/>Injection Attempts]
    Calculate --> M6[Anomaly Count]

    M1 & M2 & M3 & M4 & M5 & M6 --> Dashboard[CLI Dashboard]
    Recent --> Dashboard
    Anom --> Dashboard
    Risk --> Dashboard

    Dashboard --> Display[Rich Console Display]
    Display --> Tables[Pretty Tables]
    Display --> Charts[Charts & Graphs]
    Display --> Alerts[Color-coded Alerts]

    Dashboard --> Export[Export Options]
    Export --> JSON[JSON Export]
    Export --> CSV[CSV Export]
```

## 🎯 Kluczowe Komponenty

### Collectors (collector.py, local_collector.py)
- **Rola**: Przechwytywanie wywołań API
- **Funkcje**:
  - Wrapping klientów API (monkey patching)
  - Pomiar latencji
  - Obliczanie kosztów
  - Emitowanie eventów

### EventProcessor (processor.py)
- **Rola**: Wzbogacanie eventów o analizy bezpieczeństwa
- **Funkcje**:
  - Wykrywanie PII (regex patterns)
  - Wykrywanie prompt injection
  - Kalkulacja poziomu ryzyka
  - Agregacja metryk

### AnomalyDetector (analyzer.py)
- **Rola**: Wykrywanie anomalii i zagrożeń
- **Funkcje**:
  - Sprawdzanie progów (threshold checks)
  - Wykrywanie skoków wartości (spike detection)
  - Analiza wzorców (pattern analysis)
  - Generowanie rekomendacji

### EventStorage (storage.py)
- **Rola**: Persystencja danych
- **Funkcje**:
  - Zapis eventów i anomalii
  - Indeksowanie dla szybkich zapytań
  - Zapytania agregujące
  - Statystyki czasowe

### CLI Dashboard (cli.py)
- **Rola**: Wizualizacja danych
- **Funkcje**:
  - Wyświetlanie statystyk
  - Lista eventów i anomalii
  - Alerty w czasie rzeczywistym
  - Eksport danych

## 📈 Metryki i Progi

| Metryka | Próg | Akcja | Severity |
|---------|------|-------|----------|
| **Cost per Request** | > $0.50 | Alert | HIGH |
| **Cost Spike** | > 3x średnia | Alert + Log | HIGH |
| **Latency** | > 5000ms | Monitor | MEDIUM |
| **Latency Spike** | > 3x średnia | Monitor | MEDIUM |
| **Prompt Injection** | Pattern match | **BLOCK** + Alert | **CRITICAL** |
| **PII Detected** | Regex match | Alert + Flag | HIGH |
| **Error Rate** | > 10% | Alert | **CRITICAL** |
| **Token Usage** | > 8000 tokens | Review | MEDIUM |
| **Request Rate** | > 50 req/min | Check for anomalies | MEDIUM |
| **Hourly Cost** | > $10/hour | Implement controls | HIGH |

## 🔐 Wzorce Wykrywania

### PII Detection Patterns
```regex
Email:        \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
Phone:        \b\d{3}[-.]?\d{3}[-.]?\d{4}\b
SSN:          \b\d{3}-\d{2}-\d{4}\b
Credit Card:  \b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b
IP Address:   \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b
```

### Prompt Injection Patterns
```regex
ignore\s+previous\s+instructions
disregard\s+all\s+prior
new\s+instructions:
system\s*:\s*you\s+are
</prompt>.*<prompt>
\n\nHuman:
\n\nAssistant:
```

## 🎨 Risk Level Scoring

```
Risk Score Calculation:
─────────────────────
Failed Request:       +3 points
Injection Detected:   +4 points
PII Present:          +2 points
High Latency (>10s):  +1 point
High Tokens (>10k):   +1 point
High Cost (>$1):      +2 points

Risk Level Mapping:
─────────────────────
CRITICAL:  Score >= 5
HIGH:      Score >= 3
MEDIUM:    Score >= 1
LOW:       Score < 1
```

## 📊 Typy Anomalii

| Typ Anomalii | Opis | Wykrywanie | Akcja |
|--------------|------|------------|-------|
| **high_cost** | Pojedyncze zapytanie > $0.50 | Threshold | Review model usage |
| **cost_spike** | Koszt > 3x średnia | Spike detection | Investigate activity |
| **high_latency** | Latencja > 5000ms | Threshold | Check API status |
| **latency_spike** | Latencja > 3x średnia | Spike detection | Monitor performance |
| **prompt_injection** | Wykryto próbę injection | Pattern matching | **BLOCK REQUEST** |
| **pii_detected** | Wykryto PII | Regex matching | Implement scrubbing |
| **request_failure** | Błąd zapytania | Error event | Check logs & credentials |
| **high_token_usage** | Tokeny > 8000 | Threshold | Implement limits |
| **high_error_rate** | Błędy > 10% | Pattern analysis | Check API status |
| **model_errors** | Błędy dla konkretnego modelu | Pattern analysis | Switch to backup |
| **high_request_rate** | > 50 zapytań/min | Pattern analysis | Check for runaway process |
| **high_cost_rate** | > $10/godzinę | Cost accumulation | Implement cost controls |

## 🔄 Event Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: API Call
    Created --> Intercepted: Collector wraps call
    Intercepted --> Measured: Timer start/stop
    Measured --> Enriched: EventProcessor

    Enriched --> PIICheck: Check for PII
    Enriched --> InjectionCheck: Check for injection

    PIICheck --> RiskScoring
    InjectionCheck --> RiskScoring

    RiskScoring --> Analyzed: AnomalyDetector
    Analyzed --> Stored: EventStorage
    Stored --> Presented: CLI Dashboard
    Presented --> [*]

    note right of Enriched
        Security Analysis:
        - PII patterns
        - Injection patterns
        - Risk calculation
    end note

    note right of Analyzed
        Anomaly Detection:
        - Threshold checks
        - Spike detection
        - Pattern analysis
    end note
```

## 🚀 Usage Flow Example

```mermaid
sequenceDiagram
    actor User
    participant App as Python App
    participant Collector as OpenAICollector
    participant Processor as EventProcessor
    participant Analyzer as AnomalyDetector
    participant Storage as EventStorage
    participant CLI as CLI Dashboard

    User->>App: Run script
    App->>Collector: Initialize with event_handler

    loop For each API call
        App->>Collector: chat.completions.create()
        Collector->>Collector: Intercept & measure
        Collector->>Processor: emit_event(AIEvent)

        Processor->>Processor: Detect PII
        Processor->>Processor: Detect injection
        Processor->>Processor: Calculate risk

        Processor->>Analyzer: analyze_event()
        Analyzer->>Analyzer: Check thresholds
        Analyzer->>Analyzer: Detect spikes
        Analyzer->>Analyzer: Analyze patterns

        alt Anomalies detected
            Analyzer->>Storage: store_anomaly()
            Analyzer-->>User: 🚨 ALERT: Critical threat!
        end

        Processor->>Storage: store_event()
        Storage->>Storage: Write to SQLite

        Collector-->>App: Return response
    end

    User->>CLI: make cli (view dashboard)
    CLI->>Storage: get_statistics()
    CLI->>Storage: get_recent_events()
    CLI->>Storage: get_recent_anomalies()
    Storage-->>CLI: Query results
    CLI-->>User: Display dashboard
```

---

## 📝 Podsumowanie

System AI SIEM działa w pięciu głównych fazach:

1. **Interception** - Przechwytywanie wywołań API przez Collectors
2. **Processing** - Analiza bezpieczeństwa i wzbogacanie eventów
3. **Analysis** - Wykrywanie anomalii i zagrożeń
4. **Storage** - Persystencja w SQLite z indeksowaniem
5. **Presentation** - Wizualizacja w CLI Dashboard

Każdy request przechodzi przez pełny pipeline monitoringu, co zapewnia kompleksową widoczność i bezpieczeństwo dla wszystkich interakcji z AI/LLM.
