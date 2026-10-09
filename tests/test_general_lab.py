import json
import time
import pytest

from fastapi.testclient import TestClient

from app import create_app
from agents.test_generator_agent import TestGeneratorAgent
from services.general_suite import objectives
from services.offline_gateway import OfflineGateway
from schemas.contracts import category_identifier


def test_live_category_formatting_accepts_matching_label_and_rejects_wrong_mapping():
    assert category_identifier('LLM01:2026: Prompt Injection') == 'LLM01:2026'
    with pytest.raises(ValueError):
        category_identifier('LLM01:2026: Excessive Agency')
    with pytest.raises(ValueError):
        category_identifier('LLM01:2025')


def general_target(endpoint):
    return {
        'application': {'name': 'Workspace assistant', 'purpose': 'Explain the workspace retention policy.',
                        'requirements': 'The retention period is 30 days. Cite Workspace policy. Do not modify records.'},
        'integration': {'rag_enabled': False, 'tools_enabled': False, 'conversation_memory': False},
        'testing_scope': {'authorized': True, 'environment': 'Local development', 'allowed_endpoints': [endpoint]},
        'adapter': {'kind': 'http', 'endpoint': endpoint},
    }


def test_general_catalog_has_200_unique_cases_without_campus_contracts():
    target = general_target('http://127.0.0.1:8001/api/chat')
    plan = objectives({'target': target})
    assert not {'RAG', 'Tools', 'Memory'} & {o['component'] for o in plan['objectives']}
    cases, _ = TestGeneratorAgent(OfflineGateway()).generate(target, plan, 200, 50)
    assert len(cases) == 200
    assert len({json.dumps(c['turns']) for c in cases}) == 200
    assert all(c['turns'][0]['user'] == 'test-user' for c in cases)
    assert all(c['assertions'][0]['kind'] == 'subjective' for c in cases)
    assert not any('student-' in json.dumps(c) or 'CANARY' in json.dumps(c) for c in cases)


def test_general_run_retains_actual_http_evidence_and_agent_reviews(tmp_path, general_url):
    with TestClient(create_app(tmp_path)) as client:
        target = client.post('/api/targets', json=general_target(general_url)).json()
        probe = client.post('/api/targets/' + target['id'] + '/probe').json()
        assert probe['connected'] and probe['status'] == 200
        assert '30 days' in probe['response_preview']
        result = client.post('/api/runs', json={'target_id': target['id'], 'mode': 'offline',
                            'limits': {'max_tests': 20, 'requests_per_second': 50, 'price_per_million': 0}})
        assert result.status_code == 201, result.text
        run_id = result.json()['id']
        client.post('/api/runs/' + run_id + '/start').raise_for_status()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            run = client.get('/api/runs/' + run_id).json()
            if run['report']:
                break
            time.sleep(.05)
        assert run['status'] == 'completed'
        assert run['report']['counts']['INCONCLUSIVE'] == 20
        assert run['report']['target_engine'] == 'external'
        assert run['usage']['target_requests'] == 20
        assert all(e['turns'][0]['status'] == 200 for e in run['executions'])
        events = client.get('/api/runs/' + run_id + '/trace').json()['events']
        expected = {a['name'] for a in client.get('/api/agents').json()['agents']}
        assert expected <= {e['agent'] for e in events}
        assert any(e['activity'] == 'working' for e in events)
        reviews = [e for e in events if e['activity'] == 'review']
        assert len(reviews) >= 5 and all(e['evidence']['passed'] for e in reviews)
        assert run['report']['agent_reviews']
        retest = client.post('/api/runs/' + run_id + '/retest').json()
        assert retest['status'] == 'created'
        assert retest['cases'] == run['cases'] and retest['plan'] == run['plan']
        assert retest['source_run_id'] == run_id and retest['usage'] is None
        assert retest['config']['limits']['max_tests'] == 20
        assert client.post('/api/runs/' + retest['id'] + '/retest').status_code == 409
    with TestClient(create_app(tmp_path)) as restarted:
        assert restarted.get('/api/runs/' + run_id + '/trace').json()['events'] == events


def test_connection_probe_requires_authorization_before_dispatch(tmp_path, general_url, monkeypatch):
    from agents.execution_agent import ExecutionAgent
    async def forbidden(*args, **kwargs):
        raise AssertionError('An unauthorized target must not receive a probe')
    monkeypatch.setattr(ExecutionAgent, 'execute', forbidden)
    target = general_target(general_url)
    target['testing_scope']['authorized'] = False
    with TestClient(create_app(tmp_path)) as client:
        saved = client.post('/api/targets', json=target).json()
        assert client.post('/api/targets/' + saved['id'] + '/probe').status_code == 422
