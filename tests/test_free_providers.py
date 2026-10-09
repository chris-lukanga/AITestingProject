import json
from unittest.mock import Mock
import pytest
import llm_gateway as gateway_module
from services import free_providers as providers
from services.budget import BudgetExceeded


def model(identifier='vendor/free-chat', tier='free', input_price=0, output_price=0):
    return {'id': identifier, 'access_tier': tier, 'modality': 'chat', 'context_length': 100000,
            'pricing': {'input': input_price, 'output': output_price}}


@pytest.mark.parametrize('candidate', [model(tier='paid'), model(tier='premium'),
                                      model(input_price='.1'), model(output_price=None), model(input_price='NaN')])
def test_xkiro_excludes_paid_unknown_and_invalid_pricing(candidate):
    assert not providers.eligible_model('xkiro', candidate)


def test_free_catalog_accepts_explicit_zero_prices_and_groq_supported_free_plan_models():
    assert providers.eligible_model('xkiro', model(input_price='0.000000'))
    assert providers.eligible_model('groq', {'id': 'openai/gpt-oss-20b'})
    assert not providers.eligible_model('groq', {'id': 'paid-model'})


def test_legacy_grok_variable_only_routes_groq_key_to_groq(monkeypatch):
    monkeypatch.setenv('GROK_API_KEY', 'gsk_synthetic')
    assert providers.groq_key() == 'gsk_synthetic'
    monkeypatch.setenv('GROK_API_KEY', 'xai-synthetic')
    assert not providers.groq_key()


def test_fallback_preserves_context_and_metadata_and_stops_before_budget_dispatch(monkeypatch):
    fallback = providers.FreeChatFallback('xkiro', 'synthetic-key')
    fallback.models, fallback.discovered_at = [model()], providers.time.monotonic()
    gateway = gateway_module.LLMGateway()
    gateway.before_call = Mock()
    gateway.on_usage = Mock()
    response = Mock(status_code=200)
    response.json.return_value = {'model': 'vendor/free-chat', 'choices': [{'message': {'content': '{"ok":true}'}}], 'usage': {'total_tokens': 12}}
    post = Mock(return_value=response)
    monkeypatch.setattr(providers.requests, 'post', post)
    result, metadata = fallback.generate(gateway, 'complete system', 'complete user', .2, 'evaluation', 'fingerprint', json.loads)
    assert result == {'ok': True} and metadata['provider'] == 'xkiro' and metadata['free_model']
    assert post.call_args.kwargs['json']['messages'] == [{'role': 'system', 'content': 'complete system'}, {'role': 'user', 'content': 'complete user'}]
    gateway.on_usage.assert_called_once_with(12)
    gateway.before_call.side_effect = BudgetExceeded('Limit reached')
    with pytest.raises(BudgetExceeded):
        fallback.generate(gateway, 'system', 'user', .2, 'generation', 'next', json.loads)
    assert post.call_count == 1


def test_quota_rejection_stops_free_provider_without_paid_upgrade(monkeypatch):
    fallback = providers.FreeChatFallback('xkiro', 'synthetic-key')
    fallback.models, fallback.discovered_at = [model(), model('vendor/second')], providers.time.monotonic()
    post = Mock(return_value=Mock(status_code=429))
    monkeypatch.setattr(providers.requests, 'post', post)
    gateway = gateway_module.LLMGateway()
    for _ in range(2):
        assert fallback.generate(gateway, 'system', 'user', .2, 'generation', 'fp', json.loads) is None
    assert post.call_count == 1


def test_gateway_enforces_free_models_even_if_paid_preference_is_supplied(monkeypatch):
    gateway = gateway_module.LLMGateway(preferred_model='gemini-pro-paid', only_free=False)
    gateway._gemini_models = ['gemini-pro-paid', 'gemini-3.1-flash-lite']
    assert gateway.only_free and gateway._get_gemini_models() == ['gemini-3.1-flash-lite']


def test_openrouter_rejects_extra_charges_even_for_models_named_free(monkeypatch):
    monkeypatch.setattr(gateway_module, 'OPENROUTER_API_KEY', 'synthetic-key')
    def entry(identifier, **extra):
        return {'id': identifier, 'context_length': 100000,
                'architecture': {'input_modalities': ['text'], 'output_modalities': ['text']},
                'pricing': dict(prompt='0', completion='0', **extra)}
    response = Mock()
    response.json.return_value = {'data': [entry('request:free', request='.1'),
                                         entry('reasoning:free', internal_reasoning='.1'), entry('safe:free')]}
    monkeypatch.setattr(gateway_module.requests, 'get', Mock(return_value=response))
    assert [m['id'] for m in gateway_module.discover_openrouter_free_models(only_free=True)] == ['safe:free']
