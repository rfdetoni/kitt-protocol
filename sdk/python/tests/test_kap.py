import unittest
from kitt_protocol import decode_kap_content


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


if __name__ == "__main__":
    unittest.main()
