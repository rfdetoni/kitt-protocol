use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;

mod multillm;
pub use multillm::{
    ModelRoute, ModelTier, RoutedAskRequest, RoutedAskResponse, TranscribeRequest,
    TranscribeResponse,
};

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
    pub const MEMORY_FORGET_REQUEST: &str = "memory.forget.request";
    pub const MEMORY_FORGET_RESPONSE: &str = "memory.forget.response";
    pub const HUD_SUBSCRIBE_REQUEST: &str = "hud.subscribe.request";
    pub const HUD_SUBSCRIBE_RESPONSE: &str = "hud.subscribe.response";
    pub const HUD_IMAGE_REQUEST: &str = "hud.image.request";
    pub const HUD_IMAGE_RESPONSE: &str = "hud.image.response";
    pub const HUD_EVENT: &str = "hud.event";
    pub const WORKER_EXECUTE_REQUEST: &str = "worker.execute.request";
    pub const WORKER_EXECUTE_RESPONSE: &str = "worker.execute.response";
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Envelope {
    pub version: u16,
    pub id: String,
    pub kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub correlation_id: Option<String>,
    #[serde(default)]
    pub payload: Value,
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
        let envelope: Self = serde_json::from_slice(data).map_err(|e| e.to_string())?;
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
        let frame: Self = serde_json::from_slice(data).map_err(|e| e.to_string())?;
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
    #[serde(default)]
    pub query: String,
    #[serde(default = "default_memory_limit")]
    pub limit: usize,
    #[serde(default)]
    pub allow_private: bool,
    #[serde(default)]
    pub allow_secret: bool,
}
fn default_memory_limit() -> usize {
    6
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
