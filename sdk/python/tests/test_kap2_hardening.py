"""KAP/2 regression tests. Intentional red tests before hardening."""
import unittest
from kitt_protocol import decode_kap2_content
from kitt_protocol.models import ProtocolError


def frame(*body):
    return "\n".join(("K2 F", *body, "K2/END"))


class KAP2HardeningTests(unittest.TestCase):
    def test_tabs_in_rows(self):
        for raw in (frame("items[1]:", "  - a\tb"),
                    frame("items[1]{a}:", "  x\ty")):
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                decode_kap2_content(raw)

    def test_surrogates_controls_and_invalid_utf8(self):
        for raw in (frame(r'a: "\ud800"'), frame(r'a: "\udc00"'),
                    frame(r'a: "\u007f"'), frame("a: \x01"),
                    frame("a: \x00"), frame("a: " + chr(0xd800))):
            with self.subTest(raw=repr(raw)), self.assertRaises(ProtocolError):
                decode_kap2_content(raw)

    def test_trailing_whitespace(self):
        for raw in (frame("a: x "), frame('a: "x"   '), frame("a: "),
                    frame("items[1]:", "  - abc "), frame("items[1]{a}:", "  x\t")):
            with self.subTest(raw=repr(raw)), self.assertRaises(ProtocolError):
                decode_kap2_content(raw)

    def test_reject_negative_zero(self):
        for raw in (frame("z: -0"), frame("z: -0.000"),
                    frame("rows[1]{n}:", "  -0")):
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                decode_kap2_content(raw)

    def test_reject_bom_keep_literal_tabs(self):
        with self.assertRaises(ProtocolError):
            decode_kap2_content("\ufeff" + frame("ok: yes"))
        self.assertEqual(decode_kap2_content(frame("content<<CODE", "\ta\t", "CODE")),
                         {"content": "\ta\t"})

    def test_framing_unusual_whitespace(self):
        with self.assertRaises(ProtocolError):
            decode_kap2_content("\u00a0" + frame("a: x"))
        with self.assertRaises(ProtocolError):
            decode_kap2_content(frame("a: x") + "\u00a0")

    def test_quoted_keys_and_empty_values(self):
        self.assertEqual(decode_kap2_content(frame('"X-Foo": bar', 'a: {}', 'b: ""')),
                         {"X-Foo": "bar", "a": {}, "b": ""})
        with self.assertRaises(ProtocolError):
            decode_kap2_content(frame("a:"))

    def test_object_array(self):
        raw = frame("tasks[1]:", "  -", "    local_id: t1",
                    "    check_ids[1]:", "      - node.typecheck",
                    "    depends_on[0]:", "    note<<TXT",
                    "some text", "TXT")
        self.assertEqual(decode_kap2_content(raw),
                         {"tasks": [{"local_id": "t1", "check_ids": ["node.typecheck"],
                                     "depends_on": [], "note": "some text"}]})

    def test_summary(self):
        from kitt_protocol import decode_kap2_frame
        response = decode_kap2_frame(frame("@summary: checked", "ok: true"))
        self.assertEqual(response["reasoning_summary"], "checked")
        self.assertEqual(response["content"], {"ok": True})

    def test_schema_guided_scalar(self):
        from kitt_protocol import decode_kap2_content
        self.assertEqual(
            decode_kap2_content(frame("version: 1.10", "enabled: true"), schema={
                "type": "object", "properties": {"version": {"type": "string"}, "enabled": {"type": "string"}}
            }),
            {"version": "1.10", "enabled": "true"})

    def test_invalid_line_and_crlf(self):
        self.assertEqual(decode_kap2_content(frame("ok: true").replace("\n", "\r\n")),
                         {"ok": True})
        with self.assertRaises(ProtocolError):
            decode_kap2_content("K2 F\rok: true\nK2/END")
