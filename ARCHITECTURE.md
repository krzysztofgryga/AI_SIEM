# Architecture Documentation - AI SIEM

## 🏗️ Overview

AI SIEM uses a **3-layer modular architecture** with centralized request routing through an MPC (Multi-Provider Coordinator) Server.

**Key Principle**: **NO DIRECT INGEST** - all AI requests must go through the MPC gateway for security, monitoring, and cost optimization.

---

## 📐 Three-Layer Architecture

```
Application Layer  →  Collection Layer (MPC)  →  Processing Layer
     (Client)              (Gateway)                (Backends)
```

### Why No Direct Ingest?

**Problems with Direct Ingest (OLD)**:
- ❌ No centralized security control
- ❌ No PII detection before sending to cloud
- ❌ No cost optimization
- ❌ No audit trail
- ❌ Tight coupling to specific LLM providers

**Benefits of Gateway Architecture (NEW)**:
- ✅ Centralized authentication & authorization
- ✅ PII detection & smart routing
- ✅ Cost optimization through intelligent backend selection
- ✅ Complete audit logging
- ✅ Easy to add new backends

---

For complete architecture documentation, see component READMEs:
- [Application Layer](components/application-layer/README.md)
- [Collection Layer](components/collection-layer/README.md)
- [Processing Layer](components/processing-layer/README.md)
- [Storage Layer](components/storage-layer/README.md)
- [Security](components/security/README.md)
