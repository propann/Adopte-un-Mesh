const apiBase = `${location.protocol}//${location.host}`;
const statusEl = document.querySelector('#status');
const profilesEl = document.querySelector('#profiles');

async function checkHealth() {
  try {
    const res = await fetch(`${apiBase}/api/health`);
    const data = await res.json();
    statusEl.textContent = data.ok ? 'Bunker en ligne · zombies contenus' : 'Bunker instable';
  } catch {
    statusEl.textContent = 'API hors portee · verifier le Pi 5';
  }
}

async function createProfile() {
  const ageValue = document.querySelector('#age').value;
  const payload = {
    display_name: document.querySelector('#displayName').value || 'Signal inconnu',
    age: ageValue ? Number(ageValue) : null,
    genre_recherche: document.querySelector('#genreRecherche').value || '',
    bio: document.querySelector('#bio').value || '',
    intent: document.querySelector('#intent').value,
    tags: ['mesh', 'local'],
    avatar_heart: document.querySelector('#heart').value,
  };
  const res = await fetch(`${apiBase}/profiles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  document.querySelector('#profileResult').textContent = JSON.stringify(data, null, 2);
  await loadProfiles();
}

async function loadProfiles() {
  try {
    const res = await fetch(`${apiBase}/api/active`);
    const data = await res.json();
    profilesEl.innerHTML = '';
    if (!data.profiles?.length) {
      profilesEl.innerHTML = '<p>Aucun signal. Le desert radio respire encore.</p>';
      return;
    }
    for (const profile of data.profiles) {
      const div = document.createElement('div');
      div.className = `profile ${profile.freshness || 'gray'}`;
      const rssi = profile.rssi ?? '?';
      const age = profile.age ? ` · ${profile.age}` : '';
      div.innerHTML = `
        <div class="avatar">${escapeHtml(profile.avatar_heart || '♡')}</div>
        <div>
          <strong>${escapeHtml(profile.display_name)}${age} · ${escapeHtml(profile.public_id)}</strong>
          <small>${escapeHtml(profile.intent)} · ${escapeHtml(profile.zone)} · RSSI ${escapeHtml(rssi)}</small>
          <p>${escapeHtml(profile.bio || 'Bio cryptee par timidite.')}</p>
          <code>Contact: ${escapeHtml(profile.contact_hint || profile.node_id || profile.public_id)}</code>
        </div>`;
      profilesEl.appendChild(div);
    }
  } catch {
    profilesEl.innerHTML = '<p>Impossible de scanner. Le Pi 5 medite ou le zombie a mange le cable.</p>';
  }
}

async function loadCommands() {
  const res = await fetch(`${apiBase}/api/radio/commands`);
  const data = await res.json();
  document.querySelector('#commands').textContent = data.commands.join('\n') + '\n\n' + data.warning;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

document.querySelector('#createBtn').addEventListener('click', createProfile);
document.querySelector('#refreshBtn').addEventListener('click', loadProfiles);
document.querySelector('#commandsBtn').addEventListener('click', loadCommands);
checkHealth();
loadProfiles();
