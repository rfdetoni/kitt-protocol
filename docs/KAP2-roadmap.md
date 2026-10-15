> ARCHIVED: KAP is retained for research only. The active ecosystem uses JSON Agent contract v5. See [0.14.0](RELEASE_0.14.0.md).

# KAP/2 roadmap — proposals, not activated

This RFC describes syntax proposals that require explicit host support, capability negotiation and end-to-end approval. None of these proposals is executable in Protocol 0.13.0.

## Final modes

Separate structured `K2 F` from plain-text `K2 FT` to eliminate inference from first line. Migrate existing prompts and stored transcripts with version negotiation.

## Read-only batch

```text
K2 B
calls[2]{id,operation,path}:
  a,repo.read,README.md
  b,repo.read,pom.xml
K2/END
```

Only explicitly allowed read-only commands; each call has an independently checked schema and identifier with a matching ToolExecutionReceipt. Bound concurrency and result size. No writes in batches.

## Negotiation

Use explicit X-Kitt-KAP request metadata or a versioned K2/n header. Unknown extensions are rejected until a session explicitly negotiates them. An Agent contract v5 must be coordinated with the reverse-proxy and CLI.

## References and patches

Opaque host-scoped references should include file hash, revision, tenant/workspace scope and validity period. Patch operations require expected hash and transaction receipts, rather than trusting a model-provided path.

## Positional arguments and plans

Positional fields are allowed only with a unique host schema, order and schema digest. Differential plans use immutable revisions and optimistic concurrency to prevent stale updates.

## Streaming

The host can finish logical K2 output when a fully validated top-level terminator is observed, while preserving streaming watchdog, abort behavior and operation idempotency.

These changes require a security review, test fixtures, and cross-module releases before activation.