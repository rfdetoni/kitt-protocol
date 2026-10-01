# Changelog

## 0.6.0 - 2026-10-01

- Add progressive Memory protocol messages: `memory.search`, `memory.timeline` and `memory.get`, with explicit token budgets instead of fixed-count recall as the primary sizing control.
- Add shared conversation-runtime binding, context reconciliation, execution-resource and tool-execution receipt contracts for durable replay/idempotency.
- Align Python agentic enums with the existing Rust/TypeScript event durability, runtime backend, isolation and evidence-origin contracts.
- Keep transport Envelope protocol v1 and ContextEnvelope schema v1; this is a package/source-contract evolution.


## 0.5.2 - 2026-09-30

- Add shared `KittRequestMetadata` across Rust, Python and TypeScript SDKs.
- Make conversation/turn/request/route correlation an explicit cross-component value contract instead of an ad-hoc Agent/Proxy payload.
- Keep Envelope protocol v1 and ContextEnvelope schema v1 unchanged.

## 0.5.2 - 2026-09-30

- Add shared `AgentRole` and `MemoryLifecycleEvent` contracts across Rust, Python and TypeScript SDKs.
- Restore TypeScript parity for saved granular permissions and plugin capability declarations.
- Keep Envelope protocol v1 unchanged; this patch release aligns the agentic source contracts used by Agent CLI 0.80.1 and Memory 0.6.1.

## 0.5.0 - 2026-09-30

- Add typed `ContextEnvelope` / `ContextSegment` contracts with trust, lifecycle, recovery and cache semantics.
- Add shared agent-event, execution-budget, authority-snapshot, context-epoch, compaction, lineage, snapshot, permissions and plugin-capability contracts.
- Add durable-memory job and consumption-receipt contracts.
- Add Rust/Python/TypeScript contract parity and round-trip validation coverage.
- Keep transport Envelope protocol v1; 0.5.0 is a package/source-contract release.

## 0.4.0 - 2026-09-28

- Add `memory.manage.request/response` for the dedicated kitt-memory service control plane.
- Keep protocol Envelope v1 unchanged.
- Define a bounded generic management payload used for memory status, evidence, dream-run, maintenance and administrative operations.
- Preserve normal remember/recall/forget messages for the hot path.


## 0.3.0 - 2026-09-28

- Add semantic cross-component contracts for resource references, evidence, capability negotiation and typed effect classes.
- Add generic ChangeSet primitives for auditable memory, surface, backend, configuration and repository changes.
- Add KITT Surface v1 contracts for declarative multi-renderer UI, patches, actions and renderer capabilities.
- Add KITT Backend IR v1 contracts for typed backend resources and validated plans.
- Keep transport Envelope protocol v1; the 0.3 line is a package/source-contract release, not a framing reset.
- Add canonical JSON Schemas and Rust/Python/TypeScript SDK parity for the new contracts.


## 0.2.1 - 2026-09-27

- Align the Python SDK support floor with the ecosystem's single supported/validated interpreter, Python 3.14.
- Keep envelope protocol v1 and all 0.2.0 memory payload semantics unchanged.
- Bump Rust, Python and TypeScript package versions together so cross-language package metadata remains coherent.


## 0.2.0 - 2026-09-27

- Extend protocol-v1 memory requests with optional conversation `scope_key`.
- Add optional point-in-time `as_of` recall without changing the envelope protocol version.
- Expose optional `scope_key` on recalled memory DTOs across Rust, Python and TypeScript SDKs.
- Add cross-language fixtures for conversation-scoped remember/recall contracts.
- Bump SDK/package versions together because Rust struct-literal consumers require source updates.

## 0.1.0 - Unreleased

- Initial KITT ecosystem foundation.
