#!/usr/bin/env python3
"""Export the authoritative Agent response schema and wire identifiers."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "sdk/typescript/src/agent-contract.ts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    # Load identifiers without importing the SDK or requiring it to be installed.
    source = (ROOT / "sdk/python/kitt_protocol/agent_contract.py").read_text()
    identifiers = {}
    for line in source.splitlines():
        if line.startswith("AGENT_"):
            name, value = line.split(" = ", 1)
            identifiers[name] = json.loads(value)
    schema = json.loads((ROOT / "schemas/agent-contract.schema.json").read_text())
    encoded = json.dumps(schema, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    content = f"// Generated from kitt-protocol; schema sha256: {digest}. Do not edit.\n"
    content += "".join(f"export const {name} = {json.dumps(value)};\n" for name, value in identifiers.items())
    content += f"export const AGENT_RESPONSE_SCHEMA = {encoded} as const;\n"
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit("Agent contract export differs from Protocol")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)


if __name__ == "__main__":
    main()
