const $ = selector => document.querySelector(selector);
const format = new Intl.NumberFormat('pt-BR');
const state = { data: null, visible: 8 };
function node(tag, text, className) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el; }
function filtered() { const q = $('#search').value.trim().toUpperCase(), s = $('#status').value; return state.data.control.filter(item => item.key.includes(q) && (s === 'all' || item.status === s)); }
function renderTable() {
  const data = filtered(), body = $('#rows'); body.replaceChildren();
  for (const item of data.slice(0, state.visible)) {
    const row = node('tr');
    for (const value of [item.key, item.service, item.unit, item.history.join(' → ')]) row.append(node('td', value));
    const status = node('td'); status.append(node('span', item.status === 'SUCESSO' ? 'Sucesso' : 'Erro', `status-pill ${item.status === 'SUCESSO' ? 'ok' : 'error'}`)); row.append(status);
    const action = node('td'), button = node('button', 'Ver trilha ↗', 'detail-button'); button.addEventListener('click', () => detail(item)); action.append(button); row.append(action); body.append(row);
  }
  if (!data.length) { const row = node('tr'), cell = node('td', 'Nenhum registro corresponde aos filtros.'); cell.colSpan = 6; row.append(cell); body.append(row); }
  $('#count').textContent = `${Math.min(state.visible, data.length)} de ${data.length} registros`; $('#more').hidden = state.visible >= data.length;
}
function detail(item) {
  const root = $('#detail-content'); root.replaceChildren(node('h2', item.key), node('p', `${item.service} · ${item.unit} · dado fictício`), node('h3', 'Histórico de estados'));
  const history = node('div', undefined, 'history'); for (const step of item.history) history.append(node('span', step));
  root.append(history, node('h3', 'Resposta'), node('div', item.message, 'message'), node('h3', 'Regra de controle'), node('pre', item.payloadPrepared ? 'Payload genérico preparado; resultado confirmado somente após consulta simulada.' : 'Validação bloqueou a preparação. Nenhum envio simulado foi feito.'));
  $('#detail').showModal();
}
function render() {
  const data = state.data, m = data.metrics;
  for (const key of ['total', 'prepared', 'success', 'errors', 'services']) $(`#${key}`).textContent = format.format(m[key]);
  const pct = m.success / m.total * 100; $('#rate').textContent = `${Math.round(pct)}%`; $('#donut').style.setProperty('--done', `${pct}%`);
  $('#legend-success').textContent = m.success; $('#legend-errors').textContent = m.errors; $('#equation').textContent = `${m.total} gerados = ${m.success} sucesso + ${m.errors} erro`;
  const phases = $('#phases'); phases.replaceChildren(); phases.style.gridTemplateColumns = 'repeat(3, 1fr)';
  for (const [index, step] of data.ledger.entries()) { const el = node('div', undefined, 'phase'); el.append(node('div', '✓', 'phase-circle'), node('b', step.operation), node('small', `${step.processed}/${step.total} · ${step.state}`)); phases.append(el); }
  const entities = $('#entity-list'); entities.replaceChildren(); for (const service of data.byService) { const card = node('article', undefined, 'entity'), head = node('div', undefined, 'entity-head'), track = node('div', undefined, 'track'), fill = node('div'); head.append(node('b', service.service), node('span', `${service.success} / ${service.total}`)); fill.style.width = `${service.success / service.total * 100}%`; track.append(fill); card.append(head, node('p', `${service.errors} para revisão · ${service.total} gerados`), track); entities.append(card); }
  renderTable();
}
async function init() { try { const res = await fetch('data/snapshot.json'); if (!res.ok) throw new Error(`HTTP ${res.status}`); state.data = await res.json(); $('#search').addEventListener('input', () => { state.visible = 8; renderTable(); }); $('#status').addEventListener('change', () => { state.visible = 8; renderTable(); }); $('#more').addEventListener('click', () => { state.visible += 8; renderTable(); }); $('#close').addEventListener('click', () => $('#detail').close()); render(); } catch (error) { $('#count').textContent = 'Falha ao carregar os dados do demo.'; console.error(error); } }
init();
