from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

AGENTIC_SCHEMA_VERSION = 1

class ContextKind(StrEnum):
    SYSTEM_INSTRUCTION = "SYSTEM_INSTRUCTION"
    USER_INTENT = "USER_INTENT"
    MEMORY_RECALL = "MEMORY_RECALL"
    MEMORY_CORRECTION = "MEMORY_CORRECTION"
    SKILL = "SKILL"
    PROJECT_GUIDELINE = "PROJECT_GUIDELINE"
    HARNESS_KNOWLEDGE = "HARNESS_KNOWLEDGE"
    REPOSITORY_MAP = "REPOSITORY_MAP"
    FILE_EVIDENCE = "FILE_EVIDENCE"
    SEARCH_EVIDENCE = "SEARCH_EVIDENCE"
    TOOL_SCHEMA = "TOOL_SCHEMA"
    TOOL_RESULT = "TOOL_RESULT"
    TOOL_RECEIPT = "TOOL_RECEIPT"
    SUBAGENT_RESULT = "SUBAGENT_RESULT"
    VALIDATION_EVIDENCE = "VALIDATION_EVIDENCE"
    ERROR_EVIDENCE = "ERROR_EVIDENCE"
    COMPACTION_CHECKPOINT = "COMPACTION_CHECKPOINT"
    OUTPUT_CONTRACT = "OUTPUT_CONTRACT"

class ContextStability(StrEnum):
    BUILD = "BUILD"
    SESSION = "SESSION"
    TURN = "TURN"

class RecoveryMode(StrEnum):
    NONE = "NONE"
    EXACT = "EXACT"
    SOURCE_REF = "SOURCE_REF"
    RECOMPUTE = "RECOMPUTE"

class CacheRegion(StrEnum):
    FROZEN_PREFIX = "FROZEN_PREFIX"
    SESSION_PREFIX = "SESSION_PREFIX"
    LIVE_ZONE = "LIVE_ZONE"
    UNCACHED = "UNCACHED"

class ContextTrust(StrEnum):
    TRUSTED = "TRUSTED"
    UNTRUSTED_WORKSPACE = "UNTRUSTED_WORKSPACE"
    EXTERNAL = "EXTERNAL"

