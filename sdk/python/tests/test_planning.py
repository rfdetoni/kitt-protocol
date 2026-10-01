import json
import unittest
from pathlib import Path
from kitt_protocol import HostExecutionState, KittRequestMetadata, PlanProposal, PlanTaskProposal, SubagentReport


class PlanningContracts(unittest.TestCase):
    def test_shared_fixture_round_trip(self):
        fixture = json.loads((Path(__file__).resolve().parents[3] / 'fixtures/agentic/planning.json').read_text())
        self.assertEqual(KittRequestMetadata(**fixture['metadata']).to_mapping(), fixture['metadata'])
        self.assertEqual(HostExecutionState(**fixture['host_execution']).to_mapping(), fixture['host_execution'])
        proposal = fixture['proposal']
        self.assertEqual(PlanProposal(proposal['objective'], tuple(PlanTaskProposal(**t) for t in proposal['tasks'])).to_mapping(), proposal)
        self.assertEqual(SubagentReport(**fixture['report']).to_mapping(), fixture['report'])

    def test_malformed_metadata_and_host_facts(self):
        for kwargs in ({'agent_role':'ORCHESTRATOR'}, {'task_id':''}, {'parent_request_id':'a'*257}):
            with self.assertRaises(ValueError):
                KittRequestMetadata('c', 't', 'r', 'agent-loop', **kwargs)
        for kwargs in ({'mutation_count':-1}, {'tool_call_count':True}, {'verified_mutation_count':1}, {'completion_ready':'yes'}):
            with self.assertRaises(ValueError):
                HostExecutionState('c', 't', **kwargs)
