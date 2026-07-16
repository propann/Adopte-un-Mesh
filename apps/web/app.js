const apiBase = `${location.protocol}//${location.host}`;
const state = {
  me: localStorage.getItem('adopte_public_id') || '',
  profiles: [],
};

const $ = (selector) => document.querySelector(selector);

function setText(id, value) {
  const el = document.querySelector(id);
  if (el) el.textContent = value;
}

async function api(path, options = {}) {
  const res = await fetch(`${apiBase}${path}`, options);
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  if (!res.ok) throw new Error(data.detail || data.raw || `HTTP ${res.status}`);
  return data;
}

async function checkHealth() {
  try {
    const data = await api('/api/health');
    setText('#status', data.ok ? `Bunker en ligne · ${data.version || 'v?'}` : 'Bunker instable');
  } catch {
    setText('#status', 'API hors portée · vérifier le Pi 5');
  }
}

async function loadStats() {
  try {
    const stats = await api('/api/stats');
    setText('#statActive', stats.profiles_active ?? '0');
    setText('#statTotal', stats.profiles_total ?? '0');
    setText('#statReports', stats.reports_open ?? '0');
    setText('#statEvents', stats.mesh_events_24h ?? '0');
  } catch {
    setText('#statActive', '—');
    setText('#statTotal', '—');
    setText('#statReports', '—');
    setText('#statEvents', '—');
  }
}

async function createProfile() {
  const ageValue = $('#age').value;
  const tags = $('#tags').value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 8);
  const payload = {
    display_name: $('#displayName').value || 'Signal inconnu',
    age: ageValue ? Number(ageValue) : null,
    genre_recherche: $('#genreRecherche').value || '',
    bio: $('#bio').value || '',
    intent: $('#intent').value,
    tags: tags.length ? tags : ['mesh', 'local'],
    avatar_heart: $('#heart').value,
  };
  try {
    const data = await api('/api/profiles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    state.me = data.public_id;
    localStorage.setItem('adopte_public_id', state.me);
    $('#profileResult').textContent = `Profil allumé : ${data.public_id}\nGraine avatar : ${data.avatar_seed}\nCe code reste ton identité locale pour liker/signaler.`;
    await Promise.all([loadProfiles(), loadStats()]);
  } catch (err) {
    $('#profileResult').textContent = `Erreur création : ${err.message}`;
  }
}

async function loadProfiles() {
  const container = $('#profiles');
  try {
    const data = await api('/api/active');
    state.profiles = data.profiles || [];
    container.innerHTML = '';
    if (!state.profiles.length) {
      container.innerHTML = '<p class="empty">Aucun signal. Le désert radio respire encore.</p>';
      return;
    }
    for (const profile of state.profiles) {
      container.appendChild(renderProfile(profile));
    }
  } catch (err) {
    container.innerHTML = `<p class="empty">Impossible de scanner : ${escapeHtml(err.message)}</p>`;
  }
}

function renderProfile(profile) {
  const template = $('#profileTemplate').content.cloneNode(true);
  const card = template.querySelector('.profile-card');
  card.classList.add(profile.freshness || 'gray');
  card.dataset.publicId = profile.public_id;

  const age = profile.age ? ` · ${profile.age}` : '';
  const since = formatSince(profile.seconds_since_seen);
  const rssi = profile.rssi ?? '?';
  const snr = profile.snr ?? '?';
  const tags = (profile.tags || []).map((tag) => `<span>${escapeHtml(tag)}</span>`).join('');

  template.querySelector('.profile-avatar').textContent = profile.avatar_heart || '♡';
  template.querySelector('.profile-title').textContent = `${profile.display_name}${age} · ${profile.public_id}`;
  template.querySelector('.profile-meta').textContent = `${profile.intent || 'signal'} · ${profile.zone || 'local'} · vu ${since} · RSSI ${rssi} · SNR ${snr}`;
  template.querySelector('.profile-bio').textContent = profile.bio || 'Bio cryptée par timidité.';
  template.querySelector('.profile-tags').innerHTML = tags || '<span>mesh</span>';

  template.querySelector('[data-action="like"]').addEventListener('click', () => likeProfile(profile.public_id));
  template.querySelector('[data-action="report"]').addEventListener('click', () => reportProfile(profile.public_id));
  template.querySelector('[data-action="block"]').addEventListener('click', () => blockProfile(profile.public_id));
  return template;
}

