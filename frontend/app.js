const state = {runs:[], activity:[], run:null, target:null, recommendation:null, estimate:null, events:[], stream:null, step:1, exploration:50, limits:null, mode:'offline', targets:[], agents:[], providers:{}, expandedEvents:new Set(), caseFilter:'', filters:{agent:'',severity:'',stage:''}};
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const json = value => esc(JSON.stringify(value, null, 2));
const tag = value => `<span class="tag ${esc(value)}">${esc(value)}</span>`;
const date = value => new Date(value).toLocaleString();
const button = (action, label, cls='', data='') => `<button type="button" class="${cls}" data-action="${action}" ${data}>${label}</button>`;
const stat = (label, value, hint='') => `<div class="stat"><label>${label}</label><strong>${esc(value)}</strong><small>${esc(hint)}</small></div>`;
const empty = (title, text) => `<div class="empty"><strong>${title}</strong>${text}</div>`;
const heading = (title, text, actions='') => `<div class="page-heading"><div><div class="eyebrow">INTEGRATION ASSURANCE</div><h1>${title}</h1><p class="muted">${text}</p></div><div class="actions">${actions}</div></div>`;

async function api(path, method='GET', body) {
  const response = await fetch('/api'+path, {method, headers:{'Content-Type':'application/json'}, ...(body !== undefined ? {body:JSON.stringify(body)} : {})});
  const data = await response.json();
  if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
  return data;
}
function notice(error) {const el = $('#notice'); el.textContent = error.message || error; el.hidden = false;}
function clearNotice() {$('#notice').hidden = true;}
async function refreshRuns() {const [runs,activity,targets]=await Promise.all([api('/runs'),api('/activity'),api('/targets')]);state.runs=runs;state.activity=activity.events;state.targets=targets;}
function routeName() {return location.hash.slice(1) || 'dashboard';}
async function navigate(route) {if(routeName()!==route) window.history.pushState(null,'','#'+route);await render();}
function tableRows(runs) {
  return runs.length ? `<div class="table-scroll"><table><thead><tr><th>Target / run</th><th>Started</th><th>Strategy</th><th>Tests</th><th>Assessment</th><th>Status</th><th></th></tr></thead><tbody>${runs.map(r=>`<tr><td><strong>${esc(r.target_name)}</strong><br><span class="run-id muted">${r.id.slice(0,8)}</span></td><td>${esc(date(r.created_at))}</td><td>${r.config.exploration}% explore</td><td>${r.completed}/${r.planned || '—'}</td><td>${esc(r.report?.assessment || 'Pending')}</td><td>${tag(r.status)}</td><td>${button('open-run','Open','',`data-id="${r.id}"`)}</td></tr>`).join('')}</tbody></table></div>` : empty('No runs yet','Configure a target or try the local demonstration.');
}
function dashboard() {
  const completed=state.runs.filter(r=>r.status==='completed');
  const failures=completed.reduce((n,r)=>n+(r.report?.counts.FAIL||0),0);
  const latest=state.runs[0];
  return heading('Integration overview','Plan, test and evaluate the behaviour of any AI application.',button('new-test','New test run','primary'))+
    `<section class="hero panel"><div><span class="eyebrow">AI QUALITY / ONE WORKSPACE</span><h2>Know what your integration actually does.</h2><p>Connect a chatbot, retrieval service or agent API. Let the researcher and planner design the run, then inspect every request, evaluation and quality check.</p><div class="actions">${button('new-test','Connect an application','primary')}${latest?button('open-run','Open latest run','',`data-id="${latest.id}"`):''}</div></div><div class="hero-flow"><span>01 <strong>Research & plan</strong></span><span>02 <strong>Generate & execute</strong></span><span>03 <strong>Evaluate & review</strong></span><small>Live decisions. Captured evidence. Repeatable testing.</small></div></section>
    <div class="stats">${stat('Applications',state.targets.length,'Configured in this workspace')}${stat('Completed runs',completed.length,'Retained test evidence')}${stat('Failed checks',failures,'Inspect the underlying response')}${stat('Active runs',state.runs.filter(r=>['running','paused'].includes(r.status)).length,'Tracked through the agent console')}</div>
    <section class="panel"><div class="panel-heading inline"><div><h2>Connected applications</h2><p class="hint">Your application contract defines what the agents test.</p></div>${button('new-test','Add application')}</div>${state.targets.length?`<div class="target-grid">${state.targets.slice(0,6).map(t=>`<article class="target-card"><div class="target-monogram">${esc((t.application.name||'A').slice(0,1))}</div><h3>${esc(t.application.name||'Untitled application')}</h3><p>${esc(t.application.purpose||'AI integration')}</p><code>${esc(t.adapter.endpoint)}</code><div class="actions">${button('configure-target','Configure run','',`data-id="${t.id}"`)}</div></article>`).join('')}</div>`:empty('Connect your first application','Add its chat URL and expected behaviour. Common JSON and chat-completion formats are supported.')}</section>
    <section class="panel flush"><div class="panel-heading"><h2>Recent test runs</h2><a href="#history">All history →</a></div>${tableRows(state.runs.slice(0,6))}</section>
    <div class="grid two"><section class="panel"><h2>Agent activity</h2>${state.activity.slice(0,4).map(e=>`<div class="activity-row"><span class="activity-dot"></span><div><strong>${esc(e.agent)}</strong><p>${esc(e.decision)}</p><small>${esc(date(e.timestamp))}</small></div></div>`).join('')||empty('Ready for your first run','Agent actions will appear here when work starts.')}</section><section class="panel"><h2>Testing capabilities</h2><div class="capabilities"><span>Prompt boundaries</span><span>Grounded answers</span><span>Data isolation</span><span>Tool permissions</span><span>Conversation memory</span><span>Response contracts</span></div><p class="hint">Checks come from your declared behaviour and evidence. Errors and inconclusive judgments are reported separately.</p>${quickStart()}</section></div>`;
}

