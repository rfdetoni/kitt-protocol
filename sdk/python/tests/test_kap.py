import unittest
from kitt_protocol.kap import decode_kap_content, decode_kap2_content


class KAPContentTests(unittest.TestCase):
    def test_structured_plan(self):
        actual = decode_kap_content("\n".join((
            "KITT/1", "ACTION FINAL", "OBJECT content", "ARRAY content.items",
            "OBJECT content.items.0", "STRING content.items.0.local_id = T01",
            "ARRAY content.items.0.check_ids", "KITT/END"
        )))
        self.assertEqual(actual, {"items": [{"local_id": "T01", "check_ids": []}]})

    def test_literal_text_preserved(self):
        actual = decode_kap_content("\n".join((
            "KITT/1", "ACTION FINAL", "OBJECT content", "TEXT content.summary",
            'a "quoted" value with \\ backslash', "KITT/ENDTEXT", "KITT/END"
        )))
        self.assertEqual(actual["summary"], 'a "quoted" value with \\ backslash')

    def test_rejects_unsafe_and_incomplete_results(self):
        bad = (
            ["KITT/1", "ACTION FINAL", "STRING content.ok = 1", "STRING content.ok = 2", "KITT/END"],
            ["KITT/1", "ACTION FINAL", "ARRAY content.items", "STRING content.items.2 = skip", "KITT/END"],
            ["KITT/1", "ACTION FINAL", "STRING content.__proto__.bad = 1", "KITT/END"],
            ["KITT/1", "ACTION TOOL", "STRING content = not a final", "KITT/END"],
        )
        for lines in bad:
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                decode_kap_content("\n".join(lines))

    def test_compact_tabular_final(self):
        result = decode_kap_content("\n".join((
            "K2 F", "tasks[2]{id,done}:",
            "  T01,true", "  T02,false", "meta:", "  rev: 2", "K2/END"
        )))
        self.assertEqual(result, {
            "tasks": [{"id": "T01", "done": True}, {"id": "T02", "done": False}],
            "meta": {"rev": 2}
        })

    def test_compact_literal_keeps_raw_code(self):
        result = decode_kap2_content(
            'K2 F\nsource<<CODE\nprint("hello")\nK2/END\nCODE\nK2/END'
        )
        self.assertEqual(result["source"], 'print("hello")\nK2/END')

    def test_compact_rejects_unsafe_or_ambiguous(self):
        for payload in (
            "K2 F\n__proto__:\n  value: x\nK2/END",
            "K2 F\npath: 1\npath: 2\nK2/END",
            "K2 F\nitems[2]{id}:\n  T01\nK2/END",
            "K2 F\nsource<<CODE\npartial\nK2/END",
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                decode_kap2_content(payload)

if __name__ == "__main__":
    unittest.main()
