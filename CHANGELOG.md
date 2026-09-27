# Changelog

## 0.2.0 - 2026-09-27

- Extend protocol-v1 memory requests with optional conversation `scope_key`.
- Add optional point-in-time `as_of` recall without changing the envelope protocol version.
- Expose optional `scope_key` on recalled memory DTOs across Rust, Python and TypeScript SDKs.
- Add cross-language fixtures for conversation-scoped remember/recall contracts.
- Bump SDK/package versions together because Rust struct-literal consumers require source updates.

## 0.1.0 - Unreleased

- Initial KITT ecosystem foundation.
