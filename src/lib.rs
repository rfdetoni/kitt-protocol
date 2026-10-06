use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
mod strict_json;

mod agentic;
pub use agentic::*;

mod multillm;
pub use multillm::{
    ModelRoute, ModelTier, RoutedAskRequest, RoutedAskResponse, TranscribeRequest,
    TranscribeResponse,
};

mod semantic;
pub use semantic::*;

pub const PROTOCOL_VERSION: u16 = 1;
pub const MAX_FRAME_BYTES: usize = 1024 * 1024;

pub mod kinds {
    pub const SYSTEM_PING_REQUEST: &str = "system.ping.request";
    pub const SYSTEM_PING_RESPONSE: &str = "system.ping.response";
    pub const SYSTEM_ERROR: &str = "system.error";
    pub const ASSISTANT_ASK_REQUEST: &str = "assistant.ask.request";
    pub const ASSISTANT_ASK_RESPONSE: &str = "assistant.ask.response";
    pub const ASSISTANT_ASK_ROUTED_REQUEST: &str = "assistant.ask_routed.request";
    pub const ASSISTANT_ASK_ROUTED_RESPONSE: &str = "assistant.ask_routed.response";
    pub const ASSISTANT_TRANSCRIBE_REQUEST: &str = "assistant.transcribe.request";
    pub const ASSISTANT_TRANSCRIBE_RESPONSE: &str = "assistant.transcribe.response";
    pub const ASSISTANT_REMEMBER_REQUEST: &str = "assistant.remember.request";
    pub const ASSISTANT_REMEMBER_RESPONSE: &str = "assistant.remember.response";
    pub const MEMORY_REMEMBER_REQUEST: &str = "memory.remember.request";
    pub const MEMORY_REMEMBER_RESPONSE: &str = "memory.remember.response";
    pub const MEMORY_RECALL_REQUEST: &str = "memory.recall.request";
    pub const MEMORY_RECALL_RESPONSE: &str = "memory.recall.response";
    pub const MEMORY_SEARCH_REQUEST: &str = "memory.search.request";
    pub const MEMORY_SEARCH_RESPONSE: &str = "memory.search.response";
    pub const MEMORY_TIMELINE_REQUEST: &str = "memory.timeline.request";
    pub const MEMORY_TIMELINE_RESPONSE: &str = "memory.timeline.response";
    pub const MEMORY_GET_REQUEST: &str = "memory.get.request";
    pub const MEMORY_GET_RESPONSE: &str = "memory.get.response";
    pub const MEMORY_BASELINE_REQUEST: &str = "memory.baseline.request";
    pub const MEMORY_BASELINE_RESPONSE: &str = "memory.baseline.response";
    pub const MEMORY_FORGET_REQUEST: &str = "memory.forget.request";
    pub const MEMORY_FORGET_RESPONSE: &str = "memory.forget.response";
    pub const MEMORY_MANAGE_REQUEST: &str = "memory.manage.request";
    pub const MEMORY_MANAGE_RESPONSE: &str = "memory.manage.response";
    pub const HUD_SUBSCRIBE_REQUEST: &str = "hud.subscribe.request";
    pub const HUD_SUBSCRIBE_RESPONSE: &str = "hud.subscribe.response";
    pub const HUD_IMAGE_REQUEST: &str = "hud.image.request";
    pub const HUD_IMAGE_RESPONSE: &str = "hud.image.response";
    pub const HUD_EVENT: &str = "hud.event";
    pub const WORKER_EXECUTE_REQUEST: &str = "worker.execute.request";
    pub const WORKER_EXECUTE_RESPONSE: &str = "worker.execute.response";
    pub const SETTINGS_CATALOG_REQUEST: &str = "settings.catalog.request";
    pub const SETTINGS_CATALOG_RESPONSE: &str = "settings.catalog.response";
    pub const SETTINGS_SNAPSHOT_REQUEST: &str = "settings.snapshot.request";
    pub const SETTINGS_SNAPSHOT_RESPONSE: &str = "settings.snapshot.response";
    pub const SETTINGS_VALIDATE_REQUEST: &str = "settings.validate.request";
    pub const SETTINGS_VALIDATE_RESPONSE: &str = "settings.validate.response";
    pub const SETTINGS_APPLY_REQUEST: &str = "settings.apply.request";
    pub const SETTINGS_APPLY_RESPONSE: &str = "settings.apply.response";
    pub const SETTINGS_HEALTH_REQUEST: &str = "settings.health.request";
    pub const SETTINGS_HEALTH_RESPONSE: &str = "settings.health.response";
    pub const CAPABILITIES_REQUEST: &str = "capabilities.request";
    pub const CAPABILITIES_RESPONSE: &str = "capabilities.response";
    pub const SURFACE_CREATE: &str = "surface.create";
    pub const SURFACE_PATCH: &str = "surface.patch";
    pub const SURFACE_DELETE: &str = "surface.delete";
    pub const SURFACE_ACTION: &str = "surface.action";
    pub const SURFACE_VALIDATION_FAILED: &str = "surface.validation_failed";
    pub const BACKEND_VALIDATE_REQUEST: &str = "backend.validate.request";
    pub const BACKEND_VALIDATE_RESPONSE: &str = "backend.validate.response";
    pub const BACKEND_PLAN_REQUEST: &str = "backend.plan.request";
    pub const BACKEND_PLAN_RESPONSE: &str = "backend.plan.response";
    pub const BACKEND_APPLY_REQUEST: &str = "backend.apply.request";
    pub const BACKEND_APPLY_RESPONSE: &str = "backend.apply.response";
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Envelope {
    pub version: u16,
    pub id: String,
    pub kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub correlation_id: Option<String>,
    #[serde(deserialize_with = "required_payload")]
    pub payload: Value,
}

fn required_payload<'de, D: serde::Deserializer<'de>>(deserializer: D) -> Result<Value, D::Error> {
    Value::deserialize(deserializer)
}

impl Envelope {
    pub fn new(kind: impl Into<String>, payload: impl Serialize) -> serde_json::Result<Self> {
        Ok(Self {
            version: PROTOCOL_VERSION,
            id: Uuid::new_v4().to_string(),
            kind: kind.into(),
            correlation_id: None,
            payload: serde_json::to_value(payload)?,
        })
    }