function quickStart() {
  return `<details class="example-target"><summary>Example target: CampusHelp</summary><p class="hint">A bundled student assistant for practising the workflow. The lab also accepts your own application endpoint.</p><div class="form-grid"><label class="field">Sample suite<select id="demo-count"><option value="50">50 cases</option><option value="100" selected>100 cases</option><option value="200">200 cases</option></select></label><label class="field">Sample version<select id="demo-protection"><option value="weak">Vulnerable</option><option value="hardened">Protected</option></select></label></div><p class="hint">The sample button executes the local handbook engine. Configure a run to use live agents or a live target model.</p><div class="actions">${button('run-demo','Run tests')}${button('try-demo','Advanced demo setup')}</div><a href="http://127.0.0.1:8001" target="_blank" rel="noopener">Open example app ↗</a></details>`;
}

function targetForm() {
  const t=state.target;
  const preset=t?.adapter?.kind==='campushelp'?'campushelp':t?.adapter?.response_path==='choices.0.message.content'?'openai':'json';
  return heading('Connect an application','Define the API and expected behaviour. The agents use this contract to design meaningful tests.',button('try-demo','Use example target')+button('import-example','Import example.json'))+
    `<div class="wizard-step"><span class="step">01 Application</span><span class="muted">02 Context</span><span class="muted">03 Run settings</span></div>
    <section class="panel"><h2>Application details</h2><div class="form-grid">
    <label class="field">Application name<input id="target-name" value="${esc(t?.application?.name||'')}" placeholder="Support assistant, internal copilot, retrieval API…" required></label>
    <label class="field">Chat API URL<input id="target-url" type="url" value="${esc(t?.adapter?.endpoint||'')}" placeholder="https://your-app.example/api/chat"><span class="hint">The POST URL that receives messages in your application.</span></label>
    <label class="field full">What does the application do?<input id="target-purpose" value="${esc(t?.application?.purpose||'')}" placeholder="Helps customers answer questions from an approved knowledge base"></label>
    <label class="field full">Expected behaviour and policy facts<textarea class="prose" id="target-requirements" rows="4" placeholder="Describe what a correct answer must do, which actions need permission, and any known facts or response rules.">${esc(t?.application?.requirements||'')}</textarea><span class="hint">These requirements become the basis for test cases and evaluation. Include synthetic reference facts when possible.</span></label>
    <label class="field">API format<select id="api-preset"><option value="json" ${preset==='json'?'selected':''}>Simple JSON · message → response</option><option value="openai" ${preset==='openai'?'selected':''}>Chat completions · messages → choices</option><option value="custom">Custom JSON mapping</option><option value="campushelp" ${preset==='campushelp'?'selected':''}>CampusHelp example adapter</option></select></label>
    <label class="field">Testing environment<select id="target-environment"><option>Local development</option><option ${t?.testing_scope?.environment==='Authorized staging'?'selected':''}>Authorized staging</option><option>Production</option><option>Unknown</option></select></label>
    </div><div class="form-grid three capabilities-form">
    ${[['rag','Retrieval / knowledge base','rag_enabled'],['tools','External tools / actions','tools_enabled'],['memory','Conversation memory','conversation_memory']].map(([id,label,key])=>`<label class="field">${label}<select id="target-${id}"><option value="unknown" ${t?.integration?.[key]==null?'selected':''}>Unknown</option><option value="yes" ${t?.integration?.[key]===true?'selected':''}>Enabled</option><option value="no" ${t?.integration?.[key]===false?'selected':''}>Disabled</option></select></label>`).join('')}</div>
    <details><summary>Advanced connection settings</summary><div class="form-grid">
    <label class="field">Execution adapter<select id="target-kind"><option value="http" ${t?.adapter?.kind!=='campushelp'?'selected':''}>General HTTP integration</option><option value="campushelp" ${t?.adapter?.kind==='campushelp'?'selected':''}>CampusHelp example</option></select></label>
    <label class="field">Authentication variable<input id="target-auth-env" value="${esc(t?.adapter?.auth_env||'')}" placeholder="MY_APP_API_KEY"><span class="hint">Environment variable name. Credentials stay on the server.</span></label>
    <label class="field">Model provider<input id="target-provider" value="${esc(t?.llm?.provider||'Unknown')}"></label><label class="field">Target model<input id="target-model" value="${esc(t?.llm?.model_version||t?.llm?.model||'Unknown')}"></label>
    ${preset==='campushelp'?`<label class="field">Example protection mode<select id="target-mode"><option value="weak" ${t?.adapter?.mode==='weak'?'selected':''}>Vulnerable</option><option value="hardened" ${t?.adapter?.mode==='hardened'?'selected':''}>Protected</option></select></label><label class="field">Example answer engine<select id="target-engine"><option value="local">Local handbook</option><option value="live" ${t?.adapter?.engine==='live'?'selected':''}>Live AI</option></select></label>`:'<input type="hidden" id="target-mode" value="hardened"><input type="hidden" id="target-engine" value="local">'}
    <label class="field full">Full contract (JSON)<textarea id="target-json" rows="12" spellcheck="false">${json(t||{application:{},llm:{},integration:{},data_access:{declared:['Unknown']},testing_scope:{},adapter:{kind:'http',request_template:{message:'{input}',session_id:'{session}',max_tokens:'{max_tokens}'},response_path:'response'}})}</textarea></label>
    <label class="field full">Import an application contract<input id="import-file" type="file" accept=".json,application/json"></label>
    </div></details><label class="check authorization"><input id="authorized" type="checkbox" ${t?.testing_scope?.authorized?'checked':''}> I have permission to test this endpoint with synthetic inputs.</label>
    <div class="actions">${button('save-target','Continue to clarification','primary')}${button('probe-target','Test connection')}</div><div id="probe-result" role="status"></div></section>`;
}

