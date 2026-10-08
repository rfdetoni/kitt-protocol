# kitt-protocol 0.10.0 — Agent contract v3

The Protocol repository now owns the X-Kitt-Agent-Contract v3 identifiers and Agent response schema. content accepts a text answer, a structured JSON object, or null as required by its action. Tool input remains an object. Plans and review/validation/completion reports are objects rather than serialized JSON embedded in strings.

The existing envelope protocol v1 and ContextEnvelope v1 are unchanged. Python exports decode_json_object on the existing UTF-8, duplicate-key, non-finite-number, depth and size checks. TypeScript exports generated response schema and identifiers; Rust exports matching identifiers. No legacy Agent v2 negotiation is provided; update Agent CLI and Proxy together.

Python SDK regressions reject conflicting verdict keys and extra decisions. SDK parity, generated schema checks, TypeScript and Rust CI validate the shared boundary.
