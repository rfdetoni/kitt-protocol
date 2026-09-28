# Changelog

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
