# Protocol 0.14.1 — Clean-Room API behavior contract

Add the Draft 2020-12 black-box API schema and strict Python SDK decoder. Strict validation rejects duplicate keys, unexpected fields, oversized/Unicode-invalid input, repeated behavior IDs and obvious decompiler/assembly artifacts. No model-side repair or silent redaction is authorized. The schema is a structural gate, not proof of independent implementation or OS-level isolation. A separate human review and host-enforced process/filesystem boundary remain required before implementation.

The existing Agent contract v5 and transport are unchanged. Run python -m unittest discover -s sdk/python/tests, Rust Cargo locked checks and TypeScript fixtures in CI.
