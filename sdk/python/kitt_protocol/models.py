from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
import uuid

PROTOCOL_VERSION = 1
MAX_FRAME_BYTES = 1024 * 1024

SYSTEM_PING_REQUEST = "system.ping.request"
SYSTEM_PING_RESPONSE = "system.ping.response"
SYSTEM_ERROR = "system.error"
ASSISTANT_ASK_REQUEST = "assistant.ask.request"
ASSISTANT_ASK_RESPONSE = "assistant.ask.response"
ASSISTANT_ASK_ROUTED_REQUEST = "assistant.ask_routed.request"
ASSISTANT_ASK_ROUTED_RESPONSE = "assistant.ask_routed.response"
ASSISTANT_TRANSCRIBE_REQUEST = "assistant.transcribe.request"
ASSISTANT_TRANSCRIBE_RESPONSE = "assistant.transcribe.response"
ASSISTANT_REMEMBER_REQUEST = "assistant.remember.request"
ASSISTANT_REMEMBER_RESPONSE = "assistant.remember.response"
MEMORY_REMEMBER_REQUEST = "memory.remember.request"
MEMORY_REMEMBER_RESPONSE = "memory.remember.response"
MEMORY_RECALL_REQUEST = "memory.recall.request"
MEMORY_RECALL_RESPONSE = "memory.recall.response"
MEMORY_SEARCH_REQUEST = "memory.search.request"
MEMORY_SEARCH_RESPONSE = "memory.search.response"
MEMORY_TIMELINE_REQUEST = "memory.timeline.request"
MEMORY_TIMELINE_RESPONSE = "memory.timeline.response"
MEMORY_GET_REQUEST = "memory.get.request"
MEMORY_GET_RESPONSE = "memory.get.response"
MEMORY_FORGET_REQUEST = "memory.forget.request"
MEMORY_FORGET_RESPONSE = "memory.forget.response"
MEMORY_MANAGE_REQUEST = "memory.manage.request"
MEMORY_MANAGE_RESPONSE = "memory.manage.response"
HUD_SUBSCRIBE_REQUEST = "hud.subscribe.request"
HUD_SUBSCRIBE_RESPONSE = "hud.subscribe.response"
HUD_IMAGE_REQUEST = "hud.image.request"
HUD_IMAGE_RESPONSE = "hud.image.response"
HUD_EVENT = "hud.event"
WORKER_EXECUTE_REQUEST = "worker.execute.request"
WORKER_EXECUTE_RESPONSE = "worker.execute.response"
SETTINGS_CATALOG_REQUEST = "settings.catalog.request"
SETTINGS_CATALOG_RESPONSE = "settings.catalog.response"
SETTINGS_SNAPSHOT_REQUEST = "settings.snapshot.request"
SETTINGS_SNAPSHOT_RESPONSE = "settings.snapshot.response"
SETTINGS_VALIDATE_REQUEST = "settings.validate.request"
SETTINGS_VALIDATE_RESPONSE = "settings.validate.response"
SETTINGS_APPLY_REQUEST = "settings.apply.request"
SETTINGS_APPLY_RESPONSE = "settings.apply.response"
SETTINGS_HEALTH_REQUEST = "settings.health.request"
SETTINGS_HEALTH_RESPONSE = "settings.health.response"
CAPABILITIES_REQUEST = "capabilities.request"
CAPABILITIES_RESPONSE = "capabilities.response"
SURFACE_CREATE = "surface.create"
SURFACE_PATCH = "surface.patch"
SURFACE_DELETE = "surface.delete"
SURFACE_ACTION = "surface.action"
SURFACE_VALIDATION_FAILED = "surface.validation_failed"
BACKEND_VALIDATE_REQUEST = "backend.validate.request"
BACKEND_VALIDATE_RESPONSE = "backend.validate.response"
BACKEND_PLAN_REQUEST = "backend.plan.request"
BACKEND_PLAN_RESPONSE = "backend.plan.response"
BACKEND_APPLY_REQUEST = "backend.apply.request"
BACKEND_APPLY_RESPONSE = "backend.apply.response"


class ProtocolError(ValueError):
    pass


def _ensure_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProtocolError(f"{name} must be a JSON object")
    return value