    pub fn response(
        kind: impl Into<String>,
        request_id: impl Into<String>,
        payload: impl Serialize,
    ) -> serde_json::Result<Self> {
        let mut envelope = Self::new(kind, payload)?;
        envelope.correlation_id = Some(request_id.into());
        Ok(envelope)
    }

    pub fn error(
        request_id: Option<&str>,
        code: impl Into<String>,
        message: impl Into<String>,
    ) -> Self {
        Self {
            version: PROTOCOL_VERSION,
            id: Uuid::new_v4().to_string(),
            kind: kinds::SYSTEM_ERROR.to_string(),
            correlation_id: request_id.map(str::to_string),
            payload: serde_json::to_value(ErrorPayload {
                code: code.into(),
                message: message.into(),
            })
            .unwrap_or(Value::Null),
        }
    }

    pub fn validate(&self) -> Result<(), String> {
        if self.version != PROTOCOL_VERSION {
            return Err(format!(
                "unsupported protocol version {}; expected {}",
                self.version, PROTOCOL_VERSION
            ));
        }
        if self.id.trim().is_empty() {
            return Err("envelope id is empty".into());
        }
        if self.kind.trim().is_empty() {
            return Err("envelope kind is empty".into());
        }
        if self
            .correlation_id
            .as_ref()
            .is_some_and(|value| value.trim().is_empty())
        {
            return Err("correlation_id cannot be empty".into());
        }
        Ok(())
    }

    pub fn decode(data: &[u8]) -> Result<Self, String> {
        if data.len() > MAX_FRAME_BYTES {
            return Err("frame_too_large".into());
        }
        let value: strict_json::StrictValue =
            serde_json::from_slice(data).map_err(|e| e.to_string())?;
        let envelope: Self = serde_json::from_value(value.0).map_err(|e| e.to_string())?;
        envelope.validate()?;
        Ok(envelope)
    }
}

#[derive(Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct AuthenticatedFrame {
    pub token: String,
    pub envelope: Envelope,
}

impl AuthenticatedFrame {
    pub fn new(token: impl Into<String>, envelope: Envelope) -> Result<Self, String> {
        let token = token.into();
        if token.trim().is_empty() {
            return Err("authentication token is empty".into());
        }
        envelope.validate()?;
        Ok(Self { token, envelope })
    }

