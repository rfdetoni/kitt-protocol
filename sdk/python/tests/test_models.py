import json, unittest
from kitt_protocol.models import Envelope

class EnvelopeTest(unittest.TestCase):
    def test_round_trip_shape(self):
        raw = json.loads(Envelope("ping", {"ok": True}).dumps())
        self.assertEqual(1, raw["version"])
        self.assertEqual("ping", raw["kind"])
        self.assertTrue(raw["id"])

if __name__ == "__main__": unittest.main()
