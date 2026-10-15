# Protocol 0.14.0 — JSON Agent contract v5

The active model wire format is one JSON object, declared by `X-Kitt-Agent-Contract: v5`. The existing authoritative Agent response schema retains its six fields and host validation semantics. Structured final data lives in `content`; tool requests use `action: use_tool`, an exact host tool name and an object `tool_input`.

KAP parsers, encoders, fixtures and grammar tests remain archived in this repository. They are no longer imported or exported by either SDK's active root entrypoint. Historical research can import `kitt_protocol.kap`, `kitt_protocol.kap2`, `kitt_protocol.kap_version`, or the explicit TypeScript source modules. Applications neither negotiate nor emit KAP.

This is a coordinated breaking wire migration; update the ecosystem together. No new dependencies.