def _wire(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _wire(item) for key, item in asdict(value).items() if item is not None}
    if isinstance(value, dict):
        return {str(key): _wire(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_wire(item) for item in value]
    return value

@dataclass(frozen=True)
class ContextRecoveryRef:
    artifact_id: str
    sha256: str
    original_bytes: int
    token_estimate: int
    media_type: str
    recovery: RecoveryMode = RecoveryMode.EXACT

    def to_mapping(self) -> dict[str, Any]:
        return _wire(self)

@dataclass(frozen=True)
class ContextSegment:
    id: str
    kind: ContextKind
    source: str
    trust: ContextTrust
    stability: ContextStability
    priority: int
    sensitivity: str
    recovery: RecoveryMode
    cache_region: CacheRegion
    lifecycle: str
    provenance_digest: str
    token_cost: int
    body_ref: Any
    ttl_turns: int | None = None

    def to_mapping(self) -> dict[str, Any]:
        return _wire(self)

@dataclass(frozen=True)
class ContextEnvelope:
    epoch: str
    segments: tuple[ContextSegment, ...] = ()
    schema_version: int = AGENTIC_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != AGENTIC_SCHEMA_VERSION:
            raise ValueError(f"unsupported agentic schema version {self.schema_version}")
        if not self.epoch.strip():
            raise ValueError("context epoch is empty")
        ids = [segment.id for segment in self.segments]
        if any(not value.strip() for value in ids):
            raise ValueError("context segment id is empty")
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate context segment id")

    def to_mapping(self) -> dict[str, Any]:
        return _wire(self)

@dataclass(frozen=True)
class KittRequestMetadata:
    conversation_id: str
    turn_id: str
    request_id: str
    route: str
    session_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("conversation_id", "turn_id", "request_id", "route"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if self.session_id is not None and not str(self.session_id).strip():
            raise ValueError("session_id must be non-empty when present")

    def to_mapping(self) -> dict[str, Any]:
        return _wire(self)


@dataclass(frozen=True)
class AgentEvent:
    event_id: str
    conversation_id: str
    turn_id: str
    seq: int
    kind: str
    source: str
    timestamp: int
    payload: dict[str, Any]
    durability: str = "DURABLE"
    parent_event_id: str | None = None

@dataclass(frozen=True)
class ExecutionBudget:
    max_model_calls: int
    max_input_tokens: int
    max_output_tokens: int
    max_total_tokens: int
    max_cost: float
    max_duration_ms: int
    max_tool_calls: int
    max_subagents: int

@dataclass(frozen=True)
class BudgetLease:
    id: str
    parent_budget_id: str
    child_agent_id: str
    token_cap: int
    call_cap: int
    cost_cap: float
    reserved: dict[str, Any] = field(default_factory=dict)
    consumed: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ExecutionAuthoritySnapshot:
    policy_revision: str
    autonomy_revision: str
    approval_revision: str
    workspace_id: str
    conversation_id: str
    turn_id: str
    sandbox_profile: str
    filesystem_caps: tuple[str, ...]
    network_caps: tuple[str, ...]
    executable_identity: str
    approval_grant: dict[str, Any] | None = None

@dataclass(frozen=True)
class ContextEpoch:
    epoch_id: str
    baseline_seq: int
    memory_revision: str
    repository_revision: str
    skills_revision: str
    plugins_revision: str
    policy_revision: str
    provider_revision: str
    snapshot_digest: str

@dataclass(frozen=True)
class CompactionCheckpoint:
    objective: str
    constraints: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    completed: tuple[str, ...] = ()
    active: tuple[str, ...] = ()
    blocked: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    relevant_files: tuple[str, ...] = ()
    validation_state: tuple[str, ...] = ()
    recovery_refs: tuple[ContextRecoveryRef, ...] = ()

@dataclass(frozen=True)
class AgentLineage:
    agent_id: str
    parent_turn_id: str
    root_task_id: str
    generation: int
    role: str
    backend: str
    model: str
    context_fork_mode: str
    isolation_mode: str
    budget_lease_id: str
    parent_agent_id: str | None = None

@dataclass(frozen=True)
class WorkspaceSnapshot:
    snapshot_id: str
    turn_id: str
    created_at: int
    changed_paths: tuple[str, ...]
    digest: str
    parent_snapshot_id: str | None = None

class AgentRole(StrEnum):
    DISCOVER = "DISCOVER"
    ARCHITECT = "ARCHITECT"
    IMPLEMENT = "IMPLEMENT"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"

@dataclass(frozen=True)
class MemoryLifecycleEvent:
    event: str
    namespace: str
    workspace_id: str
    source_id: str
    source_revision: str
    input_digest: str
    source_kind: str = "external"
    source_watermark: str = ""

@dataclass(frozen=True)
class SavedPermission:
    workspace_id: str
    action: str
    resource_pattern: str
    decision: str
    executable_identity: str | None = None

@dataclass(frozen=True)
class PluginCapabilities:
    tools: tuple[str, ...] = ()
    providers: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    hooks: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    context_sources: tuple[str, ...] = ()
    ui_extensions: tuple[str, ...] = ()

@dataclass(frozen=True)
class MemoryConsumptionReceipt:
    recall_trace_id: str
    memory_id: str
    consumer: str
    purpose: str
    presented: bool
    referenced: bool
    used_for_action: bool
    outcome: str
    turn_id: str
    consumed_at: int

@dataclass(frozen=True)
class MemoryJob:
    id: str
    phase: str
    source_id: str
    source_revision: str
    source_watermark: str
    status: str
    attempt: int
    input_digest: str
    created_at: int
    updated_at: int
    lease_owner: str | None = None
    lease_until: int | None = None
    next_retry_at: int | None = None
    output_digest: str | None = None
