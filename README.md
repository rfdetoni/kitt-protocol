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

Protocol **0.6.0** keeps Envelope protocol v1 and completes the shared contracts required by the agentic runtime. Memory now has progressive `search/timeline/get` messages with explicit token budgets; conversation runtime bindings, context-segment reconciliation and tool-execution receipts are shared value contracts rather than Agent-local DTOs. `KittRequestMetadata`, typed ContextEnvelope data, tools and correlation remain structural rather than prompt-derived.

---

## Agentic 0.6 additions

- `MemorySearchRequest` returns bounded snippets/candidates first; `MemoryGetRequest` hydrates selected records under its own budget; `MemoryTimelineRequest` provides source/session chronology without overloading semantic search.
- `ToolExecutionReceipt` gives replay/reconnect a stable execution identity for side-effecting calls.
- `ConversationRuntimeBinding` represents per-conversation LOCAL/DOCKER/PODMAN/KUBERNETES/REMOTE ownership without making a global environment variable authoritative.
- `ContextSegmentReconciliation` records UNCHANGED/RECONCILED/REPLACED/INVALIDATED decisions between context epochs.

## Agentic 0.6 additions

- `MemorySearchRequest` returns bounded snippets/candidates first; `MemoryGetRequest` hydrates selected records under its own token budget; `MemoryTimelineRequest` provides source/session chronology without overloading semantic search.
- `ToolExecutionReceipt` gives replay/reconnect a stable execution identity for side-effecting calls.
- `ConversationRuntimeBinding` represents per-conversation LOCAL/DOCKER/PODMAN/KUBERNETES/REMOTE ownership without making a global environment variable authoritative.
- `ContextSegmentReconciliation` records UNCHANGED/RECONCILED/REPLACED/INVALIDATED decisions between context epochs.

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



## Memory service control plane (0.4)

The memory hot path remains `memory.remember`, `memory.recall` and `memory.forget`. Package 0.4 adds `memory.manage.request/response` for operations owned by the dedicated memory service, such as status changes, evidence/provenance, dream commits, maintenance and bounded administrative reads. The operation name is interpreted only by a trusted kitt-memory service; callers cannot use it as an arbitrary command execution channel.

## Agentic contracts 0.5

Package 0.5.0 adds the shared contracts used by the agentic control plane without changing Envelope protocol v1. The protocol repository owns data shapes only; orchestration remains in \`kitt-agent-cli\`, durable memory remains in \`kitt-memoryd\`, provider/WebChat transport remains in \`kitt-reverse-proxy\`, and low-level execution remains runtime/toolbox-owned.

### Typed context

\`ContextEnvelope\` replaces semantic rediscovery from textual headings. Every \`ContextSegment\` declares its kind, source, trust level, stability, recovery mode, cache region, lifecycle, provenance digest and token cost. Providers may still receive text after lowering, but the lowering starts from typed segments rather than parsing labels such as \`Memory:\`, \`Repo Map:\` or \`Tool Contract:\`.

Core context kinds include user intent, durable-memory recall, skills, project guidance, repository/file/search evidence, tool schemas/results/receipts, subagent output, validation/error evidence, compaction checkpoints and output contracts.

### Durable execution contracts

The package also defines language-neutral shapes for:

- \`AgentEvent\` and event durability;
- \`ExecutionBudget\` and child \`BudgetLease\`;
- immutable \`ExecutionAuthoritySnapshot\`;
- \`ContextEpoch\` and segment reconciliation;
- \`ContextRecoveryRef\` and recoverable compaction checkpoints;
- \`AgentLineage\`, isolation mode and workspace snapshots;
- saved granular permissions and plugin capabilities;
- memory jobs and \`MemoryConsumptionReceipt\`.

### Language decision

| Component | Language | Reason | Boundary |
| --- | --- | --- | --- |
| Canonical contract/validation | Rust | deterministic serialization, strict enums and low-overhead cross-service validation | JSON / protocol SDK |
| Agent orchestration SDK | Python | ergonomic control-plane integration; not a CPU hot path | same JSON mapping |
| Web/provider SDK | TypeScript | native fit for the reverse-proxy transport layer | same JSON mapping |

No domain authority is duplicated in the SDKs: Rust, Python and TypeScript represent the same wire semantics. Performance-sensitive implementations belong to their owning services and require representative benchmarks before a Python→Rust rewrite.