    pub fn decode(data: &[u8]) -> Result<Self, String> {
        if data.len() > MAX_FRAME_BYTES {
            return Err("frame_too_large".into());
        }
        let value: strict_json::StrictValue =
            serde_json::from_slice(data).map_err(|e| e.to_string())?;
        let frame: Self = serde_json::from_value(value.0).map_err(|e| e.to_string())?;
        if frame.token.trim().is_empty() {
            return Err("authentication token is empty".into());
        }
        frame.envelope.validate()?;
        Ok(frame)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ErrorPayload {
    pub code: String,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum HudState {
    Listening,
    Thinking,
    Responding,
    Executing,
    Error,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "type", rename_all = "snake_case", deny_unknown_fields)]
pub enum HudEvent {
    Status {
        state: HudState,
        message: Option<String>,
    },
    Text {
        content: String,
        ttl_ms: u64,
    },
    Image {
        src: String,
        alt: Option<String>,
        ttl_ms: u64,
    },
    Hide,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct AskRequest {
    pub text: String,
    #[serde(default)]
    pub locale: Option<String>,
    #[serde(default = "default_true")]
    pub show_hud: bool,
}

fn default_true() -> bool {
    true
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct AskResponse {
    pub text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AssistantRememberRequest {
    pub text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct IdResponse {
    pub id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum MemoryKind {
    UserPreference,
    ProjectRule,
    ArchitectureDecision,
    TechnicalFact,
    WorkingPattern,
    FailedApproach,
    OpenIssue,
    ProjectState,
    Episodic,
    PersonalFact,
    Routine,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum Sensitivity {
    Public,
    Personal,
    Private,
    Secret,
    Ephemeral,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum MemoryScope {
    Global,
    Workspace,
    Conversation,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryRememberRequest {
    pub namespace: String,
    pub workspace_id: String,
    pub content: String,
    pub kind: MemoryKind,
    pub sensitivity: Sensitivity,
    pub scope: MemoryScope,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    #[serde(default = "default_importance")]
    pub importance: f32,
    #[serde(default = "default_confidence")]
    pub confidence: f32,
    #[serde(default)]
    pub pinned: bool,
    #[serde(default)]
    pub ttl_seconds: Option<u64>,
}
fn default_importance() -> f32 {
    0.8
}
fn default_confidence() -> f32 {
    1.0
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryRecallRequest {
    pub namespace: String,
    pub workspace_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    #[serde(default)]
    pub query: String,
    #[serde(default = "default_memory_limit")]
    pub limit: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub as_of: Option<i64>,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
}
fn default_memory_limit() -> usize {
    6
}

fn default_memory_max_results() -> usize {
    24
}
fn default_memory_search_budget() -> u64 {
    1200
}
fn default_memory_get_budget() -> u64 {
    2400
}
fn default_memory_baseline_budget() -> usize {
    800
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemorySearchRequest {
    pub namespace: String,
    pub workspace_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    #[serde(default)]
    pub query: String,
    #[serde(default = "default_memory_max_results")]
    pub max_results: usize,
    #[serde(default = "default_memory_search_budget")]
    pub token_budget: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub as_of: Option<i64>,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
    #[serde(default)]
    pub include_provenance: bool,
    #[serde(default)]
    pub exclude_ids: Vec<String>,
    #[serde(default)]
    pub include_context_hints: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryTimelineRequest {
    pub namespace: String,
    pub workspace_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub around: Option<i64>,
    #[serde(default = "default_memory_max_results")]
    pub limit: usize,
    #[serde(default = "default_memory_search_budget")]
    pub token_budget: u64,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
    #[serde(default)]
    pub include_provenance: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryGetRequest {
    pub namespace: String,
    pub workspace_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    pub ids: Vec<String>,
    #[serde(default = "default_memory_get_budget")]
    pub token_budget: u64,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
    #[serde(default = "default_true")]
    pub include_provenance: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryBaselineRequest {
    pub namespace: String,
    pub workspace_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    #[serde(default = "default_memory_baseline_budget")]
    pub max_tokens: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub as_of: Option<i64>,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub if_none_match: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryBaselineEntry {
    pub memory_id: String,
    pub section: String,
    pub content: String,
    pub pinned: bool,
    pub score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryBaselineResponse {
    #[serde(default)]
    pub not_modified: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub etag: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub baseline_revision: Option<u64>,
    #[serde(default)]
    pub entries: Vec<MemoryBaselineEntry>,
    #[serde(default)]
    pub estimated_tokens: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub dropped_count: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub budget_pressure: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemorySearchHit {
    pub id: String,
    pub kind: MemoryKind,
    pub snippet: String,
    pub sensitivity: Sensitivity,
    pub scope: MemoryScope,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    pub importance: f32,
    pub confidence: f32,
    pub token_estimate: u64,
    #[serde(default)]
    pub provenance: Vec<ResourceRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryContextHint {
    pub id: String,
    pub path: String,
    pub summary: String,
    pub generation: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemorySearchCommon {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sensitivity: Option<Sensitivity>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope: Option<MemoryScope>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemorySearchResponse {
    pub recall_trace_id: String,
    pub hits: Vec<MemorySearchHit>,
    pub consumed_tokens: u64,
    pub has_more: bool,
    #[serde(default)]
    pub context_hints: Vec<MemoryContextHint>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub common: Option<MemorySearchCommon>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryTimelineHit {
    pub id: String,
    pub kind: MemoryKind,
    pub snippet: String,
    pub updated_at: i64,
    pub sensitivity: Sensitivity,
    pub scope: MemoryScope,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    pub importance: f32,
    pub confidence: f32,
    pub token_estimate: u64,
    #[serde(default)]
    pub provenance: Vec<ResourceRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryTimelineResponse {
    pub recall_trace_id: String,
    pub hits: Vec<MemoryTimelineHit>,
    pub consumed_tokens: u64,
    pub has_more: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryHydratedRecord {
    pub record: MemoryDto,
    #[serde(default)]
    pub provenance: Vec<ResourceRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryGetResponse {
    pub recall_trace_id: String,
    pub records: Vec<MemoryHydratedRecord>,
    pub consumed_tokens: u64,
    #[serde(default)]
    pub truncated_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct MemoryForgetRequest {
    pub id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct DeleteResponse {
    pub deleted: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryRecallResponse {
    pub records: Vec<MemoryDto>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryDto {
    pub id: String,
    pub namespace: String,
    pub workspace_id: String,
    pub kind: MemoryKind,
    pub content: String,
    pub sensitivity: Sensitivity,
    pub scope: MemoryScope,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scope_key: Option<String>,
    pub importance: f32,
    pub confidence: f32,
    pub pinned: bool,
    pub created_at: i64,
    pub updated_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct HudImageRequest {
    pub src: String,
    #[serde(default)]
    pub alt: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ShownResponse {
    pub shown: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct StatusResponse {
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct WorkerExecuteRequest {
    pub capability: String,
    #[serde(default)]
    pub payload: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct WorkerExecuteResponse {
    #[serde(default)]
    pub payload: Value,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn envelope_round_trip_and_correlation() {
        let request = Envelope::new(
            kinds::ASSISTANT_ASK_REQUEST,
            AskRequest {
                text: "Olá".into(),
                locale: Some("pt-BR".into()),
                show_hud: true,
            },
        )
        .unwrap();
        let response = Envelope::response(
            kinds::ASSISTANT_ASK_RESPONSE,
            request.id.clone(),
            AskResponse {
                text: "Olá!".into(),
            },
        )
        .unwrap();
        assert_eq!(
            response.correlation_id.as_deref(),
            Some(request.id.as_str())
        );
        response.validate().unwrap();
    }

    #[test]
    fn rejects_unknown_version() {
        let mut env = Envelope::new(kinds::SYSTEM_PING_REQUEST, serde_json::json!({})).unwrap();
        env.version = 99;
        assert!(env.validate().is_err());
    }

    #[test]
    fn canonical_fixture_parses() {
        let frame =
            AuthenticatedFrame::decode(include_bytes!("../fixtures/v1/assistant-ask-request.json"))
                .unwrap();
        assert_eq!(frame.envelope.kind, kinds::ASSISTANT_ASK_REQUEST);
        assert_eq!(frame.envelope.id, "req-ask-001");

        let response =
            Envelope::decode(include_bytes!("../fixtures/v1/assistant-ask-response.json")).unwrap();
        assert_eq!(response.correlation_id.as_deref(), Some("req-ask-001"));
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryManageRequest {
    pub operation: String,
    #[serde(default)]
    pub arguments: Value,
}
