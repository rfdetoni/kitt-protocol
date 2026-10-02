#!/usr/bin/env python3
"""Export the authoritative context wire schema for standalone TypeScript consumers."""
import argparse, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "sdk/typescript/src/context-schema.ts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schema = json.loads((ROOT / "schemas/context-envelope.schema.json").read_text())
    encoded = json.dumps(schema, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    content = f"// Generated from kitt-protocol; schema sha256: {digest}. Do not edit.\nexport const CONTEXT_ENVELOPE_SCHEMA = {encoded} as const;\n"
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit("context schema export differs from Protocol")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
if __name__ == "__main__": main()
