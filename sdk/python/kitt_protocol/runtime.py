from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class GpuVendor(StrEnum):
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"


class GpuIsolationMode(StrEnum):
    EXCLUSIVE = "exclusive"
    VRAM_QUOTA = "vram_quota"
    MIG = "mig"
    SHARED = "shared"


class GpuLeaseState(StrEnum):
    RESERVING = "RESERVING"
    ACTIVE = "ACTIVE"
    RELEASING = "RELEASING"
    RELEASED = "RELEASED"
    INDETERMINATE = "INDETERMINATE"


class MigrationMode(StrEnum):
    COLD = "cold"
    WARM = "warm"
    LIVE = "live"


class MigrationPhase(StrEnum):
    VERIFY_TARGET = "VERIFY_TARGET"
    RESERVE_RESOURCES = "RESERVE_RESOURCES"
    QUIESCE_SOURCE = "QUIESCE_SOURCE"
    SNAPSHOT = "SNAPSHOT"
    TRANSFER = "TRANSFER"
    VERIFY_INTEGRITY = "VERIFY_INTEGRITY"
    RESTORE = "RESTORE"
    HEALTH_CHECK = "HEALTH_CHECK"
    SWAP_BINDING = "SWAP_BINDING"
    RELEASE_SOURCE = "RELEASE_SOURCE"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class MountKind(StrEnum):
    GITHUB = "github"
    S3 = "s3"


class MountMaterializationState(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    STALE = "STALE"
    ERROR = "ERROR"
    REMOVED = "REMOVED"


@dataclass(frozen=True)
class GpuDeviceDescriptor:
    uuid: str
    vendor: GpuVendor
    isolation_mode: GpuIsolationMode
    pci_address: str | None = None
    render_node: str | None = None
    kfd_available: bool = False
    total_vram_bytes: int | None = None
    free_vram_bytes: int | None = None
    shared_memory_bytes: int | None = None
    mig_capable: bool = False
    compute_backend: str | None = None


@dataclass(frozen=True)
class GpuLeaseRecord:
    lease_id: str
    gpu_uuid: str
    owner_runtime_id: str
    worker_id: str
    mode: GpuIsolationMode
    state: GpuLeaseState
    updated_at: int
    reserved_vram_bytes: int | None = None


@dataclass(frozen=True)
class CompressionNegotiation:
    codecs: tuple[str, ...]
    max_compressed_bytes: int
    max_decompressed_bytes: int
    window_log_max: int
    adaptive_min_bytes: int


@dataclass(frozen=True)
class MountSourceSpec:
    kind: MountKind
    alias: str
    mount_path: str
    read_only: bool
    state: MountMaterializationState
    digest: str
    repository: str | None = None
    commit_sha: str | None = None
    bucket: str | None = None
    prefix: str | None = None
    version_id: str | None = None


@dataclass(frozen=True)
class WorkerCapabilities:
    worker_id: str
    name: str
    os: str
    arch: str
    version: str
    available: bool
    state: str
    cpu_millis: int
    memory_bytes: int
    pids_limit: int
    compression: CompressionNegotiation
    last_heartbeat_at: int
    gpus: tuple[GpuDeviceDescriptor, ...] = ()
    mount_aliases: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    latency_ms: float | None = None
    throughput_mbps: float | None = None
    executions: int = 0
    failures: int = 0


@dataclass(frozen=True)
class SnapshotManifestV2:
    version: int
    snapshot_id: str
    migration_mode: MigrationMode
    image: str
    image_digest: str
    cpu_millis: int
    memory_bytes: int
    pids_limit: int
    manifest_sha256: str
    created_at: int
    parent_sha256: str | None = None
    gpu_vendor: GpuVendor | None = None
    gpu_count: int = 0
    mount_aliases: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()
    writable_layer_digest: str | None = None


@dataclass(frozen=True)
class MigrationPlan:
    migration_id: str
    conversation_id: str
    source_worker_id: str
    target_worker_id: str
    mode: MigrationMode
    phase: MigrationPhase
    compatible: bool
    updated_at: int
    snapshot_sha256: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class BenchmarkReport:
    schema_version: int
    os: str
    arch: str
    version: str
    backend: str
    cpu: dict[str, Any]
    ram: dict[str, Any]
    gpu: dict[str, Any]
    network: dict[str, Any]
    runtime: dict[str, Any]
    chunking: dict[str, Any]
