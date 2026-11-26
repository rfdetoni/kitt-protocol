export type GpuVendor = "nvidia" | "amd" | "intel";
export type GpuIsolationMode = "exclusive" | "vram_quota" | "mig" | "shared";
export type GpuLeaseState = "RESERVING" | "ACTIVE" | "RELEASING" | "RELEASED" | "INDETERMINATE";
export type MigrationMode = "cold" | "warm" | "live";
export type MigrationPhase =
  | "VERIFY_TARGET"
  | "RESERVE_RESOURCES"
  | "QUIESCE_SOURCE"
  | "SNAPSHOT"
  | "TRANSFER"
  | "VERIFY_INTEGRITY"
  | "RESTORE"
  | "HEALTH_CHECK"
  | "SWAP_BINDING"
  | "RELEASE_SOURCE"
  | "ROLLED_BACK"
  | "FAILED";
export type MountKind = "github" | "s3";
export type MountMaterializationState = "PENDING" | "READY" | "STALE" | "ERROR" | "REMOVED";

export interface GpuDeviceDescriptor {
  uuid: string;
  vendor: GpuVendor;
  pci_address?: string | null;
  render_node?: string | null;
  kfd_available: boolean;
  total_vram_bytes?: number | null;
  free_vram_bytes?: number | null;
  shared_memory_bytes?: number | null;
  mig_capable: boolean;
  compute_backend?: string | null;
  isolation_mode: GpuIsolationMode;
}

export interface GpuLeaseRecord {
  lease_id: string;
  gpu_uuid: string;
  owner_runtime_id: string;
  worker_id: string;
  mode: GpuIsolationMode;
  reserved_vram_bytes?: number | null;
  state: GpuLeaseState;
  updated_at: number;
}

export interface CompressionNegotiation {
  codecs: string[];
  max_compressed_bytes: number;
  max_decompressed_bytes: number;
  window_log_max: number;
  adaptive_min_bytes: number;
}

export interface MountSourceSpec {
  kind: MountKind;
  alias: string;
  mount_path: string;
  read_only: boolean;
  state: MountMaterializationState;
  digest: string;
  repository?: string | null;
  commit_sha?: string | null;
  bucket?: string | null;
  prefix?: string | null;
  version_id?: string | null;
}

export interface WorkerCapabilities {
  worker_id: string;
  name: string;
  os: string;
  arch: string;
  version: string;
  available: boolean;
  state: string;
  cpu_millis: number;
  memory_bytes: number;
  pids_limit: number;
  gpus: GpuDeviceDescriptor[];
  mount_aliases: string[];
  compression: CompressionNegotiation;
  features: string[];
  latency_ms?: number | null;
  throughput_mbps?: number | null;
  executions: number;
  failures: number;
  last_heartbeat_at: number;
}

export interface SnapshotManifestV2 {
  version: number;
  snapshot_id: string;
  parent_sha256?: string | null;
  migration_mode: MigrationMode;
  image: string;
  image_digest: string;
  cpu_millis: number;
  memory_bytes: number;
  pids_limit: number;
  gpu_vendor?: GpuVendor | null;
  gpu_count: number;
  mount_aliases: string[];
  deleted_paths: string[];
  writable_layer_digest?: string | null;
  manifest_sha256: string;
  created_at: number;
}

export interface MigrationPlan {
  migration_id: string;
  conversation_id: string;
  source_worker_id: string;
  target_worker_id: string;
  mode: MigrationMode;
  phase: MigrationPhase;
  compatible: boolean;
  snapshot_sha256?: string | null;
  error?: string | null;
  updated_at: number;
}

export interface BenchmarkReport {
  schema_version: number;
  os: string;
  arch: string;
  version: string;
  backend: string;
  cpu: Record<string, unknown>;
  ram: Record<string, unknown>;
  gpu: Record<string, unknown>;
  network: Record<string, unknown>;
  runtime: Record<string, unknown>;
  chunking: Record<string, unknown>;
}
