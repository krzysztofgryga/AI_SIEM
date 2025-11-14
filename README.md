# 🤖 AI Agent Security Monitoring Platform

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Complete monitoring, security, and cost tracking system for AI agents and LLMs.**

Monitor OpenAI, Anthropic, Ollama, LM Studio, and any other LLM with:
- 🔒 Security threat detection (PII, prompt injection)
- 💰 Real-time cost tracking and anomaly detection
- 📊 Performance monitoring (latency, tokens, errors)
- 🐳 Docker-ready deployment
- 💻 **Works 100% locally - NO API keys required!**

---

## ⚡ Quick Start (2 Minutes)

```bash
git clone https://github.com/krzysztofgryga/AI_SIEM.git
cd AI_SIEM/poc
make setup
```

**Done!** 🎉 You now have:
- ✅ Ollama running (local LLM server)
- ✅ Monitoring active
- ✅ Example model downloaded
- ✅ Database initialized

Test it:
```bash
make test    # Run example
make cli     # View dashboard
```

---

## 🌟 Features

### 🔐 Security Monitoring
- **PII Detection**: Automatically detect emails, phone numbers, SSN, credit cards
- **Prompt Injection Detection**: Pattern matching + semantic analysis
- **Risk Scoring**: Multi-factor risk assessment for every request
- **Real-time Alerts**: Console alerts for critical security events

### 💰 Cost Management
- **Real-time Cost Tracking**: Per-request and aggregate costs
- **Cost Anomaly Detection**: Detect cost spikes (3x average)
- **Budget Monitoring**: Track spending vs limits
- **Multi-provider Comparison**: Compare costs across providers

### 📊 Performance Analytics
- **Latency Monitoring**: Track and alert on slow responses
- **Token Usage**: Monitor prompt/completion token consumption
- **Error Rate Tracking**: Detect and alert on high error rates
- **Quality Metrics**: Assess response quality

### 🌐 Multi-Provider Support

**Cloud APIs:**
- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude 3 models)

**Local LLMs (FREE!):**
- Ollama (llama2, mistral, etc.)
- LM Studio
- LocalAI

### 🎯 Zero-Code Integration
```python
from openai import OpenAI
from collector import OpenAICollector

client = OpenAI()
monitored = OpenAICollector(client, event_handler=my_handler)

# Normal usage - automatically monitored!
response = monitored.client.chat.completions.create(...)
```

---

## 📖 Documentation

- **[Quick Start Guide](poc/QUICKSTART.md)** - 5-minute setup
- **[Docker Guide](poc/DOCKER_QUICKSTART.md)** - Docker in 2 minutes
- **[Complete Documentation](poc/README.md)** - Full reference
- **[API Reference](poc/FINAL_SUMMARY.md)** - All features

---

## 🐳 Docker Deployment

### Option 1: Quick Start (Recommended)
```bash
cd poc
make setup
```

### Option 2: Manual Setup
```bash
# Start Ollama
docker-compose up -d ollama

# Pull a model
docker exec -it ai-monitoring-ollama ollama pull llama2

# Run example
docker exec -it ai-monitoring-poc python local_example.py
```

### Option 3: Full Stack (with UI)
```bash
docker-compose --profile localai --profile ui up -d
```

Access:
- **Ollama**: http://localhost:11434
- **LocalAI**: http://localhost:8080
- **SQLite UI**: http://localhost:8081

---

## 💡 Usage Examples

### Example 1: Monitor Local LLM (Free!)
```python
import asyncio
from local_collector import OllamaCollector
from processor import EventProcessor
from storage import EventStorage

async def handle_event(event):
    processor = EventProcessor()
    storage = EventStorage()

    # Process and store
    event = processor.process_event(event)
    storage.store_event(event)

    # Alert on security issues
    if event.has_pii:
        print(f"⚠️ PII detected in {event.model}")

    storage.close()

async def main():
    # No API key needed!
    collector = OllamaCollector(
        base_url="http://localhost:11434",
        event_handler=handle_event
    )

    result = await collector.generate(
        model="llama2",
        prompt="Explain AI safety"
    )

    print(result['response'])

asyncio.run(main())
```

### Example 2: Monitor OpenAI with Cost Tracking
```python
from openai import OpenAI
from collector import OpenAICollector
from analyzer import AnomalyDetector

client = OpenAI()
detector = AnomalyDetector()

async def handle_event(event):
    # Detect anomalies
    anomalies = detector.analyze_event(event, [])

    for anomaly in anomalies:
        if anomaly.anomaly_type == 'high_cost':
            print(f"💰 High cost alert: ${event.cost_usd}")

monitored = OpenAICollector(client, event_handler=handle_event)

# Use normally - costs tracked automatically
response = monitored.client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Example 3: Multi-Provider Comparison
```bash
# Compare all available providers
python test_all_llms.py
```

Output:
```
LLM Provider Comparison
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Provider ┃ Model      ┃ Status ┃ Latency ┃ Tokens┃ Cost   ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ ollama   │ llama2     │   ✓    │  1234ms │   142 │ $0.0000│
│ openai   │ gpt-3.5    │   ✓    │   456ms │   128 │ $0.0002│
│ anthropic│ claude-3   │   ✓    │   789ms │   156 │ $0.0003│
└──────────┴────────────┴────────┴─────────┴───────┴────────┘
```

---

## 🛠️ Makefile Commands

```bash
# Setup & Start
make setup           # Interactive setup (START HERE!)
make up              # Start services
make up-full         # Start with LocalAI + UI

