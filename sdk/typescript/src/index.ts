export const PROTOCOL_VERSION = 1 as const;
export const MAX_FRAME_BYTES = 1024 * 1024;

export const KINDS = {
  SYSTEM_PING_REQUEST: "system.ping.request",
  SYSTEM_PING_RESPONSE: "system.ping.response",
  SYSTEM_ERROR: "system.error",
  ASSISTANT_ASK_REQUEST: "assistant.ask.request",
  ASSISTANT_ASK_RESPONSE: "assistant.ask.response",
  ASSISTANT_ASK_ROUTED_REQUEST: "assistant.ask_routed.request",
  ASSISTANT_ASK_ROUTED_RESPONSE: "assistant.ask_routed.response",
  ASSISTANT_TRANSCRIBE_REQUEST: "assistant.transcribe.request",
  ASSISTANT_TRANSCRIBE_RESPONSE: "assistant.transcribe.response",
  ASSISTANT_REMEMBER_REQUEST: "assistant.remember.request",
  ASSISTANT_REMEMBER_RESPONSE: "assistant.remember.response",
  MEMORY_REMEMBER_REQUEST: "memory.remember.request",
  MEMORY_REMEMBER_RESPONSE: "memory.remember.response",
  MEMORY_RECALL_REQUEST: "memory.recall.request",
  MEMORY_RECALL_RESPONSE: "memory.recall.response",
  MEMORY_FORGET_REQUEST: "memory.forget.request",
  MEMORY_FORGET_RESPONSE: "memory.forget.response",
  MEMORY_MANAGE_REQUEST: "memory.manage.request",
  MEMORY_MANAGE_RESPONSE: "memory.manage.response",
  HUD_SUBSCRIBE_REQUEST: "hud.subscribe.request",
  HUD_SUBSCRIBE_RESPONSE: "hud.subscribe.response",
  HUD_IMAGE_REQUEST: "hud.image.request",
  HUD_IMAGE_RESPONSE: "hud.image.response",
  HUD_EVENT: "hud.event",
  WORKER_EXECUTE_REQUEST: "worker.execute.request",
  WORKER_EXECUTE_RESPONSE: "worker.execute.response",
  SETTINGS_CATALOG_REQUEST: "settings.catalog.request",
  SETTINGS_CATALOG_RESPONSE: "settings.catalog.response",
  SETTINGS_SNAPSHOT_REQUEST: "settings.snapshot.request",
  SETTINGS_SNAPSHOT_RESPONSE: "settings.snapshot.response",
  SETTINGS_VALIDATE_REQUEST: "settings.validate.request",
  SETTINGS_VALIDATE_RESPONSE: "settings.validate.response",
  SETTINGS_APPLY_REQUEST: "settings.apply.request",
  SETTINGS_APPLY_RESPONSE: "settings.apply.response",
  SETTINGS_HEALTH_REQUEST: "settings.health.request",
  SETTINGS_HEALTH_RESPONSE: "settings.health.response",
  CAPABILITIES_REQUEST: "capabilities.request",
  CAPABILITIES_RESPONSE: "capabilities.response",
  SURFACE_CREATE: "surface.create",
  SURFACE_PATCH: "surface.patch",
  SURFACE_DELETE: "surface.delete",
  SURFACE_ACTION: "surface.action",
  SURFACE_VALIDATION_FAILED: "surface.validation_failed",
  BACKEND_VALIDATE_REQUEST: "backend.validate.request",
  BACKEND_VALIDATE_RESPONSE: "backend.validate.response",
  BACKEND_PLAN_REQUEST: "backend.plan.request",
  BACKEND_PLAN_RESPONSE: "backend.plan.response",
  BACKEND_APPLY_REQUEST: "backend.apply.request",
  BACKEND_APPLY_RESPONSE: "backend.apply.response",
} as const;

