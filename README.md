# KITT Protocol

> Language-neutral schemas and lightweight SDKs for cross-product communication across the KITT ecosystem.

Canonical JSON Schemas define external contracts, supported by tiny, dependency-free SDKs for **Rust**, **Python**, and **TypeScript**.

---

## 🎯 Design Goals

- **Versioned Envelopes**: Structured message format with explicit semantic versions (`version: 1`).
- **Transport Agnostic**: Works over loopback TCP, NDJSON, Unix domain sockets, or named pipes.
- **Bounded Framing**: Strict 1 MiB frame limit prevents memory exhaustion.
- **Zero Heavy Dependencies**: SDKs contain minimal serialization and validation primitives only.
- **Security by Design**: Token authentication headers, constant-time token comparison, and no plain-text credentials in event payloads.

---

## 📦 Protocol v1 Message Kinds

All inter-process messages wrap payloads inside the standard envelope:

| Domain | Request Kind | Response Kind | Purpose |
|---|---|---|---|
| **System** | `system.ping.request` | `system.ping.response` / `system.error` | Health checks and errors |
| **Assistant** | `assistant.ask.request`<br>`assistant.ask_routed.request` | `assistant.ask.response`<br>`assistant.ask_routed.response` | Single / Fast-Heavy routed queries |
| **Transcription** | `assistant.transcribe.request` | `assistant.transcribe.response` | Audio file transcription |
| **Memory** | `memory.remember.request`<br>`memory.recall.request`<br>`memory.forget.request` | `memory.remember.response`<br>`memory.recall.response`<br>`memory.forget.response` | Shared structured memory storage |
| **HUD** | `hud.subscribe.request`<br>`hud.image.request` | `hud.subscribe.response`<br>`hud.image.response`<br>`hud.event` | Ephemeral desktop overlay events |
| **Workers** | `worker.execute.request` | `worker.execute.response` | On-demand ML worker tasks |
| **Settings** | `settings.catalog.request`<br>`settings.snapshot.request`<br>`settings.validate.request`<br>`settings.apply.request`<br>`settings.health.request` | `settings.catalog.response`<br>`settings.snapshot.response`<br>`settings.validate.response`<br>`settings.apply.response`<br>`settings.health.response` | KITT Control Center lifecycle |

---

## 🛠️ SDK Usage

### Rust
```rust
use kitt_protocol::{Envelope, HudEvent, PROTOCOL_VERSION, kinds};

let event = HudEvent::Text {
    content: "Response text".into(),
    ttl_ms: 5000,
};
let envelope = Envelope::new(kinds::HUD_EVENT, event)?;
```

### Python
```python
from kitt_protocol.models import Envelope, MemoryRecordDto, MEMORY_RECALL_REQUEST

envelope = Envelope(
    kind=MEMORY_RECALL_REQUEST,
    payload={"namespace": "agent-cli", "workspace_id": "ws1", "text": "rule"},
)
```

### TypeScript
```typescript
import { Envelope, HudEvent, KINDS } from "@kitt/protocol";

const event: HudEvent = { type: "text", content: "Hello", ttl_ms: 3000 };
const envelope: Envelope<HudEvent> = {
  version: 1,
  id: "550e8400-e29b-41d4-a716-446655440000",
  kind: KINDS.HUD_EVENT,
  payload: event,
};
```

---

## 🧪 Testing & Validation

```bash
# Rust core & tests
cargo fmt --all -- --check
cargo test --all

# TypeScript SDK & Fixture Validation
npm install
npm test
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE).
