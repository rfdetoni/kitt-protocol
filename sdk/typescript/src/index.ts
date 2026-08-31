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
  importance?: number;
  confidence?: number;
  pinned?: boolean;
  ttl_seconds?: number | null;
}

export interface MemoryRecallRequest {
  namespace: string;
  workspace_id: string;
  query?: string;
  limit?: number;
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
