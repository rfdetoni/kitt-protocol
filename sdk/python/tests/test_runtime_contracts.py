import unittest

from kitt_protocol import (
    BenchmarkReport,
    CompressionNegotiation,
    GpuDeviceDescriptor,
    GpuIsolationMode,
    GpuLeaseRecord,
    GpuLeaseState,
    GpuVendor,
    MigrationMode,
    MigrationPhase,
    MigrationPlan,
    MountKind,
    MountMaterializationState,
    MountSourceSpec,
    SnapshotManifestV2,
    WorkerCapabilities,
)


class RuntimeContractsTest(unittest.TestCase):
    def test_runtime_contracts_construction(self) -> None:
        gpu = GpuDeviceDescriptor(
            uuid="AMD-0000:05:00.0",
            vendor=GpuVendor.AMD,
            isolation_mode=GpuIsolationMode.EXCLUSIVE,
            pci_address="0000:05:00.0",
            render_node="/dev/dri/renderD128",
            kfd_available=True,
            total_vram_bytes=536870912,
            free_vram_bytes=400000000,
        )
        comp = CompressionNegotiation(
            codecs=("zstd", "identity"),
            max_compressed_bytes=67108864,
            max_decompressed_bytes=67108864,
            window_log_max=20,
            adaptive_min_bytes=4096,
        )
        worker = WorkerCapabilities(
            worker_id="wk-1",
            name="local-amd",
            os="linux",
            arch="x86_64",
            version="0.4.47",
            available=True,
            state="UNBOUND",
            cpu_millis=4000,
            memory_bytes=2147483648,
            pids_limit=256,
            compression=comp,
            last_heartbeat_at=1700000000,
            gpus=(gpu,),
            mount_aliases=("repo",),
            features=("zstd_binary", "cas_v2"),
        )
        self.assertEqual(worker.gpus[0].vendor, GpuVendor.AMD)

        lease = GpuLeaseRecord(
            lease_id="lease-1",
            gpu_uuid=gpu.uuid,
            owner_runtime_id="rt-1",
            worker_id=worker.worker_id,
            mode=GpuIsolationMode.VRAM_QUOTA,
            state=GpuLeaseState.ACTIVE,
            updated_at=1700000001,
            reserved_vram_bytes=128000000,
        )
        self.assertEqual(lease.state, GpuLeaseState.ACTIVE)

        mount = MountSourceSpec(
            kind=MountKind.GITHUB,
            alias="repo",
            mount_path="/mnt/kitt/repo",
            read_only=True,
            state=MountMaterializationState.READY,
            digest="0" * 64,
            repository="rfdetoni/kitt",
            commit_sha="a" * 40,
        )
        self.assertTrue(mount.read_only)

        snap = SnapshotManifestV2(
            version=2,
            snapshot_id="snap-1",
            migration_mode=MigrationMode.COLD,
            image="alpine@sha256:" + "a" * 64,
            image_digest="sha256:" + "a" * 64,
            cpu_millis=1000,
            memory_bytes=268435456,
            pids_limit=64,
            manifest_sha256="b" * 64,
            created_at=1700000002,
        )
        self.assertEqual(snap.version, 2)

        plan = MigrationPlan(
            migration_id="mig-1",
            conversation_id="conv-1",
            source_worker_id="wk-1",
            target_worker_id="wk-2",
            mode=MigrationMode.WARM,
            phase=MigrationPhase.VERIFY_TARGET,
            compatible=True,
            updated_at=1700000003,
        )
        self.assertEqual(plan.mode, MigrationMode.WARM)

        bench = BenchmarkReport(
            schema_version=1,
            os="linux",
            arch="x86_64",
            version="0.4.47",
            backend="docker",
            cpu={},
            ram={},
            gpu={},
            network={},
            runtime={},
            chunking={},
        )
        self.assertEqual(bench.schema_version, 1)


if __name__ == "__main__":
    unittest.main()
