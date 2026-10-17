# Protocol 0.14.2 — immutable release and consolidated changelog

- Retain the unchanged JSON Agent v5 wire contract and strict Clean-Room black-box API schema introduced in 0.14.1.
- Synchronize Rust/Cargo, Python and TypeScript package metadata and lock versions after the 0.14.1 npm lock correction; avoid mutating immutable 0.14.1 release tags.
- Consolidate release announcements in CHANGELOG.md and keep README.md focused on SDK usage and security contracts.
- CI requires the same parser, schema, Cargo and TypeScript validation as before.