async function likeProfile(targetId) {
  if (!state.me) return alert('Crée d’abord ton profil local : le cœur a besoin d’une adresse de retour.');
  try {
    const data = await api(`/api/profiles/${encodeURIComponent(targetId)}/like`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_public_id: state.me, mode: 'soft' }),
    });
    alert(data.match ? `Match ${data.match_id} · le bunker applaudit.` : 'Intérêt envoyé. Petit cœur, grande antenne.');
    await loadStats();
  } catch (err) {
    alert(`Like impossible : ${err.message}`);
  }
}

async function reportProfile(targetId) {
  if (!state.me) return alert('Crée d’abord ton profil local pour signaler proprement.');
  const reason = prompt('Raison du signalement ? spam, harcèlement, faux profil...');
  if (!reason) return;
  try {
    const data = await api(`/api/profiles/${encodeURIComponent(targetId)}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_public_id: state.me, reason }),
    });
    alert(`Signalement ${data.report_id} enregistré. Zombie dans le sas.`);
    await loadStats();
  } catch (err) {
    alert(`Report impossible : ${err.message}`);
  }
}

async function blockProfile(targetId) {
  if (!confirm('Bloquer ce profil sur le hub local ?')) return;
  try {
    const options = state.me
      ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ from_public_id: state.me }) }
      : { method: 'POST' };
    await api(`/api/profiles/${encodeURIComponent(targetId)}/block`, options);
    await Promise.all([loadProfiles(), loadStats()]);
  } catch (err) {
    alert(`Blocage impossible : ${err.message}`);
  }
}

async function loadCommands() {
  try {
    const data = await api('/api/radio/commands');
    $('#commands').textContent = data.commands.join('\n') + '\n\n' + data.warning;
  } catch (err) {
    $('#commands').textContent = `Erreur commandes : ${err.message}`;
  }
}

async function loadConfig() {
  try {
    const data = await api('/api/radio/config');
    $('#commands').textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    $('#commands').textContent = `Erreur config : ${err.message}`;
  }
}

async function injectMeshPayload() {
  try {
    const data = await api('/api/mesh/inbound', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload: $('#meshPayload').value, source: 'web-test', node_id: '!webtest', rssi: -64, snr: 8.2 }),
    });
    $('#meshResult').textContent = JSON.stringify(data, null, 2);
    await Promise.all([loadProfiles(), loadStats()]);
  } catch (err) {
    $('#meshResult').textContent = `Erreur injection : ${err.message}`;
  }
}

async function loadAdmin() {
  const token = $('#adminToken').value.trim();
  const headers = token ? { 'X-Admin-Token': token } : {};
  try {
    const [reports, events, stats] = await Promise.all([
      api('/api/admin/reports', { headers }),
      api('/api/admin/events', { headers }),
      api('/api/stats'),
    ]);
    $('#adminOutput').innerHTML = `
      <h3>Stats</h3><pre>${escapeHtml(JSON.stringify(stats, null, 2))}</pre>
      <h3>Reports</h3><pre>${escapeHtml(JSON.stringify(reports.reports.slice(0, 10), null, 2))}</pre>
      <h3>Derniers paquets mesh</h3><pre>${escapeHtml(JSON.stringify(events.events.slice(0, 10), null, 2))}</pre>`;
  } catch (err) {
    $('#adminOutput').innerHTML = `<p class="empty">Admin inaccessible : ${escapeHtml(err.message)}</p>`;
  }
}

async function loadMatches() {
  try {
    const data = await api('/api/matches');
    $('#adminOutput').innerHTML = `<h3>Matches</h3><pre>${escapeHtml(JSON.stringify(data.matches, null, 2))}</pre>`;
  } catch (err) {
    $('#adminOutput').innerHTML = `<p class="empty">Matches inaccessibles : ${escapeHtml(err.message)}</p>`;
  }
}

function formatSince(seconds) {
  if (seconds == null) return 'récemment';
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}min`;
  return `${Math.floor(seconds / 3600)}h`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

$('#createBtn').addEventListener('click', createProfile);
$('#refreshBtn').addEventListener('click', () => Promise.all([loadProfiles(), loadStats()]));
$('#commandsBtn').addEventListener('click', loadCommands);
$('#configBtn').addEventListener('click', loadConfig);
$('#meshTestBtn').addEventListener('click', injectMeshPayload);
$('#adminLoadBtn').addEventListener('click', loadAdmin);
$('#matchesBtn').addEventListener('click', loadMatches);

checkHealth();
loadStats();
loadProfiles();
