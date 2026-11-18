import unittest

from kitt_protocol.cortex import CortexEvent, CortexDelivery, CortexPreflight


class CortexContractTests(unittest.TestCase):
    def test_event_roundtrip(self):
        event = CortexEvent(
            id="incident-42", topic="saas.error.500", source="external.webhook",
            severity=4, untrusted=True, sensitivity="private",
            payload={"service": "billing"}, created=10.0, expires=40.0,
        )
        event.validate()
        delivery = CortexDelivery(**vars(event), attempt=1, lease_token="token")
        self.assertEqual("incident-42", delivery.id)
        self.assertEqual(1, delivery.attempt)

    def test_policy_is_not_authority(self):
        CortexPreflight(tier="YELLOW", decision="REQUIRE_APPROVAL",
                        reason="side effect").validate()
        with self.assertRaises(ValueError):
            CortexPreflight(tier="OVERRIDE", decision="READ_ONLY", reason="").validate()

    def test_invalid_event(self):
        event = CortexEvent(
            id="test", topic="saas.error.500", source="external.webhook",
            severity=6, untrusted=True, sensitivity="private",
            payload={}, created=10.0, expires=20.0,
        )
        with self.assertRaises(ValueError):
            event.validate()


if __name__ == "__main__":
    unittest.main()
