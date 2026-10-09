"""Free chat fallbacks with catalog checks and bounded provider attempts."""
import os
import time
from decimal import Decimal, InvalidOperation
import requests


GEMINI_FREE_MODELS = frozenset({
    # Google standard text pricing, verified 2026-10-09.
    'gemini-3.8-flash', 'gemini-3.6-flash', 'gemini-3.5-flash',
    'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-3-flash-preview',
    'gemini-2.5-flash', 'gemini-2.5-flash-lite',
})
GROQ_FREE_MODELS = frozenset({'openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'qwen/qwen3.8-27b'})
BASE_URLS = {'groq': 'https://api.groq.com/openai/v1', 'xkiro': 'https://api.xkiro.com/v1'}


def groq_key():
    key = os.getenv('GROQ_API_KEY', '').strip()
    legacy = os.getenv('GROK_API_KEY', '').strip()
    return key or (legacy if legacy.startswith('gsk_') else '')


def live_keys_available():
    return bool(os.getenv('GEMINI_API_KEY') or os.getenv('OPENROUTER_API_KEY') or groq_key() or os.getenv('XKIRO_API_KEY'))


def zero_price(value):
    if value is None or isinstance(value, bool):
        return False
    try:
        amount = Decimal(str(value))
        return amount.is_finite() and amount == 0
    except (InvalidOperation, ValueError):
        return False


def eligible_model(provider, model):
    identifier = model.get('id', '')
    if provider == 'groq':
        return identifier in GROQ_FREE_MODELS and model.get('active', True) is True
    if provider == 'xkiro':
        price = model.get('pricing', {}) or {}
        return (model.get('access_tier') == 'free' and model.get('modality', 'chat') == 'chat'
                and zero_price(price.get('input')) and zero_price(price.get('output')))
    return False


class FreeChatFallback:
    def __init__(self, provider, key):
        self.provider, self.key = provider, key
        self.models, self.discovered_at, self.cooldowns = None, 0, {}
        self.provider_until = 0

    def discover(self, timeout=10):
        if self.models is not None and time.monotonic() - self.discovered_at < 300:
            return self.models
        response = requests.get(BASE_URLS[self.provider] + '/models',
                                headers={'Authorization': 'Bearer ' + self.key}, timeout=timeout)
        response.raise_for_status()
        self.models = [m for m in response.json().get('data', []) if eligible_model(self.provider, m)]
        self.discovered_at = time.monotonic()
        return self.models

    def generate(self, gateway, system, user, temperature, purpose, fingerprint, parse):
        if self.provider_until > time.monotonic():
            gateway._record(self.provider, 'free-catalog', 'skipped', purpose, fingerprint, 0,
                            error='Provider cooldown is active; no paid fallback is allowed.')
            return None
        try:
            models = self.discover(timeout=min(10, gateway.timeout_seconds))
        except (requests.RequestException, ValueError, TypeError):
            gateway._record(self.provider, 'free-catalog', 'failed', purpose, fingerprint, 0,
                            error='Free-model catalog could not be verified; no model was dispatched.')
            return None
        for model in models:
            identifier = model['id']
            if self.cooldowns.get(identifier, 0) > time.monotonic():
                continue
            capacity = model.get('context_length') or model.get('context_window') or 0
            required = len((system + user).encode()) + gateway.max_output_tokens
            if capacity and required > capacity:
                gateway._record(self.provider, identifier, 'skipped', purpose, fingerprint, 0,
                                error='Insufficient context capacity; input was not truncated.')
                continue
            if gateway.before_call:
                gateway.before_call(system, user)
            payload = {'model': identifier,
                       'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                       'temperature': temperature, 'stream': False, 'response_format': {'type': 'json_object'}}
            payload['max_completion_tokens' if self.provider == 'groq' else 'max_tokens'] = gateway.max_output_tokens
            try:
                response = requests.post(BASE_URLS[self.provider] + '/chat/completions',
                                         headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'},
                                         json=payload, timeout=gateway.timeout_seconds)
                if response.status_code >= 400:
                    gateway._record(self.provider, identifier, 'failed', purpose, fingerprint, 1,
                                    error=f'HTTP {response.status_code}; free-model request was rejected.')
                    self.cooldowns[identifier] = time.monotonic() + 60
                    if response.status_code in (401, 402, 429):
                        self.provider_until = time.monotonic() + 60
                        break
                    continue
                envelope = response.json()
                usage = envelope.get('usage', {})
                if gateway.on_usage and isinstance(usage, dict):
                    gateway.on_usage(int(usage.get('total_tokens', 0) or 0))
                result = parse(envelope['choices'][0]['message']['content'])
                actual = envelope.get('model', identifier)
                if self.provider == 'xkiro' and actual != identifier:
                    raise ValueError('Response model does not match the verified free model.')
                gateway._record(self.provider, identifier, 'success', purpose, fingerprint, 1, actual_model=actual)
                return result, {'provider': self.provider, 'model': actual, 'purpose': purpose,
                                'attempt': 1, 'context_fingerprint': fingerprint,
                                'fallback': gateway.history[-1]['fallback'], 'free_model': True}
            except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
                gateway._record(self.provider, identifier, 'failed', purpose, fingerprint, 1,
                                error='Free provider returned an invalid or unavailable JSON response.')
        return None
