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
- Semantic resource references, evidence and capability negotiation.
- Generic auditable ChangeSets with host-owned side-effect classification.
- KITT Surface v1 and Backend IR v1 cross-component contracts.

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


## Memory contract 0.2

Package version 0.2.1 keeps envelope protocol **v1** and extends memory payloads additively. `scope_key` identifies a conversation when `scope = "conversation"`; `as_of` enables point-in-time recall; recalled DTOs may include `scope_key`. Workspace/global callers may omit both fields.

Rust consumers must update struct literals because these additional fields are a source-level API change. The package therefore advances to 0.2.0 while the wire envelope remains protocol v1.


### Python support policy

KITT Protocol 0.2.1 declares Python **3.14+** for its Python SDK. This matches the ecosystem policy of supporting and continuously validating only the current Python interpreter rather than advertising older minors that are no longer exercised by CI. Rust/TypeScript wire semantics are unchanged.


## Semantic contracts 0.3

Package 0.3.0 introduces a semantic layer while retaining Envelope protocol v1.

### Resource namespace

Cross-component references use logical `kitt://` URIs. The URI identifies an owner and resource, but does not transfer authority between modules. Repository files remain repository-owned, shared semantic memory remains memory-owned, transient surfaces remain renderer/runtime-owned, and generated backend source remains repository-owned after application.

### Effects and ChangeSets

Every mutation-capable domain can represent proposed work as a `ChangeSet`. Effects are classified as `pure`, `read`, `write`, `destructive`, `external_side_effect` or `privileged`. Consumers MUST reclassify model-provided effects against host policy before execution.

### Surface v1

Surface contracts describe declarative components, bounded state, revisioned patches, semantic actions and renderer capabilities. A Surface is data, never executable UI code. Renderers expose allowlisted catalogs and user actions are returned to the host policy/runtime layer rather than invoking arbitrary tools.

### Backend IR v1

Backend IR represents schemas, entities, queries, commands, endpoints, events, workflows, policies, jobs and observability resources. It is an intent/plan representation, not executable code. Validation, impact analysis, approvals and compilation remain host responsibilities.

