# K.I.T.T. Protocol

<p align="center">
  <strong>Versioned, language-neutral contracts for the K.I.T.T. ecosystem.</strong><br>
  JSON Schema · Rust · Python · TypeScript · bounded framing · transport-agnostic IPC
</p>

<p align="center">
  <a href="https://github.com/rfdetoni/kitt-protocol/blob/main/LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="Protocol v1" src="https://img.shields.io/badge/protocol-v1-6f42c1">
  <img alt="SDKs" src="https://img.shields.io/badge/SDKs-Rust%20%7C%20Python%20%7C%20TypeScript-lightgrey">
</p>

K.I.T.T. Protocol defines the external contracts used between independently packaged K.I.T.T. components. Canonical JSON Schemas are paired with small SDKs so the Agent, Assistant, Memory, workers and native services can evolve without duplicating transport logic or coupling their implementations.

---

## What’s included

- Canonical versioned message envelopes.
- JSON Schema contracts for cross-component payloads.
- Lightweight Rust, Python and TypeScript SDKs.
- Bounded framing with a strict **1 MiB** frame limit.
- Transport-neutral messages usable over loopback TCP, NDJSON, Unix sockets or named pipes.
- Authentication metadata without putting plain-text credentials into event payloads.
- Contracts for system health, assistant routing, transcription, memory, HUD, workers and Control Center settings.

---

## Quick links

- **K.I.T.T. ecosystem:** https://github.com/rfdetoni/kitt
- **Agent CLI:** https://github.com/rfdetoni/kitt-agent-cli
- **Assistant:** https://github.com/rfdetoni/kitt-assistant
- **Memory:** https://github.com/rfdetoni/kitt-memory
- **AI workers:** https://github.com/rfdetoni/kitt-ai-workers

---

## Design principles

1. **Versioned contracts.** Every envelope carries an explicit protocol version.
2. **Transport agnostic.** Schemas describe semantics, not a specific socket implementation.
3. **Bounded by default.** Frame-size limits prevent unbounded memory growth at IPC boundaries.
4. **Small SDKs.** Serialization and validation helpers stay lightweight and dependency-conscious.
5. **Security-aware.** Authentication tokens belong to transport/auth boundaries, not normal model-visible payloads.
6. **Cross-language parity.** Rust, Python and TypeScript clients should represent the same protocol semantics.

---

## Protocol v1 message kinds

| Domain | Request kind | Response/event kind | Purpose |
| --- | --- | --- | --- |
| System | `system.ping.request` | `system.ping.response`, `system.error` | health and protocol errors |
| Assistant | `assistant.ask.request`, `assistant.ask_routed.request` | `assistant.ask.response`, `assistant.ask_routed.response` | normal and Fast/Heavy routed queries |
| Transcription | `assistant.transcribe.request` | `assistant.transcribe.response` | audio transcription |
| Memory | `memory.remember.request`, `memory.recall.request`, `memory.forget.request` | corresponding memory responses | shared structured memory |
| HUD | `hud.subscribe.request`, `hud.image.request` | responses and `hud.event` | ephemeral desktop overlay events |
| Workers | `worker.execute.request` | `worker.execute.response` | on-demand worker execution |
| Settings | catalog/snapshot/validate/apply/health requests | corresponding settings responses | Control Center lifecycle |

All messages are wrapped in the standard versioned envelope rather than introducing transport-specific payload shapes.

---

## SDK usage

### Rust

```rust
use kitt_protocol::{kinds, Envelope, HudEvent};

let event = HudEvent::Text {
    content: "Response text".into(),
    ttl_ms: 5000,
};

let envelope = Envelope::new(kinds::HUD_EVENT, event)?;
```

### Python

```python
from kitt_protocol.models import Envelope, MEMORY_RECALL_REQUEST

envelope = Envelope(
    kind=MEMORY_RECALL_REQUEST,
    payload={
        "namespace": "agent-cli",
        "workspace_id": "ws1",
        "text": "rule",
    },
)
```

### TypeScript

```typescript
import { Envelope, HudEvent, KINDS } from "@kitt/protocol";

const event: HudEvent = {
  type: "text",
  content: "Hello",
  ttl_ms: 3000,
};

const envelope: Envelope<HudEvent> = {
  version: 1,
  id: "550e8400-e29b-41d4-a716-446655440000",
  kind: KINDS.HUD_EVENT,
  payload: event,
};
```

---

## Architecture

```text
K.I.T.T. component
       │
       ▼
language SDK
       │
       ▼
versioned envelope + canonical schema
       │
       ▼
TCP / NDJSON / Unix socket / named pipe
       │
       ▼
language SDK
       │
       ▼
peer component
```

Protocol code stays intentionally smaller than the services that use it. Domain behavior belongs to those services; this repository owns the shared wire contract.

---

## Security

The protocol layer is designed so callers can authenticate at the transport boundary while message payloads remain suitable for logging/redaction policies. Bounded framing rejects oversized messages before they can grow unchecked in memory.

Consumers remain responsible for authorization decisions, capability policy and secret egress rules appropriate to their component.

---

## Testing & validation

```bash
cargo fmt --all -- --check
cargo test --all

npm install
npm test
```

Cross-language fixtures should remain semantically equivalent whenever a schema or message kind changes.

---

## Contributing

Prefer additive, versioned evolution over silent wire-format changes. A protocol change should update the canonical schema, affected SDKs and compatibility tests together.

---

## K.I.T.T. ecosystem

| Repository | Responsibility |
| --- | --- |
| [`kitt`](https://github.com/rfdetoni/kitt) | installer and ecosystem composition |
| [`kitt-agent-cli`](https://github.com/rfdetoni/kitt-agent-cli) | autonomous agent control plane |
| [`kitt-reverse-proxy`](https://github.com/rfdetoni/kitt-reverse-proxy) | authorized provider gateway |
| [`kitt-memory`](https://github.com/rfdetoni/kitt-memory) | persistent memory engine |
| [`kitt-toolbox`](https://github.com/rfdetoni/kitt-toolbox) | native code/system data plane |
| [`kitt-ai-workers`](https://github.com/rfdetoni/kitt-ai-workers) | isolated AI/ML workers and evals |
| [`kitt-assistant`](https://github.com/rfdetoni/kitt-assistant) | resident assistant and Control Center |

---

## License

MIT. See [LICENSE](LICENSE).
