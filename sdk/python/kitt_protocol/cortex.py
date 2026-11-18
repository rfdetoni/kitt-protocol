"""Cross-process Cortex event contracts; data alone never grants tool authority."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CortexEvent:
    id: str
    topic: str
    source: str
    severity: int
    untrusted: bool
    sensitivity: str
    payload: dict[str, Any]
    created: float
    expires: float

    def validate(self) -> None:
        if not self.id or len(self.id) > 128:
            raise ValueError("invalid event ID")
        for text in (self.topic, self.source):
            if not text or len(text) > 80 or not text[0].islower() or not text[0].isascii():
                raise ValueError("invalid event topic/source")
            if any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_.-" for c in text):
                raise ValueError("invalid event topic/source")
        if type(self.severity) is not int or not 1 <= self.severity <= 5:
            raise ValueError("invalid event severity")
        if type(self.untrusted) is not bool:
            raise ValueError("invalid event trust flag")
        if self.sensitivity not in {"public", "personal", "private", "secret", "ephemeral"}:
            raise ValueError("invalid event sensitivity")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be an object")
        if not self.created < self.expires:
            raise ValueError("invalid lifetime")


@dataclass(frozen=True)
class CortexDelivery:
    event: CortexEvent
    attempt: int
    lease_token: str


@dataclass(frozen=True)
class CortexPreflight:
    tier: str
    decision: str
    reason: str

    def validate(self) -> None:
        if self.tier not in {"GREEN", "YELLOW", "RED"}:
            raise ValueError("unknown autonomy tier")
        if self.decision not in {"READ_ONLY", "REQUIRE_APPROVAL", "DENY"}:
            raise ValueError("unknown preflight decision")


@dataclass(frozen=True)
class CortexContextProjection:
    value: str
    source: str
    sensitivity: str
    observed: float
    expires: float
    revision: int


@dataclass(frozen=True)
class CortexRouteAdvice:
    route: str
    advisory: dict[str, Any] | None = None
    status: str = "disabled"
