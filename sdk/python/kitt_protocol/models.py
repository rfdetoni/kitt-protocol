from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Optional
import json, uuid

PROTOCOL_VERSION = 1

@dataclass(frozen=True)
class Envelope:
    kind: str
    payload: dict[str, Any]
    id: str = ""
    version: int = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        if not self.id:
            object.__setattr__(self, "id", str(uuid.uuid4()))

    def dumps(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))

@dataclass(frozen=True)
class HudEvent:
    type: str
    content: Optional[str] = None
    src: Optional[str] = None
    alt: Optional[str] = None
    state: Optional[str] = None
    message: Optional[str] = None
    ttl_ms: Optional[int] = None

@dataclass(frozen=True)
class MemoryRememberRequest:
    namespace: str
    workspace_id: str
    content: str
    kind: str
    sensitivity: str = "private"
    scope: str = "workspace"
    pinned: bool = False
    ttl_seconds: Optional[int] = None

@dataclass(frozen=True)
class MemoryRecallRequest:
    namespace: str
    workspace_id: str
    query: str = ""
    limit: int = 6
    allow_private: bool = False
    allow_secret: bool = False
