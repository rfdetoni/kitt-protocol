# KAP/1 — KITT Action Protocol

KAP is the **model-facing textual syntax** for the Agent contract v4. JSON is still the internal HTTP/OpenAI and host event representation, produced by trusted code. Never treat KAP as authorization.

Each reply is exactly one envelope (optional single ```kap code fence, no prose before or after):

```text
KITT/1
ACTION TOOL
TOOL kitt_runtime
STRING operation = repo.read
STRING arguments.path = src/app.ts
INTEGER arguments.start_line = 1
KITT/END
```

Or a final response:

```text
KITT/1
ACTION FINAL
TEXT content
Work completed, validation performed.
KITT/ENDTEXT
KITT/END
```

**Grammar:** One ACTION (TOOL, FINAL, WORKSPACE, TOOLS). TOOL requires a declared tool name. Typed path operations: STRING path = value; INTEGER path = signed integer; BOOLEAN path = true/false; DECIMAL path = finite decimal; NULL path; ARRAY path; OBJECT path; TEXT path followed by exact multiline content until a standalone KITT/ENDTEXT. Paths are dot-separated keys and decimal array indices, no escaping. Use ARRAY for empty arrays and OBJECT for empty objects, and then assign children with indexed or dotted paths. TOOL fields describe its tool_input object; non-tool fields must be rooted under content. Optional SUMMARY line is a short public progress description, never private reasoning. A reply ends only at KITT/END.

For example, structured final data uses OBJECT content and STRING content.verdict = OK. Planning arrays use ARRAY content.items, OBJECT content.items.0, STRING content.items.0.local_id = T01, and so on. Code/edit payloads use TEXT arguments.content to avoid serializing newlines, quotes and backslashes.

**Limits and security:** 64 KiB UTF-8 per response; max 3000 lines, maximum 20 path segments and index 1024. Duplicate keys, conflicting types, sparse arrays, dangerous object keys, extra prose or multiple envelopes are errors. Body containing a standalone KITT/ENDTEXT cannot be represented in this version: reject and split the tool edit into smaller actions; do not guess or execute a partial action. Host re-validates tool schemas, allowed operations, path policies, approvals and completion evidence independently. Repair must not change an already identified action/tool or valid data.

**Operational expectation:** Model emits KAP text. Reverse-proxy parses to internal typed objects and native tool calls, and can return JSON over HTTP (host-generated), so existing backend/event machinery does not become an LLM output contract.
