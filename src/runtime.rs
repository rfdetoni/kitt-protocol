use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum GpuVendor {
    Nvidia,
    Amd,
    Intel,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum GpuIsolationMode {
    Exclusive,
    VramQuota,
    Mig,
    Shared,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum GpuLeaseState {
    Reserving,
    Active,
    Releasing,
    Released,
    Indeterminate,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum MigrationMode {
    Cold,
    Warm,
    Live,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum MigrationPhase {
    VerifyTarget,
    ReserveResources,
    QuiesceSource,
    Snapshot,
    Transfer,
    VerifyIntegrity,
    Restore,
    HealthCheck,
    SwapBinding,
    ReleaseSource,
    RolledBack,
    Failed,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum MountKind {
    Github,
    S3,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum MountMaterializationState {
    Pending,
    Ready,
    Stale,
    Error,
    Removed,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct GpuDeviceDescriptor {
    pub uuid: String,
    pub vendor: GpuVendor,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pci_address: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub render_node: Option<String>,
    #[serde(default)]
    pub kfd_available: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub total_vram_bytes: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub free_vram_bytes: Option<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub shared_memory_bytes: Option<u64>,
    #[serde(default)]
    pub mig_capable: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub compute_backend: Option<String>,
    pub isolation_mode: GpuIsolationMode,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct GpuLeaseRecord {
    pub lease_id: String,
    pub gpu_uuid: String,
    pub owner_runtime_id: String,
    pub worker_id: String,
    pub mode: GpuIsolationMode,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub reserved_vram_bytes: Option<u64>,
    pub state: GpuLeaseState,
    pub updated_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CompressionNegotiation {
    pub codecs: Vec<String>,
    pub max_compressed_bytes: u64,
    pub max_decompressed_bytes: u64,
    pub window_log_max: u8,
    pub adaptive_min_bytes: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct MountSourceSpec {
    pub kind: MountKind,
    pub alias: String,
    pub mount_path: String,
    pub read_only: bool,
    pub state: MountMaterializationState,
    pub digest: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub repository: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub commit_sha: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bucket: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub prefix: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct WorkerCapabilities {
    pub worker_id: String,
    pub name: String,
    pub os: String,
    pub arch: String,
    pub version: String,
    pub available: bool,
    pub state: String,
    pub cpu_millis: u64,
    pub memory_bytes: u64,
    pub pids_limit: u32,
    #[serde(default)]
    pub gpus: Vec<GpuDeviceDescriptor>,
    #[serde(default)]
    pub mount_aliases: Vec<String>,
    pub compression: CompressionNegotiation,
    #[serde(default)]
    pub features: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub latency_ms: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub throughput_mbps: Option<f64>,
    #[serde(default)]
    pub executions: u64,
    #[serde(default)]
    pub failures: u64,
    pub last_heartbeat_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SnapshotManifestV2 {
    pub version: u32,
    pub snapshot_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parent_sha256: Option<String>,
    pub migration_mode: MigrationMode,
    pub image: String,
    pub image_digest: String,
    pub cpu_millis: u64,
    pub memory_bytes: u64,
    pub pids_limit: u32,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub gpu_vendor: Option<GpuVendor>,
    #[serde(default)]
    pub gpu_count: u32,
    #[serde(default)]
    pub mount_aliases: Vec<String>,
    #[serde(default)]
    pub deleted_paths: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub writable_layer_digest: Option<String>,
    pub manifest_sha256: String,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct MigrationPlan {
    pub migration_id: String,
    pub conversation_id: String,
    pub source_worker_id: String,
    pub target_worker_id: String,
    pub mode: MigrationMode,
    pub phase: MigrationPhase,
    pub compatible: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub snapshot_sha256: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    pub updated_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct BenchmarkReport {
    pub schema_version: u32,
    pub os: String,
    pub arch: String,
    pub version: String,
    pub backend: String,
    pub cpu: Value,
    pub ram: Value,
    pub gpu: Value,
    pub network: Value,
    pub runtime: Value,
    pub chunking: Value,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn runtime_contracts_round_trip() {
        let gpu = GpuDeviceDescriptor {
            uuid: "AMD-0000:05:00.0".into(),
            vendor: GpuVendor::Amd,
            pci_address: Some("0000:05:00.0".into()),
            render_node: Some("/dev/dri/renderD128".into()),
            kfd_available: true,
            total_vram_bytes: Some(536_870_912),
            free_vram_bytes: Some(400_000_000),
            shared_memory_bytes: None,
            mig_capable: false,
            compute_backend: Some("drm".into()),
            isolation_mode: GpuIsolationMode::Exclusive,
        };
        let worker = WorkerCapabilities {
            worker_id: "wk-1".into(),
            name: "local-amd".into(),
            os: "linux".into(),
            arch: "x86_64".into(),
            version: "0.4.47".into(),
            available: true,
            state: "UNBOUND".into(),
            cpu_millis: 4000,
            memory_bytes: 2_147_483_648,
            pids_limit: 256,
            gpus: vec![gpu],
            mount_aliases: vec!["repo".into()],
            compression: CompressionNegotiation {
                codecs: vec!["zstd".into(), "identity".into()],
                max_compressed_bytes: 67_108_864,
                max_decompressed_bytes: 67_108_864,
                window_log_max: 20,
                adaptive_min_bytes: 4096,
            },
            features: vec!["zstd_binary".into(), "cas_v2".into()],
            latency_ms: Some(1.4),
            throughput_mbps: Some(850.0),
            executions: 0,
            failures: 0,
            last_heartbeat_at: 1_700_000_000,
        };
        let encoded = serde_json::to_vec(&worker).unwrap();
        let decoded: WorkerCapabilities = serde_json::from_slice(&encoded).unwrap();
        assert_eq!(decoded, worker);

        let lease = GpuLeaseRecord {
            lease_id: "lease-1".into(),
            gpu_uuid: "AMD-0000:05:00.0".into(),
            owner_runtime_id: "rt-1".into(),
            worker_id: "wk-1".into(),
            mode: GpuIsolationMode::VramQuota,
            reserved_vram_bytes: Some(128_000_000),
            state: GpuLeaseState::Active,
            updated_at: 1_700_000_001,
        };
        let lease_json = serde_json::to_vec(&lease).unwrap();
        assert_eq!(
            serde_json::from_slice::<GpuLeaseRecord>(&lease_json).unwrap(),
            lease
        );

        let plan = MigrationPlan {
            migration_id: "mig-1".into(),
            conversation_id: "conv-1".into(),
            source_worker_id: "wk-1".into(),
            target_worker_id: "wk-2".into(),
            mode: MigrationMode::Cold,
            phase: MigrationPhase::VerifyTarget,
            compatible: true,
            snapshot_sha256: None,
            error: None,
            updated_at: 1_700_000_002,
        };
        let plan_json = serde_json::to_vec(&plan).unwrap();
        assert_eq!(
            serde_json::from_slice::<MigrationPlan>(&plan_json).unwrap(),
            plan
        );
    }
}
