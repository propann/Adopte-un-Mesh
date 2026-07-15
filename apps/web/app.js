const apiBase = '';
const statusEl = document.querySelector('#status');
const profilesEl = document.querySelector('#profiles');

async function checkHealth() {
  try {
    const res = await fetch(`${apiBase}/health`);
    const data = await res.json();
    statusEl.textContent = data.ok ? 'Bunker en ligne · zombies contenus' : 'Bunker instable';
  } catch (err) {
    statusEl.textContent = 'API hors portee · verifier le Pi 5';
  }
}

async function createProfile() {
  const payload = {
    display_name: document.querySelector('#displayName').value || 'Signal inconnu',
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
      div.className = `profile profile-${profile.freshness || 'gray'}`;
      const age = profile.age ? ` · ${profile.age} ans` : '';
      const radio = profile.rssi ? ` · RSSI ${profile.rssi} dBm` : '';
      const contact = profile.contact_hint ? `Contact mesh : ${profile.contact_hint}` : `ID mesh : ${profile.public_id}`;
      div.innerHTML = `
        <div class="avatar">${escapeHtml(profile.avatar_heart || '♡')}</div>
        <div>
          <strong>${escapeHtml(profile.display_name)}${age} · ${escapeHtml(profile.public_id)}</strong>
          <small>${freshnessLabel(profile.freshness)} · ${escapeHtml(profile.intent)} · ${escapeHtml(profile.zone)}${radio}</small>
          <p>${escapeHtml(profile.bio || 'Bio cryptee par timidite.')}</p>
          <small>${escapeHtml(profile.tags.join(', '))}</small>
          <button class="ghost" type="button" onclick="navigator.clipboard?.writeText('${escapeJs(contact)}')">Copier contact</button>
        </div>`;
      profilesEl.appendChild(div);
    }
  } catch (err) {
    profilesEl.innerHTML = '<p>Impossible de scanner. Le Pi 5 medite ou le zombie a mange le cable.</p>';
  }
}

function freshnessLabel(value) {
  if (value === 'green') return 'A portee maintenant';
  if (value === 'orange') return 'Vu recemment';
  return 'Signal ancien';
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function escapeJs(value) {
  return String(value).replaceAll('\\', '\\\\').replaceAll("'", "\\'");
}

document.querySelector('#createBtn').addEventListener('click', createProfile);
document.querySelector('#refreshBtn').addEventListener('click', loadProfiles);
checkHealth();
loadProfiles();
