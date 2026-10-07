# kitt-protocol 0.9.2 — Provider argument limit contract

Python and TypeScript SDKs export MAX_TOOL_ARGUMENT_BYTES (65,536 bytes). The limit includes the serialized JSON and UTF-8 escaping. Producers reject larger tool arguments before dispatch, and consumers enforce the same boundary. Envelope protocol versions and memory schemas are unchanged.

## Verification

Regression checks cover the concrete bugs fixed by this release. Native changes are validated with Rust formatting, Clippy, workspace tests and a Python 3.14 wheel integration. Live provider accounts and STT model inference are not part of these local checks.
