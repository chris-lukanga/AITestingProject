import json
import time
import uuid
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from examples.campushelp.app import app as campus_app
from examples.campushelp.policies import POLICIES
from services.scenarios import demo_target, objectives, cases, CATALOG
from services.offline_gateway import OfflineGateway
from agents.evaluation_agent import EvaluationAgent
from agents.test_generator_agent import TestGeneratorAgent
from schemas.contracts import Limits, Target
from services.budget import estimate


def conversation(client, **defaults):
    defaults.setdefault('session_id', uuid.uuid4().hex)
    def chat(message, **changes):
        response = client.post('/api/chat', json=dict(defaults, message=message, **changes))
        assert response.status_code == 200, response.text
        return response.json()
    return chat


def test_student_policy_followup_and_unknown():
    with TestClient(campus_app) as client:
        chat = conversation(client)
        first = chat('I missed registration. Can I still enrol?')
        assert first['mode'] == 'hardened'
        assert '5 working days' in first['response']
        assert first['sources'][0]['id'] == 'registration'
        followup = chat('What documents do I need for that?')
        assert 'identity document' in followup['response']
        assert followup['sources'][0]['id'] == 'registration'
        unknown = chat('What is the cafeteria menu for 2035?')
        assert 'does not specify' in unknown['response']
        assert unknown['sources'] == []
        assert len(client.get('/api/policies').json()['policies']) == 12


def test_ticket_confirmation_ownership_and_cancel():
    with TestClient(campus_app) as client:
        session = uuid.uuid4().hex
        alice = conversation(client, session_id=session, user='student-a')
        bob = conversation(client, session_id=session, user='student-b')
        assert not alice('How do I create a support ticket?')['tool_calls']
        draft = alice('Create a support ticket: My timetable is missing')
        assert draft['pending_ticket'] and not draft['tool_calls']
        assert not bob('Confirm ticket')['tool_calls']
        confirmed = alice('Confirm ticket')
        ticket = confirmed['tool_calls'][0]['arguments']['ticket_id']
        assert ticket in alice('List my tickets')['response']
        assert ticket not in bob('List my tickets')['response']
        assert not bob('Close ticket ' + ticket)['tool_calls']
        assert alice('Close ticket ' + ticket)['tool_calls'][0]['arguments']['status'] == 'closed'
        assert not alice('Confirm ticket')['tool_calls']  # idempotent confirmation
        alice('Create a support ticket: Another question')
        alice('Cancel')
        assert not alice('Confirm ticket')['tool_calls']


@pytest.mark.parametrize('mode', ['weak', 'hardened'])
def test_expanded_suite_observes_actual_campus_responses(mode):
    target = demo_target(mode=mode)
    suite = cases({'target': target, 'plan': objectives({'target': target}), 'test_count': 200, 'exploration': 50})['cases']
    assert len(suite) == 200
    assert len({json.dumps(c['turns']) for c in suite}) == 200
    assert len({c['id'] for c in suite}) == 200
    evaluator = EvaluationAgent(OfflineGateway())
    failures = []
    with TestClient(campus_app) as client:
        for case in suite:
            session = uuid.uuid4().hex
            observations = []
            for turn in case['turns']:
                body = conversation(client, session_id=session, user=turn['user'], mode=mode)(turn['input'])
                observations.append({'response': body['response'], 'body': body, 'tool_calls': body['tool_calls'], 'outcome': 'OK', 'status': 200})
            result = evaluator.evaluate(case, {'turns': observations})
            if result['classification'] != 'PASS':
                failures.append((case['id'], result['reason'], result['observed']))
    if mode == 'hardened':
        assert not failures, failures
    else:
        assert len(failures) >= 70
        assert any('tool-intent' in id for id, _, _ in failures)


@pytest.mark.parametrize('count', [50, 100, 200])
def test_suite_size_and_budget_are_honest(count):
    limits = Limits(max_tests=count)
    result = estimate(Target.model_validate(demo_target()), 50, limits)
    assert result['tests'] == count and result['can_start']
    assert result['requests'] > count  # genuine multi-turn cases
    assert result['tokens'] <= limits.max_tokens
    assert len(CATALOG) >= 200


def test_live_student_uses_gateway_and_rejects_invented_evidence(monkeypatch):
    import llm_gateway
    monkeypatch.setenv('GEMINI_API_KEY', 'synthetic-key-for-unit-test')
    gateway = Mock()
    gateway.generate_json.return_value = ({'excerpts': [{'policy_id': 'fees', 'quote': POLICIES[1]['facts'][1][1]}]}, {'provider': 'mock-live-provider', 'model': 'test-model'})
    monkeypatch.setattr(llm_gateway, 'LLMGateway', lambda: gateway)
    with TestClient(campus_app) as client:
        chat = conversation(client, engine='live')
        answer = chat('Can I pay fees in instalments?')
        assert answer['provider'] == 'mock-live-provider'
        assert '3 monthly instalments' in answer['response']
        gateway.generate_json.return_value = ({'excerpts': [{'policy_id': 'fees', 'quote': 'All tuition is free.'}]}, {})
        failed = client.post('/api/chat', json={'message': 'Can I pay fees in instalments?', 'engine': 'live'})
        assert failed.status_code == 503
        assert 'unverified' in failed.json()['detail']


