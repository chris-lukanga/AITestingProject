import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
load_dotenv(ROOT / 'backend' / '.env')
from schemas.contracts import Target, RunRequest, Limits
from database.store import Store
from services.workflow import Workflow
from services.scenarios import demo_target
from services.budget import estimate
from agents.clarification_agent import ClarificationAgent
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent
from services.history import same_target, compare_evaluations
from services.agent_manifest import AGENTS
from services.security import enforce_scope
from services.free_providers import groq_key


class EstimateRequest(BaseModel):
    target_id: str
    exploration: int = Field(default=50, ge=0, le=100)
    limits: Limits = Field(default_factory=Limits)
    mode: Literal['offline', 'live'] = 'offline'


class Settings(BaseModel):
    mode: Literal['offline', 'live'] = os.getenv('LAB_MODE', 'offline')
    default_limits: Limits = Field(default_factory=Limits)
    retention_days: int = Field(default=90, ge=1, le=3650)
    preferred_model: str = os.getenv('GEMINI_MODEL', '')
    only_free: Literal[True] = True


class DemoRunRequest(BaseModel):
    mode: Literal['weak', 'hardened'] = 'weak'
    tests: Literal[50, 100, 200] = 100
    source_run_id: str = ''


def create_app(data_dir=None):
    data_dir = Path(data_dir or os.getenv('LAB_DATA_DIR', ROOT / 'outputs' / 'lab'))
    store = Store(data_dir / 'lab.sqlite3')
    workflow = Workflow(store, data_dir / 'reports')
    @asynccontextmanager
    async def lifespan(app):
        store.recover()
        yield
        await workflow.shutdown()
    app = FastAPI(title=os.getenv('PRODUCT_NAME', 'LLM Integrity Lab'), version='1.0.0', lifespan=lifespan)
    app.state.store, app.state.workflow = store, workflow

    @app.middleware('http')
    async def local_browser_boundary(request: Request, call_next):
        # Reject cross-origin browser mutations, including DNS rebinding Host values.
        host = request.url.hostname
        if host not in ('127.0.0.1', 'localhost', '::1', 'testserver'):
            return HTMLResponse('This local platform accepts loopback hostnames only.', status_code=403)
        origin = request.headers.get('origin')
        if request.method not in ('GET', 'HEAD', 'OPTIONS') and origin and origin != str(request.base_url).rstrip('/'):
            return HTMLResponse('Cross-origin writes are not allowed.', status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        if request.url.path in ('/docs', '/redoc'):
            # FastAPI's documentation pages load their official documentation UI.
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https://fastapi.tiangolo.com data:; frame-ancestors 'none'"
        return response

    def get(kind, id):
        value = store.get(kind, id)
        if value is None:
            raise HTTPException(404, f'{kind.title()} not found.')
        return value

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'service': 'llm-integrity-lab', 'product': app.title}

    @app.get('/api/demo-target')
    def demo(mode: str = 'weak'):
        if mode not in ('weak', 'hardened'):
            raise HTTPException(422, 'Invalid demo mode.')
        return demo_target(mode=mode)

    @app.get('/api/example')
    def example():
        return json.loads((ROOT / 'backend' / 'example.json').read_text(encoding='utf-8'))

    @app.post('/api/demo-runs', status_code=201)
    async def demo_run(config: DemoRunRequest):
        # The bundled local application is already in scope. No endpoint, JSON,
        # provider settings or separate authorization form is needed for this path.
        import httpx
        target = Target.model_validate(demo_target(mode=config.mode))
        source = get('run', config.source_run_id) if config.source_run_id else None
        if source and (source['status'] != 'completed' or source['target']['adapter']['kind'] != 'campushelp'
                       or source['target']['adapter']['endpoint'] != target.adapter.endpoint
                       or source['target']['adapter'].get('engine', 'local') != 'local'
                       or len(source['cases']) != config.tests):
            raise HTTPException(422, 'Retest requires a completed local demo run with the same suite size and endpoint.')
        try:
            async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
                response = await client.get(target.adapter.endpoint.removesuffix('/api/chat') + '/api/health')
                if response.status_code != 200 or response.json().get('service') != 'campushelp-ai':
                    raise ValueError('Wrong service')
        except (httpx.HTTPError, ValueError):
            raise HTTPException(503, 'CampusHelp is not running. Start both websites with Start-Lab.cmd or python run_lab.py.')
        target.id = uuid.uuid4().hex
        store.put('target', target.id, target.model_dump())
        request = RunRequest(target_id=target.id, limits=Limits(max_tests=config.tests, requests_per_second=15, concurrency=4))
        run = workflow.create(request)
        if source:
            # Freeze the original inputs/assertions for a controlled comparison.
            run.update(cases=source['cases'], plan=source['plan'], research=source['research'], source_run_id=source['id'])
            store.put('run', run['id'], run)
        return workflow.action(run['id'], 'start')

    @app.get('/api/targets')
    def targets():
        return store.list('target')

    @app.get('/api/agents')
    def agents():
        return {'agents': AGENTS}

    @app.post('/api/targets/{id}/probe')
    async def probe(id: str):
        from agents.execution_agent import ExecutionAgent
        from services.budget import Budget
        target = Target.model_validate(get('target', id))
        try:
            enforce_scope(target)
            limits = Limits(max_tests=1, max_requests=1, max_tokens=100000, max_seconds=20,
                            timeout_seconds=15, max_output_tokens=64)
            case = {'id': 'connection-check', 'turns': [{'input': 'Hello. Briefly describe what you can help with.', 'user': 'test-user' if target.adapter.kind == 'http' else 'student-a'}],
                    'repetitions': 1, 'assertions': []}
            result = await ExecutionAgent(target, limits, Budget(limits), asyncio.Event(), asyncio.Event()).execute(case)
            observation = result['turns'][0]
            return {'connected': observation['outcome'] == 'OK', 'status': observation['status'],
                    'latency_ms': observation['latency_ms'], 'provider': observation.get('provider'), 'model': observation.get('model'),
                    'response_preview': observation['response'][:1200], 'error': observation.get('error'),
                    'response_fields': list(observation.get('body', {}))}
        except ValueError as error:
            raise HTTPException(422, str(error))

    @app.post('/api/targets', status_code=201)
    @app.post('/api/targets/import', status_code=201)
    def target_create(target: Target):
        target.id = target.id or uuid.uuid4().hex
        store.put('target', target.id, target.model_dump())
        return get('target', target.id)

    @app.get('/api/targets/{id}')
    def target_get(id: str):
        return get('target', id)

    @app.get('/api/targets/{id}/clarifications')
    def questions(id: str):
        return {'questions': ClarificationAgent().questions(Target.model_validate(get('target', id)))}

    @app.post('/api/targets/{id}/clarifications')
    def answers(id: str, answers: dict):
        try:
            target = ClarificationAgent().apply(Target.model_validate(get('target', id)), answers)
            store.put('target', id, target.model_dump())
            return {'target': get('target', id), 'questions': ClarificationAgent().questions(target)}
        except ValueError as error:
            raise HTTPException(422, str(error))

    @app.get('/api/targets/{id}/recommendation')
    def recommendation(id: str):
        target = Target.model_validate(get('target', id))
        settings = store.get('settings', 'default') or Settings().model_dump()
        return RecommendationAgent().recommend(target, workflow.history(target.model_dump()), Limits.model_validate(settings['default_limits']))

    @app.post('/api/estimate')
    def estimated(config: EstimateRequest):
        if config.mode not in ('offline', 'live'):
            raise HTTPException(422, 'Mode must be offline or live.')
        return estimate(Target.model_validate(get('target', config.target_id)), config.exploration, config.limits, config.mode)

    @app.post('/api/runs', status_code=201)
    def run_create(config: RunRequest):
        try:
            return workflow.create(config)
        except KeyError as error:
            raise HTTPException(404, str(error))
        except ValueError as error:
            raise HTTPException(422, str(error))

    @app.get('/api/runs')
    def runs():
        return [{k: r[k] for k in ['id', 'status', 'stage', 'created_at', 'updated_at', 'config', 'usage', 'estimate']} |
                {'target_name': r['target']['application'].get('name'), 'report': {'counts': r['report']['counts'], 'assessment': r['report']['assessment']} if r['report'] else None,
                 'completed': len(r['evaluations']), 'planned': len(r['cases']), 'providers': sorted({e.get('provider', '') for e in r['provider_history']})} for r in store.list('run')]

    @app.get('/api/runs/{id}')
    def run_get(id: str):
        return get('run', id)

    @app.patch('/api/runs/{id}/limits')
    def run_limits(id: str, limits: Limits):
        run = get('run', id)
        if run['status'] not in ('created', 'interrupted', 'failed', 'limited'):
            raise HTTPException(409, 'Change limits only while the run is stopped.')
        run['config']['limits'] = limits.model_dump()
        run['estimate'] = estimate(Target.model_validate(run['target']), run['config']['exploration'], limits, run['config']['mode'])
        if not run['estimate']['can_start']:
            raise HTTPException(422, run['estimate']['violations'])
        store.put('run', id, run)
        return run

    @app.get('/api/activity')
    def activity():
        events = [dict(event, run_id=run['id']) for run in store.list('run')[:5] for event in store.events(run['id'])]
        return {'events': sorted(events, key=lambda e: e['timestamp'], reverse=True)[:12]}

    @app.post('/api/runs/{id}/retest', status_code=201)
    def retest(id: str):
        source = get('run', id)
        if source['status'] in ('running', 'paused', 'created') or not source['cases']:
            raise HTTPException(409, 'Retest requires a stopped run with saved test cases.')
        config = dict(source['config'])
        config['limits'] = dict(config['limits'], max_tests=len(source['cases']))
        try:
            run = workflow.create(RunRequest.model_validate(config))
        except ValueError as error:
            raise HTTPException(422, str(error))
        run.update(plan=source['plan'], research=source['research'],
                   cases=json.loads(json.dumps(source['cases'])), generation_complete=True,
                   source_run_id=id)
        store.put('run', run['id'], run)
        workflow.emit(run, 'Orchestrator', 'Saved suite selected for retest',
                      'Use the saved inputs, assertions and plan with a fresh execution budget.',
                      {'source_run_id': id, 'cases': len(run['cases'])})
        return run

    @app.post('/api/runs/{id}/{action}')
    async def run_action(id: str, action: str):
        try:
            return workflow.action(id, action)
        except KeyError as error:
            raise HTTPException(404, str(error))
        except ValueError as error:
            raise HTTPException(409, str(error))

    @app.get('/api/runs/{id}/cases')
    def cases(id: str):
        return {'cases': get('run', id)['cases']}

    @app.get('/api/runs/{id}/findings')
    def findings(id: str):
        return {'findings': [e for e in get('run', id)['evaluations'] if e['classification'] == 'FAIL']}

    @app.get('/api/runs/{id}/research')
    def research(id: str):
        run = get('run', id)
        return {'research': run['research'], 'plan': run['plan']}

    @app.get('/api/runs/{id}/events')
    async def events(id: str, request: Request, after: int = 0, agent: str = '', severity: str = '', stage: str = ''):
        get('run', id)
        try:
            after = max(after, int(request.headers.get('last-event-id', 0)))
        except ValueError:
            raise HTTPException(422, 'Invalid event cursor.')
        async def stream():
            cursor = after
            while not await request.is_disconnected():
                for event in store.events(id, cursor):
                    cursor = event['seq']
                    if (not agent or agent == event['agent']) and (not severity or severity == event['severity']) and (not stage or stage == event['stage']):
                        yield f"id: {cursor}\ndata: {json.dumps(event)}\n\n"
                run = get('run', id)
                if run['report'] and run['status'] in ('completed', 'failed', 'cancelled', 'limited', 'interrupted'):
                    yield 'event: done\ndata: {}\n\n'
                    break
                yield ': heartbeat\n\n'
                await asyncio.sleep(0.5)
        return StreamingResponse(stream(), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    @app.get('/api/runs/{id}/trace')
    def trace(id: str):
        get('run', id)
        return {'events': store.events(id)}

    @app.get('/api/runs/{id}/report')
    def report(id: str, format: str = 'json', download: bool = False):
        run = get('run', id)
        if not run['report']:
            raise HTTPException(409, 'Report is not available yet.')
        if format not in ('json', 'html'):
            raise HTTPException(422, 'Report format must be json or html.')
        if download:
            path = workflow.output_dir / id / f'report.{format}'
            if not path.exists():
                # SQLite is authoritative; downloads can be rebuilt after report-file loss.
                path.parent.mkdir(parents=True, exist_ok=True)
                content = ReportAgent().html(run['report'], app.title) if format == 'html' else json.dumps(run['report'], indent=2)
                path.write_text(content, encoding='utf-8')
            return FileResponse(path, filename=f'{id}.{format}')
        return HTMLResponse(ReportAgent().html(run['report'], app.title)) if format == 'html' else run['report']

    @app.get('/api/compare')
    def compare(first: str, second: str):
        a, b = get('run', first), get('run', second)
        if not same_target(a['target'], b['target']):
            raise HTTPException(422, 'Compare runs of the same target.')
        if not a['report'] or not b['report']:
            raise HTTPException(409, 'Both reports must be available.')
        return {'first': first, 'second': second, **compare_evaluations(a['evaluations'], b['evaluations']),
                'counts': [a['report']['counts'], b['report']['counts']]}

    @app.get('/api/providers')
    def providers():
        return {'offline': {'available': True, 'model': 'deterministic-rules-v1'},
                'gemini': {'configured': bool(os.getenv('GEMINI_API_KEY')), 'availability': 'Not verified; discovered models can still have no quota'},
                'openrouter': {'configured': bool(os.getenv('OPENROUTER_API_KEY')), 'availability': 'Not verified; free models have quotas'},
                'groq': {'configured': bool(groq_key()), 'availability': 'Free-plan models only; your Groq account must remain on its Free plan'},
                'xkiro': {'configured': bool(os.getenv('XKIRO_API_KEY')), 'availability': 'Verified free catalog models only; paid and premium tiers are excluded'},
                'grok': {'configured': bool(os.getenv('GROK_API_KEY', '').startswith('xai-') or os.getenv('XAI_API_KEY')), 'availability': 'Disabled: direct xAI models are paid'},
                'tavily': {'configured': bool(os.getenv('TAVILY_API_KEY'))}}

    @app.get('/api/settings')
    def settings_get():
        return dict(store.get('settings', 'default') or Settings().model_dump(), product=app.title,
                    only_free=True,
                    allowed_endpoints=[x for x in os.getenv('LAB_ALLOWED_ENDPOINTS', '').split(',') if x])

    @app.put('/api/settings')
    def settings_put(settings: Settings):
        store.put('settings', 'default', settings.model_dump())
        return settings_get()

    @app.post('/api/maintenance/prune')
    def prune():
        settings = store.get('settings', 'default') or Settings().model_dump()
        count = store.prune(settings['retention_days'])
        return {'deleted_runs': count, 'note': 'Downloaded report files are retained on disk; remove them separately when no longer needed.'}

    app.mount('/assets', StaticFiles(directory=ROOT / 'frontend'), name='assets')
    @app.get('/', response_class=FileResponse)
    def index():
        return FileResponse(ROOT / 'frontend' / 'index.html')
    return app


app = create_app()
