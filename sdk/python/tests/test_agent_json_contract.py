"""Active JSON model wire stays strict; archived grammar is never loaded implicitly."""
import subprocess
import sys
import pytest
from kitt_protocol import AGENT_CONTRACT_VERSION, AGENT_WIRE_FORMAT, ProtocolError, decode_json_object


def test_json_result_preserves_source_and_unicode():
    import json
    expected = {"tasks":[{"id":"T01"}],"source":'  print("ação 😀")\n\n',"path":"src/__init__.py"}
    assert AGENT_CONTRACT_VERSION == "v5" and AGENT_WIRE_FORMAT == "json"
    assert decode_json_object(json.dumps(expected)) == expected


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', '{} {}', '[]', '{"x":'])
def test_invalid_results_fail_closed(raw):
    with pytest.raises(ProtocolError):
        decode_json_object(raw)


def test_active_sdk_import_does_not_load_archived_grammar():
    subprocess.run([sys.executable,"-c","import sys,kitt_protocol; assert not any(name in sys.modules for name in ['kitt_protocol.kap','kitt_protocol.kap2','kitt_protocol.kap_version'])"],check=True,timeout=10)
