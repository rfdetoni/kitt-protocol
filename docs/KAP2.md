# KAP/2 — compact model-facing actions

## Exact version negotiation (Protocol 0.13.2)

Agent HTTP requests may declare `X-Kitt-KAP: KAP/2`. The Proxy selects
the exact deployed version and acknowledges with `X-Kitt-KAP: KAP/2`.
Unknown versions, comma-separated lists, whitespace variants and empty
headers fail closed; there is no model-authored version negotiation and no
implicit downgrade. Missing request headers preserve compatibility with
previously deployed KAP/2 clients. This does not change HTTP JSON, KITT
Agent Contract v4, host authorization, or the grammar of `K2 T/F/W/Q`.
The current supported list contains only `KAP/2`.


KAP/2 0.13.0 is a bounded deterministic, TOON-inspired textual grammar. **The grammar never grants authority**: the host validates declared tools, parameters, approvals, identity, resource policy and completion. HTTP JSON, Rust IPC and Envelope v1 remain independent. KAP/1 remains a separate legacy format.

## Grammar (ABNF with context-dependent semantics)

~~~abnf
frame        = header LF [summary LF] [body LF] terminator
header       = "K2 " (tool / final / workspace / catalog)
tool         = "T " 1*64(ALPHA / DIGIT / "_" / "." / ":" / "-")
final        = "F"
workspace    = "W"
catalog      = "Q"
summary      = "@summary: " 0*400(safe-char)
body         = 1*(record LF) / 1*(plain-line LF)
record       = indent (field / array / literal)
field        = key ":" [SP scalar] / key ":" LF nested-object
array        = key "[" count "]" ["{" headers "}"] ":" LF rows
literal      = key "<<" marker [":" count] LF content LF marker
key          = bare-key / json-quoted-key
bare-key     = (ALPHA / "_") *(ALPHA / DIGIT / "_")
headers      = key *("," key)
count        = "0" / (NZDIGIT *DIGIT)
marker       = (UPPER / "_") *24(UPPER / "_" / DIGIT)
rows         = <exactly count rows, each at indent + 2>
nested-object= <one or more record lines, indented +2>
plain-line   = *safe-char
scalar       = json-string / 1*safe-char / "{}"
json-string  = <JSON double quoted string and JSON escapes>
indent       = *SP
safe-char    = %x20-7E / UTF8-NONASCII
terminator   = "K2/END"
LF           = %x0A
SP           = %x20
UPPER        = %x41-5A
NZDIGIT      = %x31-39
~~~

Indentation, array counts and literal lengths are context-dependent validations beyond ABNF. A frame contains exactly one action. A standalone K2/END is a delimiter only outside literal content. K2 W (workspace) and K2 Q (tool catalog) cannot have a body. A single optional @summary: line appears immediately after the header (maximum 400 characters), populating reasoning_summary; loop stays null.

The decoder accepts CRLF for structure and only ASCII boundary whitespace is normalized. BOM, stray CR, tab outside literal blocks, unpaired surrogates, ASCII C0/DEL controls and trailing spaces outside literals are errors. Literal content permits tab/newline; output remains UTF-8 text. Quoted values are validated after JSON unescaping.

## Named fields and arrays

~~~text
K2 T kitt_runtime
operation: repo.read
arguments:
  path: README.md
K2/END
~~~

~~~text
K2 F
@summary: Tests passed
tasks[1]:
  -
    local_id: T01
    depends_on[0]:
    check_ids[1]:
      - node.typecheck
    data: {}
rows[1]{"X-Foo",status}:
  "one,two",done
K2/END
~~~

A key is an ASCII identifier or a JSON quoted string, allowing names with periods and hyphens. Duplicates are compared **after decoding** and __proto__, prototype and constructor are forbidden everywhere, including table headers. Nested objects use two spaces per level; lists have exactly the declared number of rows at indent+2. A scalar list item starts with "- "; an object list item is a bare "-" followed by its fields at indent+4. Tables use CSV doubled-quote cells rather than JSON escapes; CSV quoted cells are strings. No implicit collection reconstruction or schema repair.

A bare scalar is a string except for true, false, null, canonical safe integers and finite decimals. Negative zero is never canonical. To preserve strings resembling primitives, quote them: "001", "true", "1.10". With an optional schema subset (type, properties, items, additionalProperties, type-only anyOf/oneOf), an inferred primitive becomes its original token text if the path permits only string. Full schema validation remains host-owned. Empty objects use a: {}, empty strings a: "", empty arrays a[0]:; a: with no children is invalid.

## Literals

~~~text
K2 T repo.write_file
path: src/app.ts
content<<CODE
export const ready = true;
K2/END
CODE
K2/END
~~~

The uppercase marker is a standalone column-zero line, including for nested literal keys. The legacy delimiter form requires that marker never occur as a standalone content line. To keep a trailing newline, include a blank line just before the marker. A length-prefixed form such as content<<CODE:12 reads exactly 12 UTF-8 bytes, then requires the marker. It may contain marker-like content and K2/END as inert data; mismatched or truncated sizes fail closed.

The Python decode_kap2_content API accepts only structured K2 F, while decode_kap2_frame and TypeScript parseKAP2 handle all actions and summary metadata. encode_kap2 and encodeKAP2 serialize structured finals deterministically with minimal safe quoting and reject unrepresentable values.

Resource bounds: UTF-8 payload 65536 bytes, at most 3000 lines, nesting depth at most 20, arrays at most 1024 rows. The encoders enforce the same bounds.

## Diagnostic code table

| Code | Meaning |
|---|---|
| E_SIZE | frame exceeds 65536 bytes |
| E_LINES | more than 3000 lines |
| E_HEADER | malformed header, or structured final required |
| E_TERMINATOR | missing final K2/END |
| E_TAB | tab in non-literal record or row |
| E_WHITESPACE | trailing whitespace outside literal |
| E_INDENT | indentation conflict or incomplete object |
| E_FIELD | invalid key/field, missing value |
| E_KEY_UNSAFE | forbidden decoded key |
| E_KEY_DUPLICATE | duplicate decoded key |
| E_SCALAR | invalid scalar/control/negative zero |
| E_NUMBER_RANGE | unsafe integer or nonfinite numeric value |
| E_ARRAY_SIZE | array count above 1024 |
| E_ARRAY_ROWS | missing rows, invalid row indentation |
| E_TABLE_HEADERS | duplicate/invalid table header |
| E_TABLE_COLUMNS | wrong number of table cells |
| E_LITERAL_UNTERMINATED | missing legacy literal terminator |
| E_LITERAL_LENGTH | invalid declared UTF-8 length |
| E_DEPTH | nesting depth above 20 |
| E_UTF8 | invalid surrogate/BOM/Unicode |
| E_BODY_NOT_ALLOWED | W/Q body present |
| E_COMPETING_FRAME | competing top-level envelope in plain final |

Error objects expose stable code and best-effort one-based line. Invalid input is never guessed or automatically repaired; authority remains in the host.

## Existing schema identity

schemas/agent-contract.schema.json currently has an identifier ending agent-contract-v3.schema.json while the AGENT_CONTRACT_VERSION constant is v4. scripts/export_agent_contract.py **copies** the existing schema and does not generate its $id. Because consumers may rely on that identifier, this change does not rename it; a consumer audit must precede any change.

KAP/2 fixtures and seeded differential fuzz tests cover Python and TypeScript. The reverse-proxy's deployed copy of the canonical TypeScript parser must be synchronized and checked during ecosystem rollout. See [the roadmap](KAP2-roadmap.md) for host-dependent features.
