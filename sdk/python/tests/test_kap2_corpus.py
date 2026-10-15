"""Shared KAP/2 golden corpus, explicit limits and round-trip cases."""
from __future__ import annotations
import json
import random
import unittest
from pathlib import Path

from kitt_protocol.kap2 import decode_kap2_content, decode_kap2_frame, encode_kap2, KAP2Error

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "fixtures" / "kap2"


class GoldenKAP2Tests(unittest.TestCase):
    def test_valid(self):
        for item in sorted((CORPUS / "valid").glob("*.k2")):
            with self.subTest(item=item.name):
                value = decode_kap2_content(item.read_text(encoding="utf-8"))
                expected = json.loads(item.with_suffix(".json").read_text(encoding="utf-8"))
                self.assertEqual(value, expected)

    def test_invalid(self):
        for item in sorted((CORPUS / "invalid").glob("*.k2")):
            with self.subTest(item=item.name):
                code = item.with_suffix(".err").read_text(encoding="utf-8").strip()
                with self.assertRaises(KAP2Error) as raised:
                    decode_kap2_frame(item.read_text(encoding="utf-8"))
                self.assertEqual(raised.exception.code, code)

    def test_empty_workspace_tools(self):
        for symbol, action in (("W", "request_workspace"), ("Q", "request_tools")):
            self.assertEqual(decode_kap2_frame("K2 " + symbol + "\nK2/END")["action"], action)
            with self.assertRaises(KAP2Error) as raised:
                decode_kap2_frame("K2 " + symbol + "\nnot allowed\nK2/END")
            self.assertEqual(raised.exception.code, "E_BODY_NOT_ALLOWED")

    def test_limits(self):
        self.assertEqual(len(decode_kap2_content("K2 F\nvalues[1024]:\n"
                         + ("  - ok\n" * 1024) + "K2/END")["values"]), 1024)
        with self.assertRaises(KAP2Error):
            decode_kap2_content("K2 F\nvalues[1025]:\nK2/END")
        for count, accepted in ((20, True), (21, False)):
            body = "\n".join(" " * (2 * i) + "x:" for i in range(count))
            raw = "K2 F\n" + body + "\n" + " " * (2 * count) + "x: true\nK2/END"
            if accepted:
                self.assertTrue(decode_kap2_content(raw)["x"])
            else:
                with self.assertRaises(KAP2Error):
                    decode_kap2_content(raw)
        short = "K2 F\nvalue: "
        tail = "\nK2/END"
        exact = short + "x" * (65536 - len(short) - len(tail)) + tail
        self.assertEqual(len(exact.encode("utf-8")), 65536)
        self.assertIsInstance(decode_kap2_content(exact)["value"], str)
        with self.assertRaises(KAP2Error) as raised:
            decode_kap2_content(exact.replace("\nK2/END", "x\nK2/END"))
        self.assertEqual(raised.exception.code, "E_SIZE")
        literal = "K2 F\nsource<<CODE\n" + "abc\n" * 2996 + "CODE\nK2/END"
        self.assertEqual(len(literal.split("\n")), 3000)
        self.assertIn("abc", decode_kap2_content(literal)["source"])
        with self.assertRaises(KAP2Error):
            decode_kap2_content(literal.replace("CODE\nK2/END", "abc\nCODE\nK2/END"))

    def test_roundtrip(self):
        rng = random.Random(3202)
        cases = [{"title": "quoted", "empty": {}, "rows": [{"id": "X-Foo", "ok": True}]},
                 {"code": 'first\nK2/END\nlast', "items": []}]
        for _ in range(100):
            cases.append({"revision": rng.randint(1, 999), "enabled": bool(rng.getrandbits(1)),
                          "tags": [str(rng.randint(0, 10)), "true", "olá"]})
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(decode_kap2_content(encode_kap2(case)), case)


if __name__ == "__main__":
    unittest.main()
