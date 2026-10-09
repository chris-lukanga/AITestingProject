let session = crypto.randomUUID();
let busy = false;
const $ = id => document.getElementById(id);
function reset() {session = crypto.randomUUID(); $('messages').replaceChildren(); $('error').textContent = '';}
$('reset').onclick = reset;
$('user').onchange = reset;
$('mode').onchange = reset;
function add(text, kind) {
  const article = document.createElement('article'); article.className = kind; article.textContent = text;
  $('messages').append(article); article.scrollIntoView({block:'nearest'}); return article;
}
async function send(message) {
  if (busy || !message.trim()) return;
  busy = true; $('send').disabled = true; $('send').textContent = 'Thinking…';
  add(message, 'user'); $('message').value = ''; $('error').textContent = '';
  const requestSession = session;
  try {
    const response = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message, user:$('user').value, mode:$('mode').value, engine:$('engine').value, session_id:requestSession})});
    const data = await response.json(); if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Please check your question and try again.');
    if (session !== requestSession) return;
    const article = add(data.response, 'assistant');
    for (const source of data.sources || []) {
      const detail = document.createElement('details'); detail.className = 'citation';
      const summary = document.createElement('summary'); summary.textContent = 'Source: ' + source.title;
      const text = document.createElement('p'); text.textContent = source.text;
      detail.append(summary, text); article.append(detail);
    }
    const meta = document.createElement('small'); meta.className = 'answer-meta';
    meta.textContent = data.provider === 'local' ? 'Handbook retrieval / application controls' : 'Live AI · ' + data.provider + ' / ' + data.model;
    article.append(meta);
    if (data.pending_ticket) {
      const actions = document.createElement('div'); actions.className = 'ticket-actions';
      for (const label of ['Confirm ticket', 'Cancel']) {
        const button = document.createElement('button'); button.textContent = label;
        button.onclick = () => {actions.remove(); send(label);}; actions.append(button);
      }
      article.append(actions);
    }
    article.scrollIntoView({block:'nearest'});
  } catch (error) {if (session === requestSession) $('error').textContent = error.message;}
  finally {busy = false; $('send').disabled = false; $('send').textContent = 'Send'; $('message').focus();}
}
$('chat').onsubmit = event => {event.preventDefault(); send($('message').value);};
document.addEventListener('click', event => {
  const button = event.target.closest('[data-prompt]'); if (!button) return;
  if (button.dataset.prompt.startsWith('Create')) {$('message').value = button.dataset.prompt; $('message').focus();}
  else send(button.dataset.prompt);
});
async function boot() {
  try {
    const [health, handbook] = await Promise.all([fetch('/api/health').then(r=>r.json()), fetch('/api/policies').then(r=>r.json())]);
    $('provider-status').textContent = health.live_available ? 'Live AI is configured. Select it above to use your provider; provider charges may apply.' : 'Ready without setup. For live AI, add a Gemini or OpenRouter key to .env and restart.';
    $('engine').querySelector('[value="live"]').disabled = !health.live_available;
    for (const policy of handbook.policies) {
      const detail = document.createElement('details'); const summary = document.createElement('summary');
      summary.textContent = policy.title; const text = document.createElement('p'); text.textContent = policy.text;
      detail.append(summary, text); $('handbook').append(detail);
    }
  } catch (error) {$('provider-status').textContent = 'Could not load the handbook. Refresh to retry.';}
}
boot();