# Testing
make test            # Run example
make cli             # Open dashboard
make stats           # Show statistics

# Models (Ollama)
make pull-llama2     # Download llama2 (3.8GB)
make pull-tinyllama  # Download tinyllama (637MB, fast)
make pull-mistral    # Download mistral (4.1GB, best)
make list-models     # List downloaded models

# Management
make logs            # View logs
make shell           # Enter container
make down            # Stop all services
make clean           # Clean up (keep data)
make clean-all       # Clean everything (delete data!)

# Utilities
make backup          # Backup database
make help            # Show all commands
```

---

## 📊 Detected Anomalies

| Anomaly Type | Threshold | Severity | Auto Action |
|--------------|-----------|----------|-------------|
| High Cost | > $0.50/request | HIGH | Alert |
| Cost Spike | 3x average | HIGH | Alert + Log |
| High Latency | > 5000ms | MEDIUM | Monitor |
| Latency Spike | 3x average | MEDIUM | Monitor |
| Prompt Injection | Pattern match | **CRITICAL** | **Block + Alert** |
| PII Detected | Regex match | HIGH | Alert + Flag |
| High Error Rate | > 10% | **CRITICAL** | Alert |
| High Token Usage | > 8000 tokens | MEDIUM | Review |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AI Applications                      │
│  (OpenAI, Anthropic, Ollama, LM Studio, LocalAI)        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Collectors Layer                      │
│  • OpenAICollector    • AnthropicCollector              │
│  • OllamaCollector    • LMStudioCollector               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Processing Layer                       │
│  • EventProcessor  (PII, Injection Detection)           │
│  • EventAggregator (Metrics Calculation)                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Analysis Layer                        │
│  • AnomalyDetector (Threshold + Spike Detection)        │
│  • RiskScorer      (Multi-factor Assessment)            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│  • EventStorage    (SQLite Database)                    │
│  • Indexed Queries (Fast Retrieval)                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│  • CLI Dashboard   • Statistics Reports                 │
│  • Real-time Alerts • Export Capabilities               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Local LLM endpoints (NO API KEYS NEEDED!)
OLLAMA_HOST=http://localhost:11434
LM_STUDIO_HOST=http://localhost:1234
LOCALAI_HOST=http://localhost:8080

# Cloud APIs (optional)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Settings
DATABASE_PATH=ai_monitoring.db
DEFAULT_USER_ID=local_user
LOG_LEVEL=INFO
```

### Anomaly Detection Config
```python
detector = AnomalyDetector(config={
    'cost_threshold_usd': 0.5,
    'latency_threshold_ms': 5000,
    'error_rate_threshold': 0.1,
    'token_threshold': 8000,
    'spike_multiplier': 3.0
})
```

---

## 📈 Roadmap

### ✅ Current (POC)
- [x] Multi-provider support (OpenAI, Anthropic, Ollama, etc.)
- [x] Real-time monitoring
- [x] PII & injection detection
- [x] Cost tracking
- [x] SQLite storage
- [x] CLI dashboard
- [x] Docker deployment

### 🚧 Next Phase
- [ ] Elasticsearch for scalable storage
- [ ] Kafka for event streaming
- [ ] ML-based anomaly detection
- [ ] Web dashboard (Grafana/Streamlit)
- [ ] Slack/PagerDuty integration
- [ ] GDPR compliance checks
- [ ] Distributed tracing
- [ ] Kubernetes deployment

### 🔮 Future
- [ ] Predictive analytics
- [ ] Auto-remediation
- [ ] Multi-tenant support
- [ ] SaaS offering

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: [poc/README.md](poc/README.md)
- **Quick Start**: [poc/QUICKSTART.md](poc/QUICKSTART.md)
- **Docker Guide**: [poc/DOCKER_README.md](poc/DOCKER_README.md)
- **Issues**: [GitHub Issues](https://github.com/krzysztofgryga/AI_SIEM/issues)

---

## 🙏 Acknowledgments

- **Ollama** - Amazing local LLM runtime
- **LM Studio** - Great local LLM UI
- **LocalAI** - OpenAI-compatible local server
- **Rich** - Beautiful terminal output
- **Pydantic** - Data validation

---

## ⭐ Star History

If this project helped you, please consider giving it a star! ⭐

---

**Built with ❤️ for AI safety and transparency**

🚀 **Get started now**: `cd poc && make setup`