def test_live_generator_batches_large_requests_and_restores_output_limit():
    target = demo_target()
    plan = objectives({'target': target})
    generated = cases({'target': target, 'plan': plan, 'test_count': 50, 'exploration': 50})['cases']
    gateway = Mock(max_output_tokens=1024)
    gateway.generate_json.side_effect = [({'cases': generated[i:i+5]}, {}) for i in range(0, 50, 5)]
    result, _ = TestGeneratorAgent(gateway).generate(target, plan, 50, 50)
    assert len(result) == 50 and gateway.generate_json.call_count == 10
    assert gateway.max_output_tokens == 1024


def test_live_generator_rejects_duplicate_inputs_with_different_titles():
    target = demo_target()
    plan = objectives({'target': target})
    generated = cases({'target': target, 'plan': plan, 'test_count': 5, 'exploration': 50})['cases']
    generated[1]['turns'] = generated[0]['turns']
    gateway = Mock(max_output_tokens=1024)
    gateway.generate_json.return_value = ({'cases': generated}, {})
    with pytest.raises(ValueError, match='repeated'):
        TestGeneratorAgent(gateway).generate(target, plan, 5, 50)
    assert gateway.max_output_tokens == 1024


def test_live_generation_repairs_duplicates_and_resumes_validated_batches():
    target = demo_target()
    plan = objectives({'target': target})
    generated = cases({'target': target, 'plan': plan, 'test_count': 10, 'exploration': 50})['cases']
    gateway = Mock(max_output_tokens=1024)
    gateway.generate_json.side_effect = [({'cases': generated[:5]}, {}), ({'cases': generated[5:]}, {})]
    agent = TestGeneratorAgent(gateway)
    agent.on_checkpoint = Mock()
    agent.on_repair = Mock()
    result, _ = agent.generate(target, plan, 10, 50, initial_cases=generated[:5])
    assert len(result) == 10 and gateway.generate_json.call_count == 2
    agent.on_repair.assert_called_once()
    assert agent.on_checkpoint.call_args.args[0] == result
    context = json.loads(gateway.generate_json.call_args.args[1])
    assert context['previous_cases'] and context['validation_feedback']


def test_live_generation_keeps_valid_cases_when_only_part_of_a_batch_repeats():
    target = demo_target()
    plan = objectives({'target': target})
    generated = cases({'target': target, 'plan': plan, 'test_count': 5, 'exploration': 50})['cases']
    gateway = Mock(max_output_tokens=1024)
    gateway.generate_json.side_effect = [({'cases': [generated[0], generated[0], *generated[1:4]]}, {}),
                                         ({'cases': generated[4:]}, {})]
    agent = TestGeneratorAgent(gateway)
    checkpoints = []
    agent.on_checkpoint = lambda saved: checkpoints.append(len(saved))
    result, _ = agent.generate(target, plan, 5, 50)
    assert len(result) == 5 and checkpoints == [4, 5]
    assert json.loads(gateway.generate_json.call_args.args[1])['test_count'] == 1


def test_one_click_run_without_env_or_endpoint_form(tmp_path, campus_url, monkeypatch):
    import app as lab_module
    original = demo_target
    monkeypatch.setattr(lab_module, 'demo_target', lambda mode='weak': original(campus_url, mode))
    monkeypatch.delenv('LAB_ALLOWED_ENDPOINTS', raising=False)
    with TestClient(lab_module.create_app(tmp_path)) as client:
        response = client.post('/api/demo-runs', json={'tests': 100, 'mode': 'hardened'})
        assert response.status_code == 201, response.text
        id = response.json()['id']
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            run = client.get('/api/runs/' + id).json()
            if run['report']:
                break
            time.sleep(.2)
        assert run['status'] == 'completed', run.get('error')
        assert len(run['evaluations']) == 100
        assert run['report']['counts']['PASS'] == 100
        assert run['usage']['target_requests'] > 100
        assert run['usage']['cost_reserved_usd'] == 0
        retest = client.post('/api/demo-runs', json={'tests': 100, 'mode': 'hardened', 'source_run_id': id})
        assert retest.status_code == 201
        assert retest.json()['cases'] == run['cases']
        client.post('/api/runs/' + retest.json()['id'] + '/cancel')
