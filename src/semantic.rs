use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum EffectClass {
    Pure,
    Read,
    Write,
    Destructive,
    ExternalSideEffect,
    Privileged,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ResourceRef {
    pub uri: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub revision: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub digest: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct EvidenceRef {
    pub source: ResourceRef,
    pub observed_at: i64,
    #[serde(default = "default_confidence")]
    pub confidence: f32,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
}

fn default_confidence() -> f32 {
    1.0
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Default)]
#[serde(deny_unknown_fields)]
pub struct CapabilitySet {
    pub protocol: String,
    #[serde(default)]
    pub capabilities: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ChangeOperation {
    pub op: String,
    pub target: String,
    #[serde(default)]
    pub value: Value,
    pub effect: EffectClass,
    #[serde(default)]
    pub evidence: Vec<EvidenceRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ChangeSet {
    pub id: String,
    pub domain: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub base_revision: Option<String>,
    #[serde(default)]
    pub operations: Vec<ChangeOperation>,
    #[serde(default)]
    pub metadata: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ValidationSeverity {
    Info,
    Warning,
    Error,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ValidationIssue {
    pub code: String,
    pub message: String,
    pub severity: ValidationSeverity,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct SurfaceComponent {
    pub id: String,
    pub component: String,
    #[serde(default)]
    pub props: Value,
    #[serde(default)]
    pub children: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Surface {
    pub id: String,
    pub revision: u64,
    pub catalog_id: String,
    pub root: String,
    #[serde(default)]
    pub components: Vec<SurfaceComponent>,
    #[serde(default)]
    pub state: Value,
    #[serde(default)]
    pub metadata: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct SurfacePatch {
    pub surface_id: String,
    pub base_revision: u64,
    #[serde(default)]
    pub operations: Vec<ChangeOperation>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct SurfaceAction {
    pub surface_id: String,
    pub component_id: String,
    pub action: String,
    #[serde(default)]
    pub context: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct RendererCapabilities {
    pub surface_protocol: String,
    #[serde(default)]
    pub catalogs: Vec<String>,
    #[serde(default)]
    pub components: Vec<String>,
    #[serde(default)]
    pub features: Vec<String>,
    #[serde(default)]
    pub max_depth: usize,
    #[serde(default)]
    pub max_nodes: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct BackendResource {
    pub id: String,
    pub kind: String,
    #[serde(default)]
    pub spec: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct BackendModule {
    pub id: String,
    pub revision: u64,
    #[serde(default)]
    pub metadata: Value,
    #[serde(default)]
    pub resources: Vec<BackendResource>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct BackendPlan {
    pub backend_id: String,
    pub base_revision: u64,
    pub changeset: ChangeSet,
    #[serde(default)]
    pub affected_resources: Vec<ResourceRef>,
    #[serde(default)]
    pub issues: Vec<ValidationIssue>,
}