export type ModelRoute = "auto" | "fast" | "heavy";
export type ModelTier = "fast" | "heavy";
export interface RoutedAskRequest { text: string; locale?: string | null; route?: ModelRoute; show_hud?: boolean; }
export interface RoutedAskResponse { text: string; tier: ModelTier; fallback_used?: boolean; }
export interface TranscribeRequest { path: string; locale?: string | null; show_hud?: boolean; }
export interface TranscribeResponse { text: string; }

export type HudState = "listening" | "thinking" | "responding" | "executing" | "error";
export type HudEvent =
  | { type: "status"; state: HudState; message?: string | null }
  | { type: "text"; content: string; ttl_ms: number }
  | { type: "image"; src: string; alt?: string | null; ttl_ms: number }
  | { type: "hide" };

export interface Envelope<T = unknown> {
  version: 1;
  id: string;
  kind: string;
  correlation_id?: string | null;
  payload: T;
}

export interface AuthenticatedFrame<T = unknown> {
  token: string;
  envelope: Envelope<T>;
}

export type MemoryKind =
  | "user_preference" | "project_rule" | "architecture_decision"
  | "technical_fact" | "working_pattern" | "failed_approach"
  | "open_issue" | "project_state" | "episodic" | "personal_fact" | "routine";

export type Sensitivity = "public" | "personal" | "private" | "secret" | "ephemeral";
export type MemoryScope = "global" | "workspace" | "conversation";

export interface MemoryRememberRequest {
  namespace: string;
  workspace_id: string;
  content: string;
  kind: MemoryKind;
  sensitivity: Sensitivity;
  scope: MemoryScope;
  scope_key?: string | null;
  importance?: number;
  confidence?: number;
  pinned?: boolean;
  ttl_seconds?: number | null;
}

export interface MemoryRecallRequest {
  namespace: string;
  workspace_id: string;
  scope_key?: string | null;
  query?: string;
  limit?: number;
  as_of?: number | null;
  allow_private?: boolean;
  allow_secret?: boolean;
}

export interface MemoryDto {
  id: string;
  namespace: string;
  workspace_id: string;
  kind: MemoryKind;
  content: string;
  sensitivity: Sensitivity;
  scope: MemoryScope;
  scope_key?: string | null;
  importance: number;
  confidence: number;
  pinned: boolean;
  created_at: number;
  updated_at: number;
}

export interface ErrorPayload { code: string; message: string; }

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function parseEnvelope(value: unknown): Envelope {
  if (!isObject(value)) throw new Error("envelope must be an object");
  const allowed = new Set(["version", "id", "kind", "correlation_id", "payload"]);
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) throw new Error(`unknown envelope field: ${key}`);
  }
  if (value.version !== PROTOCOL_VERSION) throw new Error("unsupported protocol version");
  if (typeof value.id !== "string" || !value.id.trim()) throw new Error("invalid envelope id");
  if (typeof value.kind !== "string" || !value.kind.trim()) throw new Error("invalid envelope kind");
  if (
    value.correlation_id !== undefined &&
    value.correlation_id !== null &&
    (typeof value.correlation_id !== "string" || !value.correlation_id.trim())
  ) {
    throw new Error("invalid correlation_id");
  }
  if (!Object.prototype.hasOwnProperty.call(value, "payload")) {
    throw new Error("missing envelope payload");
  }
  return value as unknown as Envelope;
}

export function parseAuthenticatedFrame(value: unknown): AuthenticatedFrame {
  if (!isObject(value)) throw new Error("authenticated frame must be an object");
  if (Object.keys(value).sort().join(",") !== "envelope,token") {
    throw new Error("authenticated frame must contain exactly token and envelope");
  }
  if (typeof value.token !== "string" || !value.token.trim()) {
    throw new Error("invalid authentication token");
  }
  return { token: value.token, envelope: parseEnvelope(value.envelope) };
}


export type EffectClass =
  | "pure" | "read" | "write" | "destructive" | "external_side_effect" | "privileged";

