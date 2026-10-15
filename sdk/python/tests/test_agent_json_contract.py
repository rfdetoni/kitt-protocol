"""Active JSON model wire is strict; archived grammar is opt-in."""
import json
import subprocess
import sys
import unittest

from kitt_protocol import (
    AGENT_CONTRACT_VERSION, AGENT_WIRE_FORMAT, ProtocolError, decode_json_object,
)


class AgentJsonContractTests(unittest.TestCase):
    def test_source_and_unicode_are_preserved(self):
        expected = {"tasks": [{"id": "T01"}], "source": '  print("ação 😀")\n\n',
                    "path": "src/__init__.py"}
        self.assertEqual(AGENT_CONTRACT_VERSION, "v5")
        self.assertEqual(AGENT_WIRE_FORMAT, "json")
        self.assertEqual(decode_json_object(json.dumps(expected)), expected)

    def test_invalid_results_fail_closed(self):
        for raw in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', '{} {}', '[]', '{"x":']:
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                decode_json_object(raw)

    def test_active_sdk_does_not_load_archived_grammar(self):
        subprocess.run([sys.executable, "-c", "import sys,kitt_protocol; assert not any("
                        "name in sys.modules for name in ['kitt_protocol.kap',"
                        "'kitt_protocol.kap2','kitt_protocol.kap_version'])"],
                       check=True, timeout=10)
