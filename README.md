# KITT Protocol

Language-neutral contracts shared by KITT products. JSON Schema is the canonical external contract; Rust/Python/TypeScript SDKs provide small convenience types.

Design goals: versioned envelopes, backward-compatible additions, no transport coupling, no secrets in payloads, and stable identifiers.

## Protocol v1

All messages use an envelope:

```json
{"version":1,"id":"...","kind":"assistant.ask","payload":{}}
```

The transport is intentionally unspecified. `kitt-assistant` v0 uses NDJSON over loopback TCP with a local auth token.

## Validation

- Rust: `cargo test`
- Python: `python -m unittest discover sdk/python/tests`
- TypeScript: `npm install && npm test` from repository root
