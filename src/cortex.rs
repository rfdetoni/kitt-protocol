//! Optional Cortex event-plane contracts. These types carry data, not authority.
//! Existing Agent capability policy and execution receipts remain canonical.

use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum CortexAutonomyTier {
    Green,
    Yellow,
    Red,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum CortexPreflightDecision {
    ReadOnly,
    RequireApproval,
    Deny,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CortexEvent {
    pub id: String,
    pub topic: String,
    pub source: String,
    pub severity: u8,
    pub untrusted: bool,
    pub sensitivity: String,
    pub payload: Value,
    pub created: f64,
    pub expires: f64,
}

impl CortexEvent {
    pub fn validate(&self) -> Result<(), String> {
        if self.id.is_empty() || self.id.len() > 128 {
            return Err("invalid Cortex event ID".into());
        }
        if !valid_name(&self.topic) || !valid_name(&self.source) {
            return Err("invalid Cortex topic/source".into());
        }
        if !(1..=5).contains(&self.severity) {
            return Err("invalid Cortex severity".into());
        }
        if !matches!(
            self.sensitivity.as_str(),
            "public" | "personal" | "private" | "secret" | "ephemeral"
        ) {
            return Err("invalid Cortex sensitivity".into());
        }
        if !self.payload.is_object() {
            return Err("Cortex event payload must be an object".into());
        }
        if !self.created.is_finite() || !self.expires.is_finite() || self.expires <= self.created {
            return Err("invalid Cortex event lifetime".into());
        }
        if serde_json::to_vec(&self.payload)
            .map_err(|e| e.to_string())?
            .len()
            > 16 * 1024
        {
            return Err("Cortex event payload exceeds 16 KiB".into());
        }
        Ok(())
    }
}

fn valid_name(value: &str) -> bool {
    value.len() <= 80
        && value.starts_with(|c: char| c.is_ascii_lowercase())
        && value.bytes().all(|b| {
            b.is_ascii_lowercase() || b.is_ascii_digit() || matches!(b, b'_' | b'-' | b'.')
        })
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CortexDelivery {
    #[serde(flatten)]
    pub event: CortexEvent,
    pub attempt: u8,
    pub lease_token: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CortexPreflight {
    pub tier: CortexAutonomyTier,
    pub decision: CortexPreflightDecision,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CortexContextProjection {
    pub value: String,
    pub source: String,
    pub sensitivity: String,
    pub observed: f64,
    pub expires: f64,
    pub revision: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CortexRouteAdvice {
    pub route: String,
    pub advisory: Option<Value>,
    pub status: String,
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn serialize_and_validate_external_event() {
        let example = json!({
            "id": "evt.42", "topic": "saas.error.500", "source": "external.webhook",
            "severity": 4, "untrusted": true, "sensitivity": "private",
            "payload": {"service": "billing"}, "created": 100.0, "expires": 200.0
        });
        let event: CortexEvent = serde_json::from_value(example.clone()).unwrap();
        event.validate().unwrap();
        assert_eq!(serde_json::to_value(event).unwrap(), example);
    }

    #[test]
    fn reject_unbounded_or_invalid_payloads() {
        let event: CortexEvent = serde_json::from_value(json!({
            "id": "evt.42", "topic": "saas.error.500", "source": "external.webhook",
            "severity": 6, "untrusted": true, "sensitivity": "private",
            "payload": {}, "created": 100.0, "expires": 200.0
        }))
        .unwrap();
        assert!(event.validate().is_err());
    }

    #[test]
    fn preserve_governor_wire_values() {
        let v: CortexPreflight = serde_json::from_value(json!({
            "tier": "YELLOW", "decision": "REQUIRE_APPROVAL", "reason": "cross-domain"
        }))
        .unwrap();
        assert_eq!(v.tier, CortexAutonomyTier::Yellow);
        assert_eq!(v.decision, CortexPreflightDecision::RequireApproval);
    }
}
