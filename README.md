# KITT Protocol

> Language-neutral schemas and lightweight SDKs for cross-product communication across the KITT ecosystem.

Canonical JSON Schemas define the external contracts, supported by tiny, dependency-free SDKs for **Rust**, **Python**, and **TypeScript**.

---

## 🎯 Design Goals

- **Versioned Envelopes**: Structured message format with explicit semantic versions.
- **Transport Agnostic**: Works over loopback TCP, NDJSON, Unix domain sockets, or named pipes.
- **Backward Compatibility**: Additive schema fields without breaking changes.
- **Zero Heavy Dependencies**: SDKs contain minimal serialization and validation primitives only.
- **Security by Design**: Token authentication headers and no plain-text credentials in event payloads.

---

## 📦 Protocol v1 Specification

All inter-process messages wrap payloads inside the standard envelope:

```json
{
  "version": 1,
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "kind": "assistant.ask",
  "payload": {
    "text": "Olá, KITT",
    "show_hud": true
  }
}
```

### JSON Schemas

Located in [`schemas/`](schemas/):
- [`envelope.schema.json`](schemas/envelope.schema.json): Standard message container.
- [`memory.schema.json`](schemas/memory.schema.json): Memory record structure, sensitivity scopes, and recall parameters.
- [`hud-event.schema.json`](schemas/hud-event.schema.json): Ephemeral HUD status, text response, and image display events.

---

## 🛠️ SDK Usage

### Rust
```rust
use kitt_protocol::{Envelope, HudEvent, PROTOCOL_VERSION};

let event = HudEvent::Text {
    content: "Response text".into(),
    ttl_ms: 5000,
};
let envelope = Envelope::new("hud.event", event)?;
```

### Python
```python
from kitt_protocol.models import Envelope, MemoryDto

dto = MemoryDto(id="mem_1", namespace="agent-cli", workspace_id="ws1", kind="PROJECT_RULE", content="Clean diffs")
env = Envelope(kind="memory.record", payload=dto.to_dict())
```

### TypeScript
```typescript
import { Envelope, HudEvent } from "@kitt/protocol";

const event: HudEvent = { type: "text", content: "Hello", ttl_ms: 3000 };
```

---

## 🧪 Testing & Validation

```bash
# Rust core
cargo test

# Python SDK
python -m unittest discover sdk/python/tests

# TypeScript SDK
npm install
npm test
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE).
