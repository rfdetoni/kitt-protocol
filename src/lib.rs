use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;

pub const PROTOCOL_VERSION: u16 = 1;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Envelope {
    pub version: u16,
    pub id: String,
    pub kind: String,
    #[serde(default)]
    pub payload: Value,
}

impl Envelope {
    pub fn new(kind: impl Into<String>, payload: impl Serialize) -> serde_json::Result<Self> {
        Ok(Self {
            version: PROTOCOL_VERSION,
            id: Uuid::new_v4().to_string(),
            kind: kind.into(),
            payload: serde_json::to_value(payload)?,
        })
    }
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
#[serde(tag = "type", rename_all = "snake_case")]
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
pub struct AskResponse {
    pub text: String,
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

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum MemoryScope {
    Global,
    Workspace,
    Conversation,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct MemoryRememberRequest {
    pub namespace: String,
    pub workspace_id: String,
    pub content: String,
    pub kind: MemoryKind,
    pub sensitivity: Sensitivity,
    pub scope: MemoryScope,
    #[serde(default)]
    pub pinned: bool,
    #[serde(default)]
    pub ttl_seconds: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
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

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn envelope_round_trip() {
        let env = Envelope::new(
            "hud.event",
            HudEvent::Text {
                content: "Olá".into(),
                ttl_ms: 1000,
            },
        )
        .unwrap();
        let encoded = serde_json::to_string(&env).unwrap();
        let decoded: Envelope = serde_json::from_str(&encoded).unwrap();
        assert_eq!(decoded.version, PROTOCOL_VERSION);
        assert_eq!(decoded.kind, "hud.event");
    }
}