function clarificationForm(questions) {
  return heading('Clarify the testing context','Only authorization and exact target scope block execution.')+
    `<div class="wizard-step"><span class="step">02 / CLARIFICATION</span></div><section class="panel">${questions.length ? questions.map(q=>`<fieldset data-question="${q.id}" data-type="${q.type}"><legend>${esc(q.label)} ${q.essential?'· required':''}</legend>${q.type==='single' || q.type==='multiple' ? `<div class="choices">${q.options.map(o=>`<label class="check"><input type="${q.type==='single'?'radio':'checkbox'}" name="q-${q.id}" value="${esc(o)}">${esc(o)}</label>`).join('')}</div>` : q.type==='long'?`<textarea aria-label="${esc(q.label)}" rows="3"></textarea>`:`<input aria-label="${esc(q.label)}">`}</fieldset>`).join('') : `<div class="info-box">The supplied configuration already contains the essential context.</div>`}<div class="actions">${button('save-answers','Continue to strategy','primary')}${button('back-target','Edit target')}</div></section>`;
}
function strategyForm() {
  const rec = state.recommendation;
  return heading('Testing strategy & budget','Review the allocation and limits before any target requests are sent.')+
    `<div class="wizard-step"><span class="step">03 / REVIEW</span></div><div class="grid two"><section class="panel"><h2>Exploration / focused validation</h2>
    <div class="slider-labels"><div><strong id="explore-label">${state.exploration}%</strong><span>Exploration</span></div><div><strong id="exploit-label">${100-state.exploration}%</strong><span>Exploitation / retesting</span></div></div>
    <label for="exploration" class="hint">Proportion of testing scope allocated to unfamiliar risk areas</label><input id="exploration" type="range" min="0" max="100" value="${state.exploration}">
    <div id="exploration-warning" class="warning-box" ${state.exploration>65?'':'hidden'}>High exploration can substantially increase unique scenarios, prompts, tokens, model calls and execution time. Consider a lower level for your first run.</div>
    <div class="info-box"><strong>Recommended: ${rec.exploration}% Exploration / ${rec.exploitation}% Exploitation</strong><p>${esc(rec.explanation)}</p>${button('apply-recommendation','Apply recommendation')}</div>
    <table><thead><tr><th>Observable heuristic</th><th>Contribution</th></tr></thead><tbody>${rec.contributions.map(c=>`<tr><td>${esc(c.reason)}</td><td>${c.points>0?'+':''}${c.points}</td></tr>`).join('')}</tbody></table></section>
    <section class="panel"><h2>Execution limits</h2><label class="field">Agent mode<select id="agent-mode"><option value="offline" ${state.mode==='offline'?'selected':''}>Local catalog + bundled references</option><option value="live" ${state.mode==='live'?'selected':''}>Live AI planning + optional web research</option></select></label>
    <p class="hint">Live agents use your configured model provider. Research uses Tavily when available. Local catalog runs are labelled separately.</p><label class="field">Number of test cases<select id="test-count">${[20,50,100,200].map(n=>`<option value="${n}" ${state.limits.max_tests===n?'selected':''}>${n} cases</option>`).join('')}</select></label><div class="form-grid budget-fields"><label class="field">Reservation budget (USD)<input id="run-budget" type="number" min="0" step="0.25" value="${state.limits.budget_usd}"></label><label class="field">Maximum runtime (seconds)<input id="run-seconds" type="number" min="1" max="3600" value="${state.limits.max_seconds}"></label><label class="field full">Reservation rate (USD per million tokens)<input id="run-price" type="number" min="0" step="0.25" value="${state.limits.price_per_million??''}"><span class="hint">Your pricing ceiling for dispatch estimates. Actual invoices can differ; local sample execution is free.</span></label></div><details><summary>Advanced budgets and rate limits</summary><label class="field">Limits (JSON)<textarea id="limits" rows="12">${json(state.limits)}</textarea></label></details>
    <div class="actions">${button('estimate','Recalculate estimate')}</div><div id="estimate-output">${estimateView()}</div>
    <div class="actions">${button('start-run','Create & start authorized run','primary')}${button('back-target','Edit target')}</div></section></div>
    <details class="panel"><summary>Final target preview</summary><pre>${json(state.target)}</pre></details>`;
}
function estimateView() {
  const e = state.estimate;
  if (!e) return `<p class="hint">Recalculate the estimate after changing limits.</p>`;
  return `<div class="info-box"><strong>${e.tests} test cases · up to ${e.requests} requests</strong><p>~${e.tokens.toLocaleString()} reserved tokens · ~${e.seconds}s baseline runtime<br>Cost: ${e.cost_usd===null?'unavailable':'$'+e.cost_usd.toFixed(4)}<br>${esc(e.pricing)}</p></div>${e.violations.map(v=>`<div class="error-box">${esc(v)}</div>`).join('')}`;
}
function selector(options, id, selected, first='All') {return `<select id="${id}" aria-label="${id}"><option value="">${first}</option>${options.map(o=>`<option ${o===selected?'selected':''}>${esc(o)}</option>`).join('')}</select>`;}
function evidenceView(e) {
  const data=e.evidence;
  if(!data) return '';
  if(data.checks) return `<ul class="review-checks">${data.checks.map(c=>`<li><span class="check-icon ${c.passed?'good':'bad'}">${c.passed?'✓':'!'}</span>${esc(c.check)}</li>`).join('')}</ul>`;
  if(data.queries) return `<ul class="evidence-list">${data.queries.slice(0,8).map(q=>`<li>${esc(q)}</li>`).join('')}</ul>`;
  if(data.objectives) return `<div class="evidence-list">${data.objectives.slice(0,5).map(o=>`<p>${tag(o.severity)} ${esc(o.testing_objective)}</p>`).join('')}<small>${data.objectives.length} objectives in the plan</small></div>`;
  if(data.titles) return `<p class="hint">${data.generated}/${data.requested} cases validated</p><ul class="evidence-list">${data.titles.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
  if(data.classification) return `<div class="evidence-outcome">${tag(data.classification)}<span>${Math.round((data.confidence||0)*100)}% confidence</span>${button('inspect-case','Inspect evidence','',`data-id="${esc(data.test_id)}"`)}</div>`;
  if(data.query) return `<p class="evidence-query">${esc(data.query)}${data.results!==undefined?` · ${data.results} results`:''}</p>`;
  return '';
}
function traceView() {
  const f=state.filters;
  const events=state.events.filter(e=>(!f.agent||e.agent===f.agent)&&(!f.severity||e.severity===f.severity)&&(!f.stage||e.stage===f.stage));
  return events.slice(-100).reverse().map(e=>`<article class="trace-entry"><header><span class="event-agent">${esc(e.agent)}</span>${tag(e.activity||'completed')}<time>${esc(date(e.timestamp))}</time></header><h3>${esc(e.decision)}</h3><p>${esc(e.explanation)}</p>${evidenceView(e)}<small>${esc(e.provider||'local')} / ${esc(e.model||'application checks')}</small><details data-event-id="${e.seq}" ${state.expandedEvents.has(e.seq)?'open':''}><summary>Full decision record</summary><pre>${json({stage:e.stage,evidence:e.evidence,confidence:e.confidence})}</pre></details></article>`).join('')||empty('No matching activity','Actions appear as the agents work. Select an agent to inspect its decisions.');
}
function agentCards() {
  const terminal=state.run&&!['created','running','paused'].includes(state.run.status);
  return state.agents.map((a,i)=>{
    const events=state.events.filter(e=>e.agent===a.name),last=events.at(-1);
    const status=!last?'Waiting':last.activity==='working'?(terminal?'Stopped':state.run?.status==='paused'?'Paused':'Working'):last.activity==='review'?'Reviewed':'Completed';
    return `<button class="agent-card ${state.filters.agent===a.name?'selected':''} ${status.toLowerCase()}" data-action="filter-agent" data-agent="${esc(a.name)}"><div class="agent-card-top"><span class="agent-number">${String(i+1).padStart(2,'0')}</span><span class="agent-state"><i></i>${status}</span></div><h3>${esc(a.label)}</h3><p>${esc(a.purpose)}</p><div class="agent-latest">${esc(last?.decision||'Waiting for its workflow stage')}</div><small>${events.length} recorded actions</small></button>`;
  }).join('');
}
function queueView(r) {
  const cases=r.cases.filter(c=>!state.caseFilter||(r.evaluations.find(e=>e.test_id===c.id)?.classification||(r.active_tests?.includes(c.id)?'ACTIVE':'QUEUED'))===state.caseFilter);
  return cases.length?`<div class="table-scroll"><table><thead><tr><th>Test case</th><th>Boundary</th><th>Result</th><th></th></tr></thead><tbody>${cases.map(c=>`<tr><td><strong>${esc(c.title)}</strong><br><small class="hint">${esc(c.id)} · ${c.turns.length} turn${c.turns.length===1?'':'s'}</small></td><td>${esc(c.component)}</td><td>${tag(r.evaluations.find(e=>e.test_id===c.id)?.classification||(r.active_tests?.includes(c.id)?'ACTIVE':'QUEUED'))}</td><td>${button('inspect-case','Evidence','',`data-id="${esc(c.id)}"`)}</td></tr>`).join('')}</tbody></table></div>`:empty(r.cases.length?'No matching cases':'Designing your test suite',r.cases.length?'Change the result filter.':'The researcher and planner work before requests are dispatched.');
}

function live() {
  const r=state.run;
  if(!r) return heading('Live testing','Watch agent decisions, quality gates and actual execution evidence.',button('new-test','New test run','primary'))+empty('Choose a run to open the agent console','Start a test or open a saved run from History.');
  const controls=(r.status==='created'?button('start','Start run','primary'):'')+(r.status==='running'?button('pause','Pause'):'')+(['paused','failed','limited','interrupted'].includes(r.status)?button('resume','Resume'):'')+(!['completed','cancelled'].includes(r.status)?button('cancel','Cancel','danger'):'')+(r.report?button('show-results','View results','primary'):'')+(r.report&&r.cases.length?button('retest-suite','Retest saved suite'):'');
  return heading('Live testing',`${esc(r.target.application.name)} · ${r.config.mode==='live'?'Live model agents':'Local catalog'} · run ${r.id.slice(0,8)}`,controls)+
    `<div class="stats" id="live-stats">${liveStats(r)}</div><section class="panel run-progress"><div class="split-label"><div>${tag(r.status)} <strong id="stage-label">${esc(r.stage)}</strong></div><span id="completed-label">${r.evaluations.length}/${r.cases.length||r.config.limits.max_tests} cases evaluated</span></div><progress value="${r.evaluations.length}" max="${r.cases.length||1}" aria-label="Execution progress"></progress><p class="hint endpoint-label">${esc(r.target.adapter.endpoint)}</p>${r.error?`<div class="error-box">${esc(r.error)}</div>`:''}${['failed','limited','interrupted'].includes(r.status)?`<details><summary>Adjust limits before resuming</summary><textarea id="resume-limits" rows="10">${json(r.config.limits)}</textarea>${button('save-run-limits','Apply limits & resume')}</details>`:''}</section>
    <section class="panel"><div class="panel-heading inline"><div><h2>Agent control room</h2><p class="hint">Select an agent to inspect its actions. Quality review shows checks applied to each output.</p></div>${tag(r.config.mode==='live'?'LIVE AGENTS':'CATALOG RUN')}</div><div id="agent-cards" class="agent-grid">${agentCards()}</div></section>
    <div class="console-grid"><section class="panel"><div class="panel-heading inline"><h2>Decision stream</h2><span class="hint" id="trace-count">${state.events.length} recorded actions</span></div><div class="trace-toolbar">${selector(state.agents.map(a=>a.name).concat(['LLM Gateway','Orchestrator']),'trace-agent',state.filters.agent,'All agents')}${selector(['info','warning','error','critical','high','medium','low'],'trace-severity',state.filters.severity,'All outcomes')}${selector(['clarification','research','planning','generation','execution','evaluation','reporting','recommendation','review'],'trace-stage',state.filters.stage,'All stages')}</div><div id="trace" class="trace">${traceView()}</div></section>
    <section class="panel"><div class="panel-heading inline"><h2>Execution & evidence</h2>${selector(['PASS','FAIL','ERROR','INCONCLUSIVE','ACTIVE','QUEUED'],'case-filter',state.caseFilter,'All cases')}</div><div id="case-queue">${queueView(r)}</div></section></div>`;
}

function liveStats(r) {
  const counts={PASS:0,FAIL:0,ERROR:0,INCONCLUSIVE:0};r.evaluations.forEach(e=>counts[e.classification]=(counts[e.classification]||0)+1);
  return stat('Cases evaluated',r.evaluations.length+'/'+(r.cases.length||r.config.limits.max_tests),r.stage)+stat('Passed / failed',counts.PASS+' / '+counts.FAIL,'Based on captured responses')+stat('Errors / uncertain',counts.ERROR+' / '+counts.INCONCLUSIVE,'Review before drawing conclusions')+stat('Actual requests',r.usage?.requests||0,`${r.usage?.target_requests||0} target · ${r.usage?.model_requests||0} model`);
}

function results() {
  const r = state.run, report = r?.report;
  if (!report) return heading('Results','Findings grounded in observed behavior.')+empty('No report selected','Open a completed run from history.');
  return heading('Test assessment',`${esc(report.target)} · ${esc(report.status)} · ${esc(report.assessment)}`,`<a class="tag" href="/api/runs/${r.id}/report?format=json&download=true">Download JSON ↓</a><a class="tag" href="/api/runs/${r.id}/report?format=html&download=true">Download HTML ↓</a>`)+
    `<div class="stats">${stat('Passed',report.counts.PASS,'Secure behavior observed')}${stat('Failed',report.counts.FAIL,'Evidence-backed findings')}${stat('Inconclusive',report.counts.INCONCLUSIVE,'Additional assertions needed')}${stat('Errors / skipped',report.counts.ERROR+' / '+report.counts.SKIPPED,'No vulnerability claim')}</div>
    <div class="grid two"><section class="panel"><h2>Findings by severity</h2>${['critical','high','medium','low'].map(s=>`<div class="bar-row"><span>${tag(s)}</span><div class="bar-track"><div class="bar-fill fail" style="width:${(report.severity_counts[s]||0)/Math.max(1,report.counts.FAIL)*100}%"></div></div><strong>${report.severity_counts[s]||0}</strong></div>`).join('')}<p class="hint">${report.tests_executed} tests executed · ${report.usage.elapsed_seconds}s elapsed · ${report.usage.tokens_observed} observed tokens</p></section>
    <section class="panel"><h2>Next-run recommendation</h2><div class="slider-labels"><strong>${report.next_run.exploration}% explore</strong><strong>${report.next_run.exploitation}% retest</strong></div><p>${esc(report.next_run_advice)}</p><p class="hint">Repeated: ${report.repeated_failures.length} · new: ${report.new_failures.length} · resolved: ${report.resolved_failures.length}</p><details><summary>Strategy evidence</summary><pre>${json({contributions:report.next_run.contributions,outcomes:report.strategy_outcomes})}</pre></details></section></div>
    ${r.target.adapter.kind==='campushelp' && r.target.adapter.mode==='weak' && r.target.adapter.endpoint==='http://127.0.0.1:8001/api/chat' && r.target.adapter.engine!=='live' && [50,100,200].includes(r.config.limits.max_tests)?`<section class="panel"><h2>Now verify the fixes</h2><p>Run the same suite with student isolation and tool protections enabled. Compare the two runs in History.</p>${button('run-protected','Retest protected version','primary')}</section>`:''}
    <details class="panel"><summary>All ${r.evaluations.length} evaluated checks and their evidence</summary>${r.evaluations.map(e=>`<details><summary>${tag(e.classification)} ${esc(e.title)}</summary><p><strong>Expected:</strong> ${esc(e.expected)}</p><p><strong>Observed:</strong> ${esc(e.observed)}</p><pre>${json(e.evidence)}</pre></details>`).join('')}</details>
    <section class="panel"><h2>Technical findings</h2>${report.findings.length?report.findings.map(f=>`<details><summary>${tag(f.severity)} ${esc(f.title)} ${f.repeated?tag('REPEATED'):''}</summary><p>${esc(f.plain_description)}</p><p><strong>Expected:</strong> ${esc(f.expected)}</p><p><strong>Observed:</strong> ${esc(f.observed)}</p><p><strong>Classification:</strong> ${esc(f.reason)} · confidence ${Math.round(f.confidence*100)}%</p><p><strong>Consequence:</strong> ${esc(f.consequence)}</p><p><strong>Remediation:</strong> ${esc(f.mitigation)}</p><p class="hint">${esc(f.owasp)} · ${esc(f.component)}</p><pre>${json(f.evidence)}</pre></details>`).join(''):empty('No failures observed','This conclusion applies only to the executed probes.')}</section>
    <section class="panel"><h2>Coverage & all outcomes</h2><p>${report.coverage.map(tag).join(' ')}</p><p class="hint">Uncovered: ${Object.keys(report.uncovered_categories).map(esc).join(', ')}</p><table><thead><tr><th>Test</th><th>Component</th><th>Outcome</th><th>Reason</th></tr></thead><tbody>${report.evaluations.map(e=>`<tr><td>${esc(e.title)}</td><td>${esc(e.component)}</td><td>${tag(e.classification)}</td><td>${esc(e.reason)}</td></tr>`).join('')}</tbody></table></section><div class="info-box">${report.limitations.map(esc).join('<br>')}</div>`;
}
function research() {
  const r = state.run;
  if (!r?.plan) return heading('Research & planning','Review sources, trust boundaries and testing priorities.')+empty('No plan selected','Open a run after its planning stage.');
  return heading('Research & planning',`${esc(r.target.application.name)} · ${r.config.mode} mode`)+
    `<div class="info-box">${esc(r.research?.mode || 'Live Tavily research')} · Research is untrusted evidence. Sources are never executed.</div>
    <div class="grid two"><section class="panel sources"><h2>Evidence sources</h2>${(r.research?.research||[]).map(s=>`<div><strong>${esc(s.title)}</strong>${/^https?:\/\//.test(s.url)?`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.url)} ↗</a>`:''}<p class="hint">${esc(s.content)}</p></div>`).join('')}</section><section class="panel"><h2>Trust boundaries</h2>${(r.plan.trust_boundaries||[]).map(b=>`<p class="tag">${esc(typeof b==='string'?b:JSON.stringify(b))}</p>`).join('')}<h2>Declared architecture</h2><pre>${json(r.target.integration)}</pre></section></div>
    <section class="panel"><h2>Prioritized testing objectives</h2><div class="table-scroll"><table><thead><tr><th>Priority</th><th>Objective</th><th>Component</th><th>OWASP</th><th>Rationale</th></tr></thead><tbody>${r.plan.objectives.map(o=>`<tr><td>${o.priority} ${tag(o.severity)}</td><td>${esc(o.testing_objective)}</td><td>${esc(o.component)}</td><td>${esc(o.owasp)}</td><td>${esc(o.explanation)}<br><span class="hint">${esc(o.evidence)}</span></td></tr>`).join('')}</tbody></table></div></section>`;
}
function historyView() {
  const choices = state.runs.filter(r=>r.report).map(r=>`<option value="${r.id}">${esc(r.target_name)} · ${r.id.slice(0,8)} · ${esc(date(r.created_at))}</option>`).join('');
  return heading('Run history','Persistent evidence, testing allocations and regression comparisons.')+
    `<section class="panel flush">${tableRows(state.runs)}</section><section class="panel"><h2>Compare two runs of the same target</h2><div class="form-grid"><label class="field">Earlier run<select id="compare-first">${choices}</select></label><label class="field">Later run<select id="compare-second">${choices}</select></label></div><p></p>${button('compare','Compare runs')}<div id="comparison"></div></section>`;
}
function settingsView(settings, providers) {
  return heading('Workspace settings','Provider preferences, request limits and local retention.')+
    `<div class="grid two"><section class="panel"><h2>Provider status</h2>${Object.entries(providers).map(([p,s])=>`<div class="split-label"><strong>${esc(p)}</strong>${tag(s.available?'AVAILABLE':s.configured?'CONFIGURED':'NOT CONFIGURED')}</div><p class="hint">${esc(s.availability || s.model || 'Credentials remain server-side.')}</p>`).join('')}<div class="info-box">Availability indicators show configuration, not verified quota. Free models have request limits.</div><h2>Allowed remote scope</h2><pre>${json(settings.allowed_endpoints)}</pre><p class="hint">Configured server-side with LAB_ALLOWED_ENDPOINTS. Every target also requires exact endpoint authorization.</p></section>
    <section class="panel"><h2>Defaults</h2><label class="field">Preferred Gemini model<input id="preferred-model" value="${esc(settings.preferred_model)}"></label><label class="check"><input id="only-free" type="checkbox" checked disabled> Only free models (enforced)</label><label class="field">Default mode<select id="default-mode"><option value="offline" ${settings.mode==='offline'?'selected':''}>offline</option><option value="live" ${settings.mode==='live'?'selected':''}>live</option></select></label><label class="field">Default limits (JSON)<textarea id="settings-limits" rows="15">${json(settings.default_limits)}</textarea></label><label class="field">Retention (days)<input id="retention" type="number" min="1" max="3650" value="${settings.retention_days}"></label><p></p><div class="actions">${button('save-settings','Save settings','primary')}${button('prune','Prune expired run records')}</div><p class="hint">Pruning removes completed database records older than the retention window; downloaded report files remain on disk.</p></section></div>`;
}
async function render() {
  const route = routeName();
  document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active',a.hash==='#'+route));
  $('#breadcrumb').textContent = ({dashboard:'Overview',new:'New test',live:'Live testing',results:'Results',research:'Research & planning',history:'Run history',settings:'Settings'})[route] || 'Overview';
  if (route==='new') {
    if (state.step===1) $('#page').innerHTML = targetForm();
    if (state.step===2) {const q = await api(`/targets/${state.target.id}/clarifications`); $('#page').innerHTML=clarificationForm(q.questions);}
    if (state.step===3) $('#page').innerHTML = strategyForm();
  } else if (route==='settings') {
    const [settings,providers] = await Promise.all([api('/settings'),api('/providers')]); $('#page').innerHTML=settingsView(settings,providers);
  } else {$('#page').innerHTML = ({dashboard,live,results,research,history:historyView}[route]||dashboard)();}
}
async function openRun(id, page) {
  if(state.stream) state.stream.close();
  state.run=await api('/runs/'+id); state.events=(await api('/runs/'+id+'/trace')).events; state.expandedEvents.clear();
  const stream=new EventSource(`/api/runs/${id}/events`); state.stream=stream;
  stream.onmessage = event=>{const item=JSON.parse(event.data); if(!state.events.some(e=>e.seq===item.seq)) state.events.push(item); if(routeName()==='live') refreshLivePanels();};
  stream.addEventListener('done',async()=>{stream.close(); state.run=await api('/runs/'+id); await refreshRuns(); await render();});
  await navigate(page || (state.run.report?'results':'live'));
}
async function calculateEstimate() {
  if($('#limits')) state.limits=JSON.parse($('#limits').value);
  if($('#test-count')) state.limits.max_tests=Number($('#test-count').value);
  if($('#run-budget')) state.limits.budget_usd=Number($('#run-budget').value);
  if($('#run-price')) state.limits.price_per_million=$('#run-price').value===''?null:Number($('#run-price').value);
  if($('#run-seconds')) state.limits.max_seconds=Number($('#run-seconds').value);
  if($('#agent-mode')) state.mode=$('#agent-mode').value;
  state.estimate=await api('/estimate','POST',{target_id:state.target.id,exploration:state.exploration,limits:state.limits,mode:state.mode});
  if($('#estimate-output')) $('#estimate-output').innerHTML=estimateView();
}
async function action(name, el) {
  clearNotice();
  if(name==='run-demo' || name==='run-protected') {
    const mode=name==='run-protected'?'hardened':$('#demo-protection').value;
    const tests=name==='run-protected'?([50,100,200].includes(state.run.config.limits.max_tests)?state.run.config.limits.max_tests:100):Number($('#demo-count').value);
    const run=await api('/demo-runs','POST',{mode,tests,...(name==='run-protected'?{source_run_id:state.run.id}:{})});
    await refreshRuns();await openRun(run.id,'live');
  }
  if(name==='try-demo') {state.target=await api('/demo-target'); state.step=1; await navigate('new');}
  if(name==='new-test') {state.mode=['gemini','openrouter','groq','xkiro'].some(p=>state.providers[p]?.configured)?'live':'offline';state.limits={...state.limits,max_tests:100,max_seconds:600,timeout_seconds:30,price_per_million:1};state.target=null;state.step=1;await navigate('new');}
  if(name==='import-example') {state.target=await api('/example');state.step=1;await render();}
  if(name==='back-target') {state.step=1;await render();}
  if(name==='configure-target') {state.target=await api('/targets/'+el.dataset.id);state.step=1;await navigate('new');}
  if(name==='filter-agent') {state.filters.agent=state.filters.agent===el.dataset.agent?'':el.dataset.agent;$('#trace-agent').value=state.filters.agent;refreshLivePanels();}
  if(name==='inspect-case') inspectCase(el.dataset.id);
  if(name==='retest-suite') {const run=await api('/runs/'+state.run.id+'/retest','POST');await refreshRuns();await openRun(run.id,'live');}
  if(name==='close-case') $('#case-dialog').close();
  if(name==='save-target' || name==='probe-target') {
    const t=JSON.parse($('#target-json').value); delete t.id;
    t.application={...t.application,name:$('#target-name').value.trim(),purpose:$('#target-purpose').value,requirements:$('#target-requirements').value};
    t.llm={...t.llm,provider:$('#target-provider').value,model:$('#target-model').value,model_version:$('#target-model').value};
    const choice=id=>$('#'+id).value==='unknown'?null:$('#'+id).value==='yes';
    t.integration={...t.integration,rag_enabled:choice('target-rag'),tools_enabled:choice('target-tools'),conversation_memory:choice('target-memory')};
    if(!t.application.name) throw Error('Enter an application name.');
    t.adapter={...t.adapter,endpoint:$('#target-url').value.trim(),kind:$('#target-kind').value,mode:$('#target-mode').value,engine:$('#target-engine').value,auth_env:$('#target-auth-env').value.trim()};
    if($('#api-preset').value==='openai' && $('#target-model').value.trim() && $('#target-model').value.trim()!=='Unknown') t.adapter.request_template.model=$('#target-model').value.trim();
    t.testing_scope={...t.testing_scope,environment:$('#target-environment').value,authorized:$('#authorized').checked,allowed_endpoints:$('#authorized').checked?[t.adapter.endpoint]:[]};
    state.target=await api('/targets/import','POST',t);
    if(name==='probe-target'){const p=await api('/targets/'+state.target.id+'/probe','POST');$('#probe-result').innerHTML=`<div class="${p.connected?'info-box':'error-box'}"><strong>${p.connected?'Connected':'Connection needs attention'}</strong><p>HTTP ${esc(p.status)} · ${esc(p.latency_ms)} ms</p>${p.error?`<p>${esc(p.error)}</p>`:''}<p>${esc(p.response_preview)}</p><small>Response fields: ${p.response_fields.map(esc).join(', ')}</small></div>`;}else{state.step=2;await render();}
  }
  if(name==='save-answers') {
    const answers={}; document.querySelectorAll('[data-question]').forEach(field=>{
      const type=field.dataset.type; const id=field.dataset.question;
      if(type==='multiple') answers[id]=[...field.querySelectorAll('input:checked')].map(i=>i.value);
      else if(type==='single') {const input=field.querySelector('input:checked');if(input) answers[id]=input.value;}
      else {const value=field.querySelector('input,textarea').value;if(value) answers[id]=value;}
    });
    const response=await api(`/targets/${state.target.id}/clarifications`,'POST',answers);state.target=response.target;
    if(response.questions.some(q=>q.essential)) throw Error('Resolve authorization and the exact endpoint before continuing.');
    state.recommendation=await api(`/targets/${state.target.id}/recommendation`);state.exploration=state.recommendation.exploration;
    state.step=3;await calculateEstimate();await render();
  }
  if(name==='apply-recommendation') {state.exploration=state.recommendation.exploration;await calculateEstimate();await render();}
  if(name==='estimate') await calculateEstimate();
  if(name==='start-run') {
    await calculateEstimate();if(!state.estimate.can_start) throw Error('Adjust scope or limits to resolve the displayed budget violations.');
    const run=await api('/runs','POST',{target_id:state.target.id,exploration:state.exploration,limits:state.limits,mode:state.mode});
    await api('/runs/'+run.id+'/start','POST'); await refreshRuns();await openRun(run.id,'live');
  }
  if(name==='open-run') await openRun(el.dataset.id);
  if(['start','pause','resume','cancel'].includes(name)) {if(!state.run) throw Error('Select a run first.');state.run=await api('/runs/'+state.run.id+'/'+name,'POST');if(['start','resume'].includes(name))await openRun(state.run.id,'live');else await render();}
  if(name==='save-run-limits'){state.run=await api('/runs/'+state.run.id+'/limits','PATCH',JSON.parse($('#resume-limits').value));state.run=await api('/runs/'+state.run.id+'/resume','POST');await openRun(state.run.id,'live');}
  if(name==='show-results') {await navigate('results');}
  if(name==='compare') {const result=await api(`/compare?first=${$('#compare-first').value}&second=${$('#compare-second').value}`);$('#comparison').innerHTML=`<div class="info-box">Resolved ${result.resolved.length} · repeated ${result.repeated.length} · new ${result.new.length} · not retested ${result.not_retested.length}</div><pre>${json(result)}</pre>`;}
  if(name==='save-settings') {const settings=await api('/settings','PUT',{mode:$('#default-mode').value,preferred_model:$('#preferred-model').value,only_free:$('#only-free').checked,retention_days:Number($('#retention').value),default_limits:JSON.parse($('#settings-limits').value)});state.limits=settings.default_limits;state.mode=settings.mode;await render();}
  if(name==='prune') {const result=await api('/maintenance/prune','POST');await refreshRuns();notice(result.deleted_runs+' expired run records removed.');}
}
document.addEventListener('click',async event=>{const el=event.target.closest('[data-action]');if(!el)return;el.disabled=true;try{await action(el.dataset.action,el);}catch(error){notice(error);}finally{el.disabled=false;}});
document.addEventListener('input',event=>{if(event.target.id==='exploration'){state.exploration=Number(event.target.value);$('#explore-label').textContent=state.exploration+'%';$('#exploit-label').textContent=(100-state.exploration)+'%';$('#exploration-warning').hidden=state.exploration<=65;state.estimate=null;$('#estimate-output').innerHTML=estimateView();}});
document.addEventListener('change',async event=>{
  try {
    if(event.target.id==='import-file'&&event.target.files[0]){state.target=JSON.parse(await event.target.files[0].text());await render();}
    if(event.target.id==='api-preset'){applyPreset(event.target.value);}
    if(event.target.id==='case-filter'){state.caseFilter=event.target.value;$('#case-queue').innerHTML=queueView(state.run);}
    if(event.target.id.startsWith('trace-')){state.filters[event.target.id.slice(6)]=event.target.value;$('#trace').innerHTML=traceView();}
  }catch(error){notice(error);}
});
window.addEventListener('hashchange',()=>render().catch(notice));
function applyPreset(preset) {
  if(preset==='custom') return;
  const t=JSON.parse($('#target-json').value); t.adapter=t.adapter||{};
  if(preset==='campushelp'){action('try-demo').catch(notice);return;}
  t.adapter.kind='http';
  t.adapter.request_template=preset==='openai'?{messages:'{messages}',max_tokens:'{max_tokens}',stream:false}:{message:'{input}',session_id:'{session}',max_tokens:'{max_tokens}'};
  t.adapter.response_path=preset==='openai'?'choices.0.message.content':'response';
  t.adapter.tool_calls_path=preset==='openai'?'choices.0.message.tool_calls':'tool_calls';
  $('#target-json').value=JSON.stringify(t,null,2);$('#target-kind').value='http';
}
function inspectCase(id) {
  const r=state.run,c=r?.cases.find(c=>c.id===id);if(!c)return;
  const evaluation=r.evaluations.find(e=>e.test_id===id),execution=r.executions.find(e=>e.test_id===id);
  $('#case-dialog-content').innerHTML=`<div class="panel-heading inline"><div><div class="eyebrow">CAPTURED TEST EVIDENCE</div><h2>${esc(c.title)}</h2></div>${button('close-case','Close')}</div><p>${tag(evaluation?.classification||'QUEUED')} ${esc(c.component)} · ${esc(c.owasp)}</p><h3>Inputs</h3>${c.turns.map(t=>`<div class="evidence-block"><small>${esc(t.user)}</small><p>${esc(t.input)}</p></div>`).join('')}<h3>Expected behaviour</h3><p>${esc(c.expected)}</p><pre>${json(c.assertions)}</pre><h3>Observed responses</h3>${execution?execution.turns.map(t=>`<div class="evidence-block"><small>HTTP ${esc(t.status)} · ${esc(t.latency_ms)} ms · ${esc(t.provider)} / ${esc(t.model)}</small><p>${esc(t.response)}</p>${t.error?`<p class="bad">${esc(t.error)}</p>`:''}<details><summary>Tools and complete response</summary><pre>${json({tool_calls:t.tool_calls,body:t.body})}</pre></details></div>`).join(''):'<p class="hint">This case has not executed yet.</p>'}${evaluation?`<h3>Evaluation decision</h3><p>${esc(evaluation.reason)}</p><p class="hint">Confidence ${Math.round(evaluation.confidence*100)}% · ${esc(evaluation.judge.provider)} / ${esc(evaluation.judge.model)}</p>`:''}`;
  if(!$('#case-dialog').open)$('#case-dialog').showModal();
}
function refreshLivePanels() {
  if(!state.run||routeName()!=='live')return;
  if($('#trace'))$('#trace').innerHTML=traceView();
  if($('#agent-cards'))$('#agent-cards').innerHTML=agentCards();
  if($('#trace-count'))$('#trace-count').textContent=state.events.length+' recorded actions';
  if($('#live-stats'))$('#live-stats').innerHTML=liveStats(state.run);
  if($('#case-queue'))$('#case-queue').innerHTML=queueView(state.run);
  if($('#stage-label'))$('#stage-label').textContent=state.run.stage;
  if($('#completed-label'))$('#completed-label').textContent=state.run.evaluations.length+'/'+(state.run.cases.length||state.run.config.limits.max_tests)+' cases evaluated';
  const progress=$('progress');if(progress){progress.max=state.run.cases.length||1;progress.value=state.run.evaluations.length;}
}
document.addEventListener('toggle',event=>{const id=Number(event.target.dataset?.eventId);if(id){if(event.target.open)state.expandedEvents.add(id);else state.expandedEvents.delete(id);}},true);
async function boot(){try{
  const [health,settings,manifest,providers,targets]=await Promise.all([api('/health'),api('/settings'),api('/agents'),api('/providers'),api('/targets')]);
  $('#product-name').textContent=health.product;document.title=health.product;$('#connection').textContent='Workspace connected';
  state.limits=settings.default_limits;state.mode=settings.mode;state.agents=manifest.agents;state.providers=providers;state.targets=targets;
  await refreshRuns();await render();
}catch(error){notice(error);$('#connection').textContent='Connection error';}}
setInterval(async()=>{if(state.run&&['running','paused','created'].includes(state.run.status)){try{state.run=await api('/runs/'+state.run.id);if(routeName()==='live')refreshLivePanels();}catch(error){notice(error);}}},1500);
boot();
