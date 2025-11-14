# 🤖 AI Agent Security Monitoring Platform

[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/architecture-3--layer-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Modular, enterprise-grade monitoring and security system for AI agents and LLMs.**

Complete 3-layer architecture with centralized routing, PII detection, cost optimization, and audit logging:
- 🏗️ **3-Layer Architecture**: Application → Collection → Processing
- 🔒 **Enterprise Security**: JWT auth, PII detection, RBAC, audit logs
- 💰 **Cost Optimization**: Intelligent routing, rule engines, cascade strategies
- 📊 **Full Observability**: Anomaly detection, metrics, dashboards
- 🎯 **No Direct Ingest**: All requests through centralized MPC gateway

---

## ⚡ Quick Start (5 Minutes)

```bash
# Clone repository
git clone https://github.com/krzysztofgryga/AI_SIEM.git
cd AI_SIEM

# Install dependencies
pip install -r requirements.txt

# Run basic example
python examples/basic_usage.py
```

**That's it!** 🎉 You've just:
- ✅ Created an MPC client
- ✅ Sent a query through the gateway
- ✅ Got a secure, monitored response

View more examples:
```bash
python examples/secure_usage.py       # Security features
python examples/batch_processing.py   # Batch processing
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR APPLICATIONS                           │
│  (Web apps, APIs, CLI tools, microservices)                    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                              │
│                                                                 │
│  components/application-layer/                                 │
│  ├── client.py              (MPCClient, SimpleMPCClient)       │
│  └── example_usage.py       (Usage examples)                   │
│                                                                 │
│  Provides client interface for applications                    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  COLLECTION LAYER (MPC Server)                  │
│                                                                 │
│  components/collection-layer/                                  │
│  ├── server.py              (MPC Server - main orchestrator)   │
│  └── router.py              (Intelligent routing)              │
│                                                                 │
│  ✓ Request validation                                          │
│  ✓ Authentication (JWT) & Authorization (RBAC)                 │
│  ✓ PII detection & routing                                     │
│  ✓ Intelligent backend selection                               │
│  ✓ Cost & latency optimization                                 │
│  ✓ Audit logging                                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
         ┌──────────────────────────────────────┐
         │   PROCESSING LAYER                   │
         │                                      │
         │   components/processing-layer/       │
         │   └── backends.py                    │
         │                                      │
         │   ┌─────────────────────────────┐   │
         │   │  Rule Engines               │   │
         │   │  • Classification           │   │
         │   │  • Extraction               │   │
         │   │  • Validation               │   │
         │   │  Cost: $0, Latency: <10ms   │   │
         │   └─────────────────────────────┘   │
         │                                      │
         │   ┌─────────────────────────────┐   │
         │   │  LLM Backends               │   │
         │   │  • OpenAI (GPT-3.5, GPT-4)  │   │
         │   │  • Anthropic (Claude)       │   │
         │   │  • Google (Gemini)          │   │
         │   │  • Local (Ollama, LM Studio)│   │
         │   └─────────────────────────────┘   │
         │                                      │
         └──────────────────────────────────────┘
                           │
                           ▼
         ┌──────────────────────────────────────┐
         │   STORAGE & ANALYSIS LAYER           │
         │                                      │
         │   components/storage-layer/          │
         │   ├── storage.py  (EventStorage)     │
         │   └── analyzer.py (AnomalyDetector)  │
         │                                      │
         │   ✓ Event persistence (SQLite)       │
         │   ✓ Anomaly detection                │
         │   ✓ Metrics aggregation              │
         │   ✓ Reports & analytics              │
         └──────────────────────────────────────┘
                           │
                           ▼
         ┌──────────────────────────────────────┐
         │   TOOLS & DASHBOARDS                 │
         │                                      │
         │   tools/                             │
         │   └── cli.py  (CLI Dashboard)        │
         │                                      │
         │   ✓ Real-time monitoring             │
         │   ✓ Statistics & reports             │
         │   ✓ Event browsing                   │
         └──────────────────────────────────────┘
```

### 🔑 Key Difference: No Direct Ingest

**❌ OLD (Direct Ingest - REMOVED):**
```python
# Application directly wraps LLM client
client = OpenAI()
monitored = OpenAICollector(client)  # ❌ Direct ingest
response = monitored.client.chat.completions.create(...)
```

**✅ NEW (Centralized Gateway):**
```python
# Application uses MPC Client → everything goes through gateway
client = SimpleMPCClient()  # ✅ Through gateway
response = await client.ask("Question")
# → MPC Server validates, authenticates, routes, audits
```

---

## 🌟 Features

### 🔐 Enterprise Security

#### Authentication & Authorization
- **JWT Tokens**: Secure authentication with expiry
- **RBAC**: Role-based access control (Admin, Service, ReadOnly)
- **Permissions**: Fine-grained permission system
- **Signature Verification**: HMAC signatures for critical operations

#### PII Detection & Protection
- **Automatic Detection**: Email, phone, SSN, credit cards, IP addresses
- **Smart Routing**: PII data automatically routed to on-prem backends only
- **Redaction**: Multiple strategies (MASK, TOKENIZE, REMOVE)
- **Compliance**: GDPR-ready with full audit trails

#### Audit Logging
- **Complete Audit Trail**: Every request logged with full context
- **Security Violations**: Tracking of all security events
- **Performance Metrics**: Latency, cost, tokens for every request
- **Export**: JSON/CSV export for compliance reporting

### 💰 Cost Optimization

#### Intelligent Routing
- **Rule Engines First**: Free processing for simple tasks
- **Cost-Aware Selection**: Choose cheapest backend meeting requirements
- **Cascade Strategy**: Try cheap → expensive with confidence thresholds
- **Budget Controls**: Per-client cost limits and quotas

#### Processing Hints
```python
# Developer controls cost vs quality
ProcessingHint.RULE_ENGINE   # $0, fast, deterministic
ProcessingHint.MODEL_SMALL   # $, good quality
ProcessingHint.MODEL_LARGE   # $$$, best quality
ProcessingHint.HYBRID        # Smart mix
ProcessingHint.AUTO          # System decides
```

### 📊 Observability & Analytics

#### Anomaly Detection
- **Real-time**: Detect issues as they happen
- **Multi-level**: Event-level + pattern-level detection
- **Configurable**: Custom thresholds and rules
- **Actionable**: Recommended actions for each anomaly type

Detected anomalies:
- Cost spikes (3x average)
- Latency spikes (3x average)
- High error rates (>10%)
- Security violations (PII leaks, injection attempts)
- Resource exhaustion

#### Metrics & Dashboards
- **CLI Dashboard**: Rich terminal UI with tables and charts
- **Real-time Stats**: Success rate, latency, cost, tokens
- **Breakdowns**: By provider, model, user, time window
- **Export**: JSON, CSV for external analysis

---

## 📁 Project Structure

```
AI_SIEM/
│
├── components/                          # Modular components
│   ├── application-layer/              # Client interface
│   │   ├── client.py                   # MPCClient, SimpleMPCClient
│   │   ├── example_usage.py            # Usage examples
│   │   ├── README.md                   # Documentation
│   │   └── requirements.txt            # Dependencies
│   │
│   ├── collection-layer/               # MPC Server (gateway)
│   │   ├── server.py                   # Main server
│   │   ├── router.py                   # Intelligent routing
│   │   ├── README.md                   # Documentation
│   │   └── requirements.txt            # Dependencies
│   │
│   ├── processing-layer/               # Processing backends
│   │   ├── backends.py                 # Backend implementations
│   │   ├── README.md                   # Documentation
│   │   └── requirements.txt            # Dependencies
│   │
│   ├── storage-layer/                  # Data persistence
│   │   ├── storage.py                  # EventStorage
│   │   ├── analyzer.py                 # AnomalyDetector
│   │   ├── README.md                   # Documentation
│   │   └── requirements.txt            # Dependencies
│   │
│   └── security/                       # Security components
│       ├── auth.py                     # JWT, RBAC
│       ├── pii_handler.py              # PII detection/redaction
│       ├── audit.py                    # Audit logging
│       ├── README.md                   # Documentation
│       └── requirements.txt            # Dependencies
│
├── shared/                              # Shared modules
│   ├── schemas/                        # JSON-RPC contracts
│   │   └── contracts.py
│   └── models.py                       # Data models
│
├── tools/                               # CLI & utilities
│   ├── cli.py                          # Dashboard
│   ├── README.md                       # Documentation
│   └── requirements.txt                # Dependencies
│
├── examples/                            # Usage examples
│   ├── basic_usage.py                  # Simple example
│   ├── secure_usage.py                 # Security features
│   ├── batch_processing.py             # Batch processing
│   └── README.md                       # Examples documentation
│
├── README.md                            # This file
└── requirements.txt                     # All dependencies
```

### 📖 Component Documentation

Each component has detailed README:
- **[Application Layer](components/application-layer/README.md)** - Client API
- **[Collection Layer](components/collection-layer/README.md)** - MPC Server
- **[Processing Layer](components/processing-layer/README.md)** - Backends
- **[Storage Layer](components/storage-layer/README.md)** - Persistence & analytics
- **[Security](components/security/README.md)** - Auth, PII, audit
- **[Tools](tools/README.md)** - CLI dashboard
- **[Examples](examples/README.md)** - Usage examples

---

## 💡 Usage Examples

### Example 1: Basic Usage

```python
import asyncio
from components.application_layer.client import SimpleMPCClient

async def main():
    # Create client
    client = SimpleMPCClient(auth_token="demo-token")

    # Ask a question
    response = await client.ask("What is API security?")
    print(response)

asyncio.run(main())
```

### Example 2: Secure Data Handling

```python
from components.application_layer.client import MPCClient
from shared.schemas.contracts import SensitivityLevel, ProcessingHint

async def main():
    client = MPCClient()

    # Handle PII - automatically routed to private backend
    result = await client.process(
        prompt="My email is john@example.com",
        sensitivity=SensitivityLevel.PII,
        processing_hint=ProcessingHint.MODEL_PRIVATE,
        enable_pii_detection=True
    )

    print(result['response'])
    print(f"Security flags: {result['security_flags']}")
```

### Example 3: Cost Optimization

```python
async def main():
    client = MPCClient()

    # Use rule engine (free) for simple task
    result = await client.process(
        prompt="Classify: ERROR message",
        processing_hint=ProcessingHint.RULE_ENGINE
    )
    print(f"Cost: ${result['cost']}")  # $0.0000

    # Use LLM only when needed
    result = await client.process(
        prompt="Explain the architecture of microservices",
        processing_hint=ProcessingHint.MODEL_LARGE
    )
    print(f"Cost: ${result['cost']}")  # $0.0234
```

---

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/krzysztofgryga/AI_SIEM.git
cd AI_SIEM

# Install all dependencies
pip install -r requirements.txt

# Or install per component
pip install -r components/application-layer/requirements.txt
pip install -r components/collection-layer/requirements.txt
# ...
```

### Run Examples

```bash
# Basic usage
python examples/basic_usage.py

# Secure usage (PII handling)
python examples/secure_usage.py

# Batch processing
python examples/batch_processing.py
```

### View Dashboard

```bash
# CLI dashboard
python tools/cli.py

# Or specific commands
python tools/cli.py stats      # Statistics
python tools/cli.py events 20  # Recent events
python tools/cli.py anomalies  # Anomalies
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Authentication secrets (use KMS/Vault in production)
export JWT_SECRET="your-jwt-secret-here"
export HMAC_SECRET="your-hmac-secret-here"

# Database
export DATABASE_PATH="ai_monitoring.db"

# Optional: LLM API keys (for cloud backends)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### Anomaly Detection Config

```python
from components.storage_layer.analyzer import AnomalyDetector

detector = AnomalyDetector(config={
    'cost_threshold_usd': 0.5,       # Alert when cost > $0.50
    'latency_threshold_ms': 5000,    # Alert when latency > 5s
    'error_rate_threshold': 0.1,     # Alert when errors > 10%
    'token_threshold': 8000,         # Alert when tokens > 8000
    'spike_multiplier': 3.0          # Alert when 3x higher than average
})
```

---

## 📊 CLI Dashboard

```bash
$ python tools/cli.py

╔════════════════════════════════════════╗
║   AI Monitoring Dashboard CLI          ║
╚════════════════════════════════════════╝

📊 Statistics (Last 24 Hours)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric           ┃    Value ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Events     │       47 │
│ Successful       │       45 │
│ Failed           │        2 │
│ Success Rate     │    95.7% │
│ Total Tokens     │    8,234 │
│ Total Cost       │ $0.0421  │
│ Avg Latency      │    723ms │
│ PII Events       │        3 │
│ Injection        │        1 │
│ Anomalies        │        7 │
└──────────────────┴──────────┘
```

---

## 🔒 Security Best Practices

### 1. Never Use Direct Ingest
```python
# ❌ DON'T: Direct access to LLM APIs
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(...)  # No auth, no PII check, no audit

# ✅ DO: Use MPC Client (gateway)
from components.application_layer.client import SimpleMPCClient
client = SimpleMPCClient(auth_token="...")
response = await client.ask("...")  # Authenticated, PII-checked, audited
```

### 2. Handle PII Correctly
```python
# Always detect and route PII to private backends
result = await client.process(
    prompt="Email: john@example.com",
    sensitivity=SensitivityLevel.PII,
    processing_hint=ProcessingHint.MODEL_PRIVATE,  # MUST be private!
    enable_pii_detection=True
)
```

### 3. Use Proper Authentication
```python
from components.security.auth import AccessControl

# Create tokens with appropriate permissions
ac = AccessControl(jwt_secret="...", hmac_secret="...")
token = ac.create_service_token(
    client_id="my-app",
    permissions=[Permission.READ, Permission.EXECUTE]
)

client = MPCClient(auth_token=token)
```

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific component tests
pytest components/collection-layer/
pytest components/security/
```

### Adding Custom Backend

```python
from components.processing_layer.backends import ProcessingBackend

class MyBackend(ProcessingBackend):
    def __init__(self):
        super().__init__(
            backend_id="custom:my-backend",
            name="My Custom Backend",
            capabilities=[CapabilityType.TEXT_GENERATION],
            max_sensitivity=SensitivityLevel.INTERNAL
        )

    async def process(self, prompt: str, **kwargs):
        # Your processing logic
        return {
            "response": "...",
            "tokens": 100,
            "cost": 0.001
        }

# Register
from components.processing_layer.backends import get_backend_registry
registry = get_backend_registry()
registry.register(MyBackend())
```

---

## 📈 Roadmap

### ✅ Current (v1.0)
- [x] 3-layer architecture
- [x] MPC Server gateway
- [x] JWT authentication & RBAC
- [x] PII detection & routing
- [x] Intelligent backend selection
- [x] Anomaly detection
- [x] CLI dashboard
- [x] Audit logging
- [x] **Removed direct ingest**

### 🚧 Next (v1.1)
- [ ] HTTP/REST API for MPC Server
- [ ] Web dashboard (React/Streamlit)
- [ ] Elasticsearch for scalable storage
- [ ] Kafka for event streaming
- [ ] Prometheus metrics export
- [ ] Kubernetes deployment

### 🔮 Future (v2.0)
- [ ] ML-based anomaly detection
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Multi-tenancy support
- [ ] SaaS offering
- [ ] Auto-remediation
- [ ] Predictive analytics

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the modular architecture
4. Add tests for new features
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Architecture inspiration**: Kubernetes, Istio, API Gateways
- **Security best practices**: OWASP, NIST guidelines
- **LLM providers**: OpenAI, Anthropic, Google
- **Local LLMs**: Ollama, LM Studio
- **Python libraries**: Pydantic, Rich, PyJWT

---

## 📞 Support

- **Documentation**: See component READMEs in `components/*/README.md`
- **Examples**: See `examples/README.md`
- **Issues**: [GitHub Issues](https://github.com/krzysztofgryga/AI_SIEM/issues)
- **Discussions**: [GitHub Discussions](https://github.com/krzysztofgryga/AI_SIEM/discussions)

---

**Built with ❤️ for AI safety, security, and transparency**

🚀 **Get started now**: `python examples/basic_usage.py`
