use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashSet;

pub const AGENTIC_SCHEMA_VERSION: u16 = 1;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ContextKind {
    SystemInstruction,
    UserIntent,
    MemoryRecall,
    MemoryCorrection,
    Skill,
    ProjectGuideline,
    HarnessKnowledge,
    RepositoryMap,
    FileEvidence,
    SearchEvidence,
    ToolSchema,
    ToolResult,
    ToolReceipt,
    SubagentResult,
    ValidationEvidence,
    ErrorEvidence,
    CompactionCheckpoint,
    OutputContract,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ContextStability {
    Build,
    Session,
    Turn,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum RecoveryMode {
    None,
    Exact,
    SourceRef,
    Recompute,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum CacheRegion {
    FrozenPrefix,
    SessionPrefix,
    LiveZone,
    Uncached,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ContextTrust {
    Trusted,
    UntrustedWorkspace,
    External,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ContextRecoveryRef {
    pub artifact_id: String,
    pub sha256: String,
    pub original_bytes: u64,
    pub token_estimate: u64,
    pub media_type: String,
    pub recovery: RecoveryMode,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ContextSegment {
    pub id: String,
    pub kind: ContextKind,
    pub source: String,
    pub trust: ContextTrust,
    pub stability: ContextStability,
    pub priority: i16,
    pub sensitivity: String,
    pub recovery: RecoveryMode,
    pub cache_region: CacheRegion,
    pub lifecycle: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ttl_turns: Option<u32>,
    pub provenance_digest: String,
    pub token_cost: u64,
    pub body_ref: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ContextEnvelope {
    pub schema_version: u16,
    pub epoch: String,
    pub segments: Vec<ContextSegment>,
}

impl ContextEnvelope {
    pub fn validate(&self) -> Result<(), String> {
        if self.schema_version != AGENTIC_SCHEMA_VERSION {
            return Err(format!(
                "unsupported agentic schema version {}",
                self.schema_version
            ));
        }
        if self.epoch.trim().is_empty() {
            return Err("context epoch is empty".into());
        }
        let mut ids = HashSet::new();
        for segment in &self.segments {
            if segment.id.trim().is_empty() {
                return Err("context segment id is empty".into());
            }
            if !ids.insert(segment.id.as_str()) {
                return Err(format!("duplicate context segment id {}", segment.id));
            }
            if segment.source.trim().is_empty() {
                return Err(format!("segment {} source is empty", segment.id));
            }
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EventDurability {
    Durable,
    Transient,
    StreamStart,
    StreamDelta,
    StreamAbort,
    Sync,
    Error,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct KittRequestMetadata {
    pub conversation_id: String,
    pub turn_id: String,
    pub request_id: String,
    pub route: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session_id: Option<String>,
}

impl KittRequestMetadata {
    pub fn validate(&self) -> Result<(), String> {
        for (name, value) in [
            ("conversation_id", self.conversation_id.as_str()),
            ("turn_id", self.turn_id.as_str()),
            ("request_id", self.request_id.as_str()),
            ("route", self.route.as_str()),
        ] {
            if value.trim().is_empty() {
                return Err(format!("{name} is required"));
            }
        }
        if self
            .session_id
            .as_deref()
            .is_some_and(|value| value.trim().is_empty())
        {
            return Err("session_id must be non-empty when present".into());
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct AgentEvent {
    pub event_id: String,
    pub conversation_id: String,
    pub turn_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parent_event_id: Option<String>,
    pub seq: u64,
    pub kind: String,
    pub source: String,
    pub timestamp: i64,
    pub payload: Value,
    pub durability: EventDurability,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum RunState {
    Idle,
    Running,
    Stopping,
    FollowupPending,
    Paused,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ExecutionBudget {
    pub max_model_calls: u64,
    pub max_input_tokens: u64,
    pub max_output_tokens: u64,
    pub max_total_tokens: u64,
    pub max_cost: f64,
    pub max_duration_ms: u64,
    pub max_tool_calls: u64,
    pub max_subagents: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct BudgetLease {
    pub id: String,
    pub parent_budget_id: String,
    pub child_agent_id: String,
    pub token_cap: u64,
    pub call_cap: u64,
    pub cost_cap: f64,
    pub reserved: Value,
    pub consumed: Value,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum PolicyDecision {
    Allow,
    Ask,
    Deny,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ExecutionAuthoritySnapshot {
    pub policy_revision: String,
    pub autonomy_revision: String,
    pub approval_revision: String,
    pub workspace_id: String,
    pub conversation_id: String,
    pub turn_id: String,
    pub sandbox_profile: String,
    pub filesystem_caps: Vec<String>,
    pub network_caps: Vec<String>,
    pub executable_identity: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub approval_grant: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ContextEpoch {
    pub epoch_id: String,
    pub baseline_seq: u64,
    pub memory_revision: String,
    pub repository_revision: String,
    pub skills_revision: String,
    pub plugins_revision: String,
    pub policy_revision: String,
    pub provider_revision: String,
    pub snapshot_digest: String,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum SegmentDisposition {
    Unchanged,
    Reconciled,
    Replaced,
    Invalidated,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CompactionCheckpoint {
    pub objective: String,
    pub constraints: Vec<String>,
    pub decisions: Vec<String>,
    pub completed: Vec<String>,
    pub active: Vec<String>,
    pub blocked: Vec<String>,
    pub next_actions: Vec<String>,
    pub relevant_files: Vec<String>,
    pub validation_state: Vec<String>,
    pub recovery_refs: Vec<ContextRecoveryRef>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum RuntimeBackend {
    Local,
    Docker,
    Podman,
    Kubernetes,
    Remote,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum IsolationMode {
    Worktree,
    Shared,
    Runtime,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AgentLineage {
    pub agent_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parent_agent_id: Option<String>,
    pub parent_turn_id: String,
    pub root_task_id: String,
    pub generation: u32,
    pub role: String,
    pub backend: String,
    pub model: String,
    pub context_fork_mode: String,
    pub isolation_mode: IsolationMode,
    pub budget_lease_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct WorkspaceSnapshot {
    pub snapshot_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parent_snapshot_id: Option<String>,
    pub turn_id: String,
    pub created_at: i64,
    pub changed_paths: Vec<String>,
    pub digest: String,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AgentRole {
    Discover,
    Architect,
    Implement,
    Verify,
    Review,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct MemoryLifecycleEvent {
    pub event: String,
    pub namespace: String,
    pub workspace_id: String,
    pub source_id: String,
    pub source_revision: String,
    pub input_digest: String,
    pub source_kind: String,
    pub source_watermark: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SavedPermission {
    pub workspace_id: String,
    pub action: String,
    pub resource_pattern: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub executable_identity: Option<String>,
    pub decision: PolicyDecision,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct PluginCapabilities {
    pub tools: Vec<String>,
    pub providers: Vec<String>,
    pub skills: Vec<String>,
    pub hooks: Vec<String>,
    pub commands: Vec<String>,
    pub context_sources: Vec<String>,
    pub ui_extensions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EvidenceOrigin {
    Human,
    Assistant,
    Subagent,
    Tool,
    Repository,
    Memory,
    Skill,
    Plugin,
    Harness,
    System,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryConsumptionReceipt {
    pub recall_trace_id: String,
    pub memory_id: String,
    pub consumer: String,
    pub purpose: String,
    pub presented: bool,
    pub referenced: bool,
    pub used_for_action: bool,
    pub outcome: String,
    pub turn_id: String,
    pub consumed_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct MemoryJob {
    pub id: String,
    pub phase: String,
    pub source_id: String,
    pub source_revision: String,
    pub source_watermark: String,
    pub status: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lease_owner: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lease_until: Option<i64>,
    pub attempt: u32,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub next_retry_at: Option<i64>,
    pub input_digest: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub output_digest: Option<String>,
    pub created_at: i64,
    pub updated_at: i64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn context_envelope_round_trip_and_validation() {
        let envelope = ContextEnvelope {
            schema_version: AGENTIC_SCHEMA_VERSION,
            epoch: "epoch-1".into(),
            segments: vec![ContextSegment {
                id: "intent".into(),
                kind: ContextKind::UserIntent,
                source: "user".into(),
                trust: ContextTrust::Trusted,
                stability: ContextStability::Turn,
                priority: 100,
                sensitivity: "private".into(),
                recovery: RecoveryMode::None,
                cache_region: CacheRegion::LiveZone,
                lifecycle: "turn".into(),
                ttl_turns: Some(1),
                provenance_digest: "abc".into(),
                token_cost: 4,
                body_ref: serde_json::json!({"text":"implement"}),
            }],
        };
        envelope.validate().unwrap();
        let wire = serde_json::to_vec(&envelope).unwrap();
        let decoded: ContextEnvelope = serde_json::from_slice(&wire).unwrap();
        assert_eq!(decoded, envelope);
        decoded.validate().unwrap();
    }

    #[test]
    fn request_metadata_round_trip_and_validation() {
        let metadata = KittRequestMetadata {
            conversation_id: "conversation-1".into(),
            turn_id: "turn-1".into(),
            request_id: "request-1".into(),
            route: "agent-loop".into(),
            session_id: Some("session-1".into()),
        };
        metadata.validate().unwrap();
        let wire = serde_json::to_vec(&metadata).unwrap();
        let decoded: KittRequestMetadata = serde_json::from_slice(&wire).unwrap();
        assert_eq!(decoded, metadata);

        let invalid = KittRequestMetadata {
            conversation_id: String::new(),
            ..metadata
        };
        assert!(invalid.validate().is_err());
    }

    #[test]
    fn duplicate_segment_ids_are_rejected() {
        let segment = ContextSegment {
            id: "dup".into(),
            kind: ContextKind::ToolSchema,
            source: "host".into(),
            trust: ContextTrust::Trusted,
            stability: ContextStability::Build,
            priority: 90,
            sensitivity: "normal".into(),
            recovery: RecoveryMode::Recompute,
            cache_region: CacheRegion::FrozenPrefix,
            lifecycle: "build".into(),
            ttl_turns: None,
            provenance_digest: "x".into(),
            token_cost: 1,
            body_ref: Value::Null,
        };
        let envelope = ContextEnvelope {
            schema_version: AGENTIC_SCHEMA_VERSION,
            epoch: "e".into(),
            segments: vec![segment.clone(), segment],
        };
        assert!(envelope.validate().is_err());
    }
}
