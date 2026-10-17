import json
import unittest

from kitt_protocol.cleanroom import (
    CleanRoomContractError, canonical_cleanroom_bytes,
    cleanroom_digest, decode_cleanroom_contract,
)

BASE = {
    "target_dll": "kernel32.dll",
    "function_name": "CreateEventW",
    "signature": {"return_type": "HANDLE", "parameters": [
        {"name": "bManualReset", "c_type": "BOOL", "direction": "IN"}]},
    "calling_convention": "WINAPI",
    "observed_behaviors": [{
        "case_id": "null_handle", "input_conditions": "bManualReset=FALSE",
        "expected_return": "non-NULL handle", "last_error": "ERROR_SUCCESS",
        "side_effects": "No externally visible changes",
    }],
}


class CleanRoomTests(unittest.TestCase):
    def test_valid_roundtrip(self):
        parsed = decode_cleanroom_contract(json.dumps(BASE))
        self.assertEqual(canonical_cleanroom_bytes(parsed), canonical_cleanroom_bytes(BASE))
        self.assertEqual(len(cleanroom_digest(BASE)), 64)

    def test_deny_duplicate_members(self):
        raw = json.dumps(BASE).replace('"target_dll":', '"target_dll": "other.dll", "target_dll":', 1)
        with self.assertRaises(CleanRoomContractError):
            decode_cleanroom_contract(raw)

    def test_deny_leakage(self):
        for bad in ("FUN_00401620", "local_20", "goto next", "sizeof(T)",
                    "0x7ffdeadbeef0", "mov eax; ret", "RtlpInternal"):
            item = json.loads(json.dumps(BASE))
            item["observed_behaviors"][0]["side_effects"] = bad
            with self.subTest(bad=bad), self.assertRaises(CleanRoomContractError):
                decode_cleanroom_contract(json.dumps(item))

    def test_deny_unknown_fields_and_controls(self):
        for change in ({"source_code": "secret"}, {"target_dll": "../foo.dll"},
                       {"function_name": "FUN_1234"}):
            item = json.loads(json.dumps(BASE))
            item.update(change)
            with self.assertRaises(CleanRoomContractError):
                decode_cleanroom_contract(json.dumps(item))
        item = json.loads(json.dumps(BASE))
        item["observed_behaviors"][0]["input_conditions"] = "a\nb"
        with self.assertRaises(CleanRoomContractError):
            decode_cleanroom_contract(json.dumps(item))

    def test_deny_duplicate_cases(self):
        item = json.loads(json.dumps(BASE))
        item["observed_behaviors"].append(item["observed_behaviors"][0])
        with self.assertRaises(CleanRoomContractError):
            decode_cleanroom_contract(json.dumps(item))


if __name__ == "__main__":
    unittest.main()
