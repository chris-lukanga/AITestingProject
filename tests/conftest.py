import sys
import socket
import threading
import time
from pathlib import Path
import pytest
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolate_extra_provider_credentials(monkeypatch):
    for variable in ('GROQ_API_KEY', 'GROK_API_KEY', 'XKIRO_API_KEY', 'XAI_API_KEY'):
        monkeypatch.delenv(variable, raising=False)


@pytest.fixture(scope='session')
def general_url():
    from fastapi import FastAPI
    service = FastAPI()
    @service.post('/api/chat')
    def answer(payload: dict):
        assert isinstance(payload['message'], str)
        return {'response': 'The workspace retention period is 30 days. Source: Workspace policy.',
                'tool_calls': [], 'provider': 'local', 'model': 'contract-fixture'}
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    server = uvicorn.Server(uvicorn.Config(service, log_level='error'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(.05)
    assert server.started
    yield f'http://127.0.0.1:{sock.getsockname()[1]}/api/chat'
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()


@pytest.fixture(scope='session')
def campus_url():
    from examples.campushelp.app import app
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level='error'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started, 'Demo failed to start.'
    yield f'http://127.0.0.1:{port}/api/chat'
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()
