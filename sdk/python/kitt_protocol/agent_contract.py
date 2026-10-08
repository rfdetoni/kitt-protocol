"""Agent response wire identifiers and strict structured-result decoding."""
from typing import Any
from .models import ProtocolError, _load_json

AGENT_CONTRACT_HEADER = "X-Kitt-Agent-Contract"
AGENT_CONTRACT_VERSION = "v3"
AGENT_ROUTE_HEADER = "X-Kitt-Route"


def decode_json_object(raw: str | bytes) -> dict[str, Any]:
    """Decode one complete JSON object; reject duplicate keys and non-finite data."""
    value = _load_json(raw)
    if not isinstance(value, dict):
        raise ProtocolError("structured result must be a JSON object")
    return value
