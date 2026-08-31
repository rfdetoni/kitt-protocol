use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Default)]
#[serde(rename_all = "snake_case")]
pub enum ModelRoute {
    #[default]
    Auto,
    Fast,
    Heavy,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ModelTier {
    Fast,
    Heavy,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct RoutedAskRequest {
    pub text: String,
    #[serde(default)]
    pub locale: Option<String>,
    #[serde(default)]
    pub route: ModelRoute,
    #[serde(default = "default_true")]
    pub show_hud: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct RoutedAskResponse {
    pub text: String,
    pub tier: ModelTier,
    #[serde(default)]
    pub fallback_used: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct TranscribeRequest {
    pub path: String,
    #[serde(default)]
    pub locale: Option<String>,
    #[serde(default = "default_true")]
    pub show_hud: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct TranscribeResponse {
    pub text: String,
}

fn default_true() -> bool {
    true
}
