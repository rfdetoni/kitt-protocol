import unittest
from kitt_protocol import KAP_CURRENT_VERSION, KAP_VERSION_HEADER, KAPNegotiationError, negotiate_kap_version


class NegotiationTests(unittest.TestCase):
    def test_exact_current_version_and_legacy_missing_header(self):
        self.assertEqual(KAP_VERSION_HEADER, "X-Kitt-KAP")
        self.assertEqual(negotiate_kap_version(None), KAP_CURRENT_VERSION)
        self.assertEqual(negotiate_kap_version("KAP/2"), KAP_CURRENT_VERSION)

    def test_unsupported_or_ambiguous_versions_fail_closed(self):
        for value in ("KAP/1", "KAP/3", "K2/3", "KAP/2,KAP/1", " KAP/2", "", "kap/2"):
            with self.subTest(value=value), self.assertRaises(KAPNegotiationError):
                negotiate_kap_version(value)