export interface ResourceRef {
  uri: string;
  revision?: string | null;
  digest?: string | null;
}

export interface EvidenceRef {
  source: ResourceRef;
  observed_at: number;
  confidence?: number;
  note?: string | null;
}

export interface CapabilitySet {
  protocol: string;
  capabilities: string[];
}

export interface ChangeOperation {
  op: string;
  target: string;
  value?: unknown;
  effect: EffectClass;
  evidence?: EvidenceRef[];
}

export interface ChangeSet {
  id: string;
  domain: string;
  base_revision?: string | null;
  operations: ChangeOperation[];
  metadata?: Record<string, unknown>;
}

export type ValidationSeverity = "info" | "warning" | "error";
export interface ValidationIssue {
  code: string;
  message: string;
  severity: ValidationSeverity;
  path?: string | null;
}

export interface SurfaceComponent {
  id: string;
  component: string;
  props?: Record<string, unknown>;
  children?: string[];
}

export interface Surface {
  id: string;
  revision: number;
  catalog_id: string;
  root: string;
  components?: SurfaceComponent[];
  state?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface SurfacePatch {
  surface_id: string;
  base_revision: number;
  operations: ChangeOperation[];
}

export interface SurfaceAction {
  surface_id: string;
  component_id: string;
  action: string;
  context?: Record<string, unknown>;
}

export interface RendererCapabilities {
  surface_protocol: string;
  catalogs: string[];
  components: string[];
  features?: string[];
  max_depth?: number;
  max_nodes?: number;
}

export interface BackendResource {
  id: string;
  kind: string;
  spec?: Record<string, unknown>;
}

export interface BackendModule {
  id: string;
  revision: number;
  metadata?: Record<string, unknown>;
  resources: BackendResource[];
}

export interface BackendPlan {
  backend_id: string;
  base_revision: number;
  changeset: ChangeSet;
  affected_resources?: ResourceRef[];
  issues?: ValidationIssue[];
}


export interface MemoryManageRequest {
  operation: string;
  arguments?: Record<string, unknown>;
}


// Agentic protocol contracts ---------------------------------------------------
export type ContextKind =
  | "SYSTEM_INSTRUCTION" | "USER_INTENT" | "MEMORY_RECALL" | "MEMORY_CORRECTION"
  | "SKILL" | "PROJECT_GUIDELINE" | "HARNESS_KNOWLEDGE" | "REPOSITORY_MAP"
  | "FILE_EVIDENCE" | "SEARCH_EVIDENCE" | "TOOL_SCHEMA" | "TOOL_RESULT"
  | "TOOL_RECEIPT" | "SUBAGENT_RESULT" | "VALIDATION_EVIDENCE" | "ERROR_EVIDENCE"
  | "COMPACTION_CHECKPOINT" | "OUTPUT_CONTRACT";
export type ContextStability = "BUILD" | "SESSION" | "TURN";
export type RecoveryMode = "NONE" | "EXACT" | "SOURCE_REF" | "RECOMPUTE";
export type CacheRegion = "FROZEN_PREFIX" | "SESSION_PREFIX" | "LIVE_ZONE" | "UNCACHED";
export type ContextTrust = "TRUSTED" | "UNTRUSTED_WORKSPACE" | "EXTERNAL";

export interface ContextRecoveryRef {
  artifact_id: string;
  sha256: string;
  original_bytes: number;
  token_estimate: number;
  media_type: string;
  recovery: RecoveryMode;
}
export interface ContextSegment {
  id: string;
  kind: ContextKind;
  source: string;
  trust: ContextTrust;
  stability: ContextStability;
  priority: number;
  sensitivity: string;
  recovery: RecoveryMode;
  cache_region: CacheRegion;
  lifecycle: string;
  ttl_turns?: number | null;
  provenance_digest: string;
  token_cost: number;
  body_ref: unknown;
}
export interface ContextEnvelope {
  schema_version: 1;
  epoch: string;
  segments: ContextSegment[];
}
export type EventDurability = "DURABLE" | "TRANSIENT" | "STREAM_START" | "STREAM_DELTA" | "STREAM_ABORT" | "SYNC" | "ERROR";
export interface AgentEvent {
  event_id: string;
  conversation_id: string;
  turn_id: string;
  parent_event_id?: string | null;
  seq: number;
  kind: string;
  source: string;
  timestamp: number;
  payload: unknown;
  durability: EventDurability;
}
export interface ExecutionBudget {
  max_model_calls: number;
  max_input_tokens: number;
  max_output_tokens: number;
  max_total_tokens: number;
  max_cost: number;
  max_duration_ms: number;
  max_tool_calls: number;
  max_subagents: number;
}
export interface BudgetLease {
  id: string;
  parent_budget_id: string;
  child_agent_id: string;
  token_cap: number;
  call_cap: number;
  cost_cap: number;
  reserved: Record<string, unknown>;
  consumed: Record<string, unknown>;
}
export interface ExecutionAuthoritySnapshot {
  policy_revision: string;
  autonomy_revision: string;
  approval_revision: string;
  workspace_id: string;
  conversation_id: string;
  turn_id: string;
  sandbox_profile: string;
  filesystem_caps: string[];
  network_caps: string[];
  executable_identity: string;
  approval_grant?: Record<string, unknown> | null;
}
export interface ContextEpoch {
  epoch_id: string;
  baseline_seq: number;
  memory_revision: string;
  repository_revision: string;
  skills_revision: string;
  plugins_revision: string;
  policy_revision: string;
  provider_revision: string;
  snapshot_digest: string;
}
export interface CompactionCheckpoint {
  objective: string;
  constraints: string[];
  decisions: string[];
  completed: string[];
  active: string[];
  blocked: string[];
  next_actions: string[];
  relevant_files: string[];
  validation_state: string[];
  recovery_refs: ContextRecoveryRef[];
}
export interface AgentLineage {
  agent_id: string;
  parent_agent_id?: string | null;
  parent_turn_id: string;
  root_task_id: string;
  generation: number;
  role: string;
  backend: string;
  model: string;
  context_fork_mode: string;
  isolation_mode: "WORKTREE" | "SHARED" | "RUNTIME";
  budget_lease_id: string;
}
export interface WorkspaceSnapshot {
  snapshot_id: string;
  parent_snapshot_id?: string | null;
  turn_id: string;
  created_at: number;
  changed_paths: string[];
  digest: string;
}
export type AgentRole = "DISCOVER" | "ARCHITECT" | "IMPLEMENT" | "VERIFY" | "REVIEW";
export interface SavedPermission {
  workspace_id: string;
  action: string;
  resource_pattern: string;
  executable_identity?: string | null;
  decision: "ALLOW" | "ASK" | "DENY";
}
export interface PluginCapabilities {
  tools: string[];
  providers: string[];
  skills: string[];
  hooks: string[];
  commands: string[];
  context_sources: string[];
  ui_extensions: string[];
}
export interface MemoryLifecycleEvent {
  event: string;
  namespace: string;
  workspace_id: string;
  source_id: string;
  source_revision: string;
  input_digest: string;
  source_kind: string;
  source_watermark: string;
}
export interface MemoryConsumptionReceipt {
  recall_trace_id: string;
  memory_id: string;
  consumer: string;
  purpose: string;
  presented: boolean;
  referenced: boolean;
  used_for_action: boolean;
  outcome: string;
  turn_id: string;
  consumed_at: number;
}
export interface MemoryJob {
  id: string;
  phase: string;
  source_id: string;
  source_revision: string;
  source_watermark: string;
  status: string;
  lease_owner?: string | null;
  lease_until?: number | null;
  attempt: number;
  next_retry_at?: number | null;
  input_digest: string;
  output_digest?: string | null;
  created_at: number;
  updated_at: number;
}
