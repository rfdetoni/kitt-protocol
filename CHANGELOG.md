# Changelog — K.I.T.T. Protocol

## Histórico migrado do README

## Protocol 0.14.1 — Clean-Room public API contracts

Strict black-box schema and Python decoder for Wine/ReactOS behavioral handoff, independent of the existing Agent v5 JSON wire. Human review and OS isolation are separately required. [Release details](docs/RELEASE_0.14.1.md).

## Protocol 0.14.0 — JSON Agent contract v5

The active model wire format is one JSON object, declared by `X-Kitt-Agent-Contract: v5`. The existing authoritative Agent response schema retains its six fields and host validation semantics. Structured final data lives in `content`; tool requests use `action: use_tool`, an exact host tool name and an object `tool_input`.

[Release details](docs/RELEASE_0.14.0.md).

## Release 0.10.0 — Agent contract v3

Agent responses may carry structured result objects directly in content. The authoritative response schema and wire identifiers are exported to the SDKs; strict object decoding rejects duplicate fields and extra decisions. Upgrade Agent CLI and Reverse Proxy together. See [release notes](docs/RELEASE_0.10.0.md).

## Release 0.9.2 — Provider argument limit contract

Python and TypeScript SDKs export MAX_TOOL_ARGUMENT_BYTES (65,536 bytes). The limit includes the serialized JSON and UTF-8 escaping. Producers reject larger tool arguments before dispatch, and consumers enforce the same boundary. Envelope protocol versions and memory schemas are unchanged.

See [release notes](docs/RELEASE_0.9.2.md).

## Release 0.9.1 — execution boundary hardening

Reject duplicate JSON keys, non-finite numbers and invalid UTF-8 at the public wire decoders. Python requires an integer version; Rust requires the payload field (explicit null remains valid). Add shared adversarial wire fixtures and exercise the public TypeScript decoders. Wire version remains 1.

See [release notes](docs/RELEASE_0.9.1.md).

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

Protocol **0.9.0** keeps Envelope protocol v1 and extends the shared memory contract without changing framing. Memory now has progressive `search/timeline/get` messages with explicit token budgets; conversation runtime bindings, context-segment reconciliation and tool-execution receipts are shared value contracts rather than Agent-local DTOs. `KittRequestMetadata`, typed ContextEnvelope data, tools and correlation remain structural rather than prompt-derived.

---

---

## Histórico anteriormente mantido no CHANGELOG

# Protocol 0.14.0 — JSON Agent contract v5

The active model wire format is one JSON object, declared by `X-Kitt-Agent-Contract: v5`. The existing authoritative Agent response schema retains its six fields and host validation semantics. Structured final data lives in `content`; tool requests use `action: use_tool`, an exact host tool name and an object `tool_input`.

KAP parsers, encoders, fixtures and grammar tests remain archived in this repository. They are no longer imported or exported by either SDK's active root entrypoint. Historical research can import `kitt_protocol.kap`, `kitt_protocol.kap2`, `kitt_protocol.kap_version`, or the explicit TypeScript source modules. Applications neither negotiate nor emit KAP.

This is a coordinated breaking wire migration; update the ecosystem together. No new dependencies.

## 0.13.2

- Export a cross-language `X-Kitt-KAP` negotiation contract selecting only deployed `KAP/2`.
- Explicit, ambiguous or unsupported versions are rejected; absent header preserves pre-negotiation clients.
- Model grammar and host authorization are unchanged.

## 0.13.1

- Fix shared KAP2Error construction under TypeScript exactOptionalPropertyTypes, preserving optional metadata without assigning undefined.
- Verify authoritative TypeScript diagnostic class parity with the reverse-proxy consumer.

## 0.13.0

- KAP/2 additive features: JSON-quoted keys, explicit empty values, object list items, UTF-8 length-prefixed literals, optional schema-informed primitives, typed error codes/lines, summary metadata and canonical encoders in both SDKs.
- Add shared golden fixtures, seeded Python/TypeScript differential fuzz and size/depth/line-limit tests.
- Document existing v3 JSON Schema identifier alongside Agent contract v4; no unverified schema renaming.

## 0.12.2 (hardening phase, included in 0.13.0)

- **Behavior changes:** reject row tabs, unpaired surrogates, controls, BOM, trailing spaces, negative zero, stray CR and W/Q bodies. These previously accepted forms are invalid.
- Keep literal content verbatim; reject ambiguities rather than repairing output.

## 0.12.1

- Reject competing KAP/2 control frames in non-literal final text.
- Keep explicit literal blocks capable of carrying control-like text as inert data.

## 0.12.0

- Introduce compact KAP/2 grammar with bounded Python and TypeScript decoders, literal payloads and tabular records.
- Keep the trusted host responsible for tool resolution, validation and authorization. Legacy KAP/1 input remains decodable during migration.

## 0.11.0

- Add KAP/1 bounded model-facing wire format and shared TS parser.
- Increment Agent contract negotiation to v4 without changing host-owned runtime authorization.

## 0.11.0

- Introduce KAP/1 bounded textual actions for the WebChat boundary; tool permissions and JSON transport remain host-owned.
- Move Agent proxy contract negotiation to v4 without changing the validated in-process response schema.

## 0.10.0

- Own Agent contract v3 identifiers and response schema; object-valued content avoids model-side double serialization.
- Export a strict Python JSON-object decoder using the existing bounded wire decoder.
- Check SDK identifier parity and generated schema provenance in CI.

# Changelog

## 0.9.2 — 2026-10-07

Python and TypeScript SDKs export MAX_TOOL_ARGUMENT_BYTES (65,536 bytes). The limit includes the serialized JSON and UTF-8 escaping. Producers reject larger tool arguments before dispatch, and consumers enforce the same boundary. Envelope protocol versions and memory schemas are unchanged.

## 0.9.1 — 2026-10-06

- Reject duplicate JSON keys, non-finite numbers and invalid UTF-8 at the public wire decoders. Python requires an integer version; Rust requires the payload field (explicit null remains valid). Add shared adversarial wire fixtures and exercise the public TypeScript decoders. Wire version remains 1.

## 0.9.0 — 2026-10-02

- Keep Envelope protocol v1 while adding `memory.baseline.request/response` with deterministic revision/ETag reuse.
- Add optional progressive retrieval controls for provenance, session exclusions and context hints across Rust, Python and TypeScript.
- Add optional search response context-hint/common metadata while preserving existing v1 hit fields.
- Bump Rust/Python/TypeScript package metadata together to 0.9.0 and extend SDK contract tests.

## 0.8.0 — 2026-10-02

- Add optional bounded upstream attempt, end-to-end deadline and cumulative prompt grants in Rust, Python, TypeScript and JSON Schema.
- Bound context envelopes to 256 segments and export the authoritative context schema for standalone consumers.
- Preserve wire version 1 and compatibility for callers that omit the new metadata.


## 0.7.0 - 2026-10-01

- Add shared host execution facts, bounded plan proposals, task roles and subagent reports across Rust, Python and TypeScript.
- Extend request metadata with optional role, parent request and task correlation.
- Add a shared planning JSON schema, wire fixture, malformed input tests and cross-SDK field parity checks.
- Preserve transport Envelope v1, ContextEnvelope v1 and existing role names; plans and reports never confer execution authority.

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