@dataclass(frozen=True)
class Envelope:
    kind: str
    payload: Any
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str | None = None
    version: int = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        if self.version != PROTOCOL_VERSION:
            raise ProtocolError(
                f"unsupported protocol version {self.version}; expected {PROTOCOL_VERSION}"
            )
        if not isinstance(self.id, str) or not self.id.strip():
            raise ProtocolError("envelope id is empty")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ProtocolError("envelope kind is empty")
        if self.correlation_id is not None and (
            not isinstance(self.correlation_id, str) or not self.correlation_id.strip()
        ):
            raise ProtocolError("correlation_id cannot be empty")

    def to_mapping(self) -> dict[str, Any]:
        data = {
            "version": self.version,
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
        }
        if self.correlation_id is not None:
            data["correlation_id"] = self.correlation_id
        return data

    @classmethod
    def from_mapping(cls, value: Any) -> "Envelope":
        data = _ensure_object(value, "envelope")
        allowed = {"version", "id", "kind", "correlation_id", "payload"}
        required = {"version", "id", "kind", "payload"}
        unknown = set(data) - allowed
        missing = required - set(data)
        if unknown:
            raise ProtocolError(f"unknown envelope fields: {sorted(unknown)}")
        if missing:
            raise ProtocolError(f"missing envelope fields: {sorted(missing)}")
        return cls(
            version=data["version"],
            id=data["id"],
            kind=data["kind"],
            correlation_id=data.get("correlation_id"),
            payload=data["payload"],
        )

    def dumps(self) -> str:
        return json.dumps(
            self.to_mapping(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @classmethod
    def loads(cls, raw: str | bytes) -> "Envelope":
        encoded = raw.encode("utf-8") if isinstance(raw, str) else raw
        if len(encoded) > MAX_FRAME_BYTES:
            raise ProtocolError("frame_too_large")
        try:
            data = json.loads(encoded)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProtocolError(f"invalid_json: {exc}") from exc
        return cls.from_mapping(data)

    @classmethod
    def response(cls, kind: str, request_id: str, payload: Any) -> "Envelope":
        return cls(kind=kind, payload=payload, correlation_id=request_id)

    @classmethod
    def error(cls, request_id: str | None, code: str, message: str) -> "Envelope":
        return cls(
            kind=SYSTEM_ERROR,
            correlation_id=request_id,
            payload={"code": code, "message": message},
        )


@dataclass(frozen=True)
class AuthenticatedFrame:
    envelope: Envelope
    token: str = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.token, str) or not self.token.strip():
            raise ProtocolError("authentication token is empty")

    def dumps(self) -> str:
        return json.dumps(
            {"token": self.token, "envelope": self.envelope.to_mapping()},
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @classmethod
    def loads(cls, raw: str | bytes) -> "AuthenticatedFrame":
        encoded = raw.encode("utf-8") if isinstance(raw, str) else raw
        if len(encoded) > MAX_FRAME_BYTES:
            raise ProtocolError("frame_too_large")
        try:
            data = _ensure_object(json.loads(encoded), "authenticated frame")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProtocolError(f"invalid_json: {exc}") from exc
        if set(data) != {"token", "envelope"}:
            raise ProtocolError("authenticated frame must contain exactly token and envelope")
        return cls(
            token=data["token"],
            envelope=Envelope.from_mapping(data["envelope"]),
        )


@dataclass(frozen=True)
class HudEvent:
    type: str
    content: str | None = None
    src: str | None = None
    alt: str | None = None
    state: str | None = None
    message: str | None = None
    ttl_ms: int | None = None


@dataclass(frozen=True)
class MemoryRememberRequest:
    namespace: str
    workspace_id: str
    content: str
    kind: str
    sensitivity: str
    scope: str
    scope_key: str | None = None
    importance: float = 0.8
    confidence: float = 1.0
    pinned: bool = False
    ttl_seconds: int | None = None


@dataclass(frozen=True)
class MemoryRecallRequest:
    namespace: str
    workspace_id: str
    query: str = ""
    limit: int = 6
    scope_key: str | None = None
    as_of: int | None = None
    allow_private: bool = False
    allow_secret: bool = False


@dataclass(frozen=True)
class MemorySearchRequest:
    namespace: str
    workspace_id: str
    query: str = ""
    max_results: int = 24
    token_budget: int = 1200
    scope_key: str | None = None
    as_of: int | None = None
    allow_private: bool = False
    allow_secret: bool = False


@dataclass(frozen=True)
class MemoryTimelineRequest:
    namespace: str
    workspace_id: str
    source_id: str | None = None
    scope_key: str | None = None
    around: int | None = None
    limit: int = 24
    token_budget: int = 1200
    allow_private: bool = False
    allow_secret: bool = False


@dataclass(frozen=True)
class MemoryGetRequest:
    namespace: str
    workspace_id: str
    ids: tuple[str, ...]
    scope_key: str | None = None
    token_budget: int = 2400
    allow_private: bool = False
    allow_secret: bool = False


@dataclass(frozen=True)
class MemorySearchHit:
    id: str
    kind: str
    snippet: str
    sensitivity: str
    scope: str
    scope_key: str | None
    importance: float
    confidence: float
    token_estimate: int
    provenance: tuple["ResourceRef", ...] = ()


@dataclass(frozen=True)
class MemorySearchResponse:
    recall_trace_id: str
    hits: tuple[MemorySearchHit, ...]
    consumed_tokens: int
    has_more: bool


@dataclass(frozen=True)
class MemoryTimelineHit:
    id: str
    kind: str
    snippet: str
    updated_at: int
    sensitivity: str
    scope: str
    scope_key: str | None
    importance: float
    confidence: float
    token_estimate: int
    provenance: tuple["ResourceRef", ...] = ()


@dataclass(frozen=True)
class MemoryTimelineResponse:
    recall_trace_id: str
    hits: tuple[MemoryTimelineHit, ...]
    consumed_tokens: int
    has_more: bool


@dataclass(frozen=True)
class MemoryHydratedRecord:
    record: dict[str, Any]
    provenance: tuple["ResourceRef", ...] = ()


@dataclass(frozen=True)
class MemoryGetResponse:
    recall_trace_id: str
    records: tuple[MemoryHydratedRecord, ...]
    consumed_tokens: int
    truncated_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemoryForgetRequest:
    id: str


@dataclass(frozen=True)
class WorkerExecuteRequest:
    capability: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class RoutedAskRequest:
    text: str
    locale: str | None = None
    route: str = "auto"
    show_hud: bool = True


@dataclass(frozen=True)
class RoutedAskResponse:
    text: str
    tier: str
    fallback_used: bool = False


@dataclass(frozen=True)
class TranscribeRequest:
    path: str
    locale: str | None = None
    show_hud: bool = True


@dataclass(frozen=True)
class TranscribeResponse:
    text: str


# Semantic protocol contracts -------------------------------------------------

@dataclass(frozen=True)
class ResourceRef:
    uri: str
    revision: str | None = None
    digest: str | None = None


@dataclass(frozen=True)
class EvidenceRef:
    source: ResourceRef
    observed_at: int
    confidence: float = 1.0
    note: str | None = None


@dataclass(frozen=True)
class CapabilitySet:
    protocol: str
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChangeOperation:
    op: str
    target: str
    effect: str
    value: Any = None
    evidence: tuple[EvidenceRef, ...] = ()


@dataclass(frozen=True)
class ChangeSet:
    id: str
    domain: str
    base_revision: str | None = None
    operations: tuple[ChangeOperation, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    path: str | None = None


@dataclass(frozen=True)
class SurfaceComponent:
    id: str
    component: str
    props: dict[str, Any] = field(default_factory=dict)
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class Surface:
    id: str
    revision: int
    catalog_id: str
    root: str
    components: tuple[SurfaceComponent, ...] = ()
    state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SurfacePatch:
    surface_id: str
    base_revision: int
    operations: tuple[ChangeOperation, ...] = ()


@dataclass(frozen=True)
class SurfaceAction:
    surface_id: str
    component_id: str
    action: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RendererCapabilities:
    surface_protocol: str = "surface.v1"
    catalogs: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    max_depth: int = 16
    max_nodes: int = 256


@dataclass(frozen=True)
class BackendResource:
    id: str
    kind: str
    spec: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BackendModule:
    id: str
    revision: int
    metadata: dict[str, Any] = field(default_factory=dict)
    resources: tuple[BackendResource, ...] = ()


@dataclass(frozen=True)
class BackendPlan:
    backend_id: str
    base_revision: int
    changeset: ChangeSet
    affected_resources: tuple[ResourceRef, ...] = ()
    issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True)
class MemoryManageRequest:
    operation: str
    arguments: dict[str, Any] = field(default_factory=dict)
