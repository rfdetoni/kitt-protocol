from __future__ import annotations

import json
from pathlib import Path
import unittest

from kitt_protocol import (
    ASSISTANT_ASK_REQUEST,
    AuthenticatedFrame,
    Envelope,
    MemoryRememberRequest,
    ProtocolError,
    SYSTEM_PING_REQUEST,
)

ROOT = Path(__file__).resolve().parents[3]


class ProtocolModelsTest(unittest.TestCase):
    def test_shared_invalid_wire_corpus(self):
        for raw in json.loads((ROOT / "fixtures/decoding-invalid.json").read_text()):
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                Envelope.loads(raw)
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                AuthenticatedFrame.loads('{"token":"test","envelope":' + raw + '}')
        valid = '{"version":1,"id":"x","kind":"system.ping.request","payload":null}'
        with self.assertRaises(ProtocolError):
            Envelope.loads(valid.encode("utf-16"))
        with self.assertRaises(ProtocolError):
            Envelope.loads(b"\xff")
        with self.assertRaises(ValueError):
            Envelope(kind="test", payload=float("nan")).dumps()

    def test_fixture_request_and_response(self):
        request = AuthenticatedFrame.loads(
            (ROOT / "fixtures/v1/assistant-ask-request.json").read_bytes()
        )
        self.assertEqual(ASSISTANT_ASK_REQUEST, request.envelope.kind)
        self.assertEqual("req-ask-001", request.envelope.id)
        response = Envelope.loads(
            (ROOT / "fixtures/v1/assistant-ask-response.json").read_bytes()
        )
        self.assertEqual("req-ask-001", response.correlation_id)

    def test_strict_unknown_fields(self):
        raw = json.dumps({
            "version": 1,
            "id": "x",
            "kind": SYSTEM_PING_REQUEST,
            "payload": {},
            "legacy_command": "ping",
        })
        with self.assertRaises(ProtocolError):
            Envelope.loads(raw)

    def test_wrong_version_rejected(self):
        raw = json.dumps({
            "version": 2,
            "id": "x",
            "kind": SYSTEM_PING_REQUEST,
            "payload": {},
        })
        with self.assertRaises(ProtocolError):
            Envelope.loads(raw)

    def test_memory_remember_requires_security_scope(self):
        with self.assertRaises(TypeError):
            MemoryRememberRequest(
                namespace="agent-cli",
                workspace_id="workspace",
                content="fact",
                kind="technical_fact",
            )
        request = MemoryRememberRequest(
            namespace="agent-cli",
            workspace_id="workspace",
            content="fact",
            kind="technical_fact",
            sensitivity="private",
            scope="workspace",
        )
        self.assertEqual("private", request.sensitivity)
        self.assertEqual("workspace", request.scope)

    def test_context_envelope_round_trip(self):
        from kitt_protocol import (
            CacheRegion,
            ContextEnvelope,
            ContextKind,
            ContextSegment,
            ContextStability,
            ContextTrust,
            RecoveryMode,
        )
        segment = ContextSegment(
            id="intent",
            kind=ContextKind.USER_INTENT,
            source="user",
            trust=ContextTrust.TRUSTED,
            stability=ContextStability.TURN,
            priority=100,
            sensitivity="private",
            recovery=RecoveryMode.NONE,
            cache_region=CacheRegion.LIVE_ZONE,
            lifecycle="turn",
            provenance_digest="abc",
            token_cost=3,
            body_ref={"text": "implement"},
            ttl_turns=1,
        )
        envelope = ContextEnvelope(epoch="epoch-1", segments=(segment,))
        mapping = envelope.to_mapping()
        self.assertEqual(1, mapping["schema_version"])
        self.assertEqual("USER_INTENT", mapping["segments"][0]["kind"])

    def test_context_envelope_rejects_duplicate_ids(self):
        from kitt_protocol import (
            CacheRegion,
            ContextEnvelope,
            ContextKind,
            ContextSegment,
            ContextStability,
            ContextTrust,
            RecoveryMode,
        )
        segment = ContextSegment(
            id="dup",
            kind=ContextKind.TOOL_SCHEMA,
            source="host",
            trust=ContextTrust.TRUSTED,
            stability=ContextStability.BUILD,
            priority=90,
            sensitivity="normal",
            recovery=RecoveryMode.RECOMPUTE,
            cache_region=CacheRegion.FROZEN_PREFIX,
            lifecycle="build",
            provenance_digest="x",
            token_cost=1,
            body_ref={},
        )
        with self.assertRaises(ValueError):
            ContextEnvelope(epoch="epoch-1", segments=(segment, segment))

    def test_request_metadata_is_structured_and_validated(self):
        from kitt_protocol import KittRequestMetadata

        metadata = KittRequestMetadata(
            conversation_id="conversation-1",
            turn_id="turn-1",
            request_id="request-1",
            route="agent-loop",
            session_id="session-1",
        )
        self.assertEqual(
            {
                "conversation_id": "conversation-1",
                "turn_id": "turn-1",
                "request_id": "request-1",
                "route": "agent-loop",
                "session_id": "session-1",
            },
            metadata.to_mapping(),
        )
        with self.assertRaises(ValueError):
            KittRequestMetadata(
                conversation_id="",
                turn_id="turn-1",
                request_id="request-1",
                route="agent-loop",
            )

    def test_progressive_memory_contracts_are_budgeted(self):
        from kitt_protocol import (
            MEMORY_BASELINE_REQUEST,
            MEMORY_GET_REQUEST,
            MEMORY_SEARCH_REQUEST,
            MEMORY_TIMELINE_REQUEST,
            MemoryBaselineRequest,
            MemoryGetRequest,
            MemorySearchRequest,
            MemoryTimelineRequest,
        )

        search = MemorySearchRequest(
            namespace="agent-cli",
            workspace_id="ws",
            query="database rule",
            max_results=12,
            token_budget=256,
            include_provenance=False,
            exclude_ids=("mem-old",),
            include_context_hints=True,
        )
        timeline = MemoryTimelineRequest(
            namespace="agent-cli",
            workspace_id="ws",
            source_id="session-1",
            token_budget=128,
        )
        get = MemoryGetRequest(
            namespace="agent-cli",
            workspace_id="ws",
            ids=("mem-1", "mem-2"),
            token_budget=512,
        )
        baseline = MemoryBaselineRequest(
            namespace="agent-cli",
            workspace_id="ws",
            max_tokens=800,
            if_none_match="etag-1",
        )

        self.assertEqual("memory.search.request", MEMORY_SEARCH_REQUEST)
        self.assertEqual("memory.timeline.request", MEMORY_TIMELINE_REQUEST)
        self.assertEqual("memory.get.request", MEMORY_GET_REQUEST)
        self.assertEqual("memory.baseline.request", MEMORY_BASELINE_REQUEST)
        self.assertEqual(256, search.token_budget)
        self.assertEqual(("mem-old",), search.exclude_ids)
        self.assertTrue(search.include_context_hints)
        self.assertEqual("session-1", timeline.source_id)
        self.assertEqual(("mem-1", "mem-2"), get.ids)
        self.assertTrue(get.include_provenance)
        self.assertEqual("etag-1", baseline.if_none_match)

    def test_authenticated_frame_hides_token_in_repr(self):
        frame = AuthenticatedFrame(
            token="super-secret",
            envelope=Envelope(kind=SYSTEM_PING_REQUEST, payload={}),
        )
        self.assertNotIn("super-secret", repr(frame))


if __name__ == "__main__":
    unittest.main()
