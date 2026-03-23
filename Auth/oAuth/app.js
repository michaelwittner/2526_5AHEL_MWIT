// Spotify Authorization Code with PKCE (client-side)
// Expects Vite env variable: VITE_SPOTIFY_CLIENT_ID
// Register redirect URI in your Spotify Developer Dashboard (e.g. http://localhost:5173)

// DOM elements
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorDetails = document.getElementById('error-details');
const app = document.getElementById('app');
const loggedOutSection = document.getElementById('logged-out');
const loggedInSection = document.getElementById('logged-in');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const profileContainer = document.getElementById('profile');
const topTracksContainer = document.getElementById('top-tracks');
const topArtistsContainer = document.getElementById('top-artists');
const profileModal = document.getElementById('profile-modal');
const modalCloseBtn = document.getElementById('modal-close-btn');
const listsContent = document.getElementById('lists-content');
const profileAvatar = document.getElementById('profile-avatar');

const CLIENT_ID = import.meta.env.VITE_SPOTIFY_CLIENT_ID;
const REDIRECT_URI = "http://127.0.0.1:5173"; // must match the registered redirect URI
const SCOPES = [
  'user-read-private',
  'user-read-email',
  'user-top-read',
  'playlist-read-private',
  'playlist-read-collaborative'
].join(' ');

function showLoading() {
  loading.style.display = 'block';
  error.style.display = 'none';
  app.style.display = 'none';
}

function hideLoading() {
  loading.style.display = 'none';
  app.style.display = 'flex';
}

function showError(message) {
  loading.style.display = 'none';
  app.style.display = 'none';
  error.style.display = 'block';
  errorDetails.textContent = message;
}

function showLoggedIn() {
  loggedOutSection.style.display = 'none';
  loggedInSection.style.display = 'flex';
}

function showLoggedOut() {
  loggedInSection.style.display = 'none';
  loggedOutSection.style.display = 'flex';
}

// PKCE helpers
function base64UrlEncode(buffer) {
  return btoa(String.fromCharCode.apply(null, new Uint8Array(buffer)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

async function sha256(plain) {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return await crypto.subtle.digest('SHA-256', data);
}

function generateCodeVerifier() {
  const array = new Uint8Array(64);
  crypto.getRandomValues(array);
  return base64UrlEncode(array);
}

async function generateCodeChallenge(verifier) {
  const hashed = await sha256(verifier);
  return base64UrlEncode(hashed);
}

// Create authorization URL and redirect
async function login() {
  try {
    if (!CLIENT_ID) throw new Error('VITE_SPOTIFY_CLIENT_ID not set');
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);



  sessionStorage.setItem('spotify_code_verifier', codeVerifier);

    const params = new URLSearchParams({
      response_type: 'code',
      client_id: CLIENT_ID,
      scope: SCOPES,
      redirect_uri: REDIRECT_URI,
      code_challenge_method: 'S256',
      code_challenge: codeChallenge,
      show_dialog: 'true'
    });

    window.location = `https://accounts.spotify.com/authorize?${params.toString()}`;
  } catch (err) {
    showError(err.message);
  }
}

async function handleRedirectCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  if (!code) return;

  showLoading();

  const codeVerifier = sessionStorage.getItem('spotify_code_verifier');
  if (!codeVerifier) {
    showError('Missing code verifier in sessionStorage. Start auth again.');
    return;
  }


  try {
    const body = new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: REDIRECT_URI,
      client_id: CLIENT_ID,
      code_verifier: codeVerifier
    });

    const resp = await fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Token exchange failed: ${resp.status} ${text}`);
    }

    const data = await resp.json();
    data.expires_at = Date.now() + data.expires_in * 1000;
    sessionStorage.setItem('spotify_auth', JSON.stringify(data));
    window.history.replaceState({}, document.title, window.location.pathname);

    await loadUserData();
  } catch (err) {
    showError(err.message);
  }
}

function getStoredAuth() {
  const raw = sessionStorage.getItem('spotify_auth');
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

async function refreshAccessToken() {
  const auth = getStoredAuth();
  if (!auth || !auth.refresh_token) {
    throw new Error('No refresh token available. Please log in again.');
  }

  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: auth.refresh_token,
    client_id: CLIENT_ID
  });

  const resp = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Token refresh failed: ${resp.status} ${text}`);
  }

  const data = await resp.json();
  const newAuth = {
    ...auth,
    access_token: data.access_token,
    expires_in: data.expires_in,
    expires_at: Date.now() + data.expires_in * 1000,
    ...(data.refresh_token ? { refresh_token: data.refresh_token } : {})
  };
  sessionStorage.setItem('spotify_auth', JSON.stringify(newAuth));
  return newAuth;
}

async function apiGet(path) {
  let auth = getStoredAuth();
  if (!auth || !auth.access_token) throw new Error('Not authenticated');

  if (auth.expires_at && Date.now() > auth.expires_at - 60000) {
    try {
      auth = await refreshAccessToken();
    } catch {
      throw new Error('Access token expired and refresh failed. Please log in again.');
    }
  }

  let resp = await fetch(`https://api.spotify.com/v1${path}`, {
    headers: { Authorization: `Bearer ${auth.access_token}` }
  });

  if (resp.status === 401) {
    try {
      auth = await refreshAccessToken();
    } catch {
      throw new Error('Access token expired and refresh failed. Please log in again.');
    }

    resp = await fetch(`https://api.spotify.com/v1${path}`, {
      headers: { Authorization: `Bearer ${auth.access_token}` }
    });

    if (resp.status === 401) {
      throw new Error('Access token expired or invalid. Please log in again.');
    }
  }

  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`Spotify API error ${resp.status}: ${txt}`);
  }

  return await resp.json();
}

async function loadUserData() {
  try {
    showLoggedIn();
    hideLoading();

    const profile = await apiGet('/me');
    renderProfile(profile);

    // Store avatar URL for the header
    const placeholder = 'https://via.placeholder.com/44?text=U';
    const avatarUrl = (profile.images && profile.images[0] && profile.images[0].url) || placeholder;
    profileAvatar.src = avatarUrl;

    const top = await apiGet('/me/top/tracks?limit=10');
    renderTopTracks(top.items || []);

    const topArtists = await apiGet('/me/top/artists?limit=10');
    renderTopArtists(topArtists.items || []);

    profileModal.classList.add('hidden');
    listsContent.style.display = 'block';

  } catch (err) {
    showError(err.message);
  }
}

function renderProfile(user) {
  const placeholder = 'https://via.placeholder.com/110?text=User';
  const image = (user.images && user.images[0] && user.images[0].url) || placeholder;
  profileContainer.innerHTML = `
    <div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;">
      <img src="${image}" alt="${user.display_name || 'User'}" style="width:110px;height:110px;border-radius:50%;object-fit:cover;"/>
      <div style="text-align:center;color:#fff;font-weight:600;font-size:1.3rem;">${user.display_name || 'Spotify User'}</div>
      <div style="color:#cbd5e1;">${user.email || ''}</div>
      <div style="color:#94a3b8;margin-top:4px;">Followers: ${user.followers ? user.followers.total : 'N/A'}</div>
    </div>
  `;
}

function renderTopTracks(items) {
  if (!topTracksContainer) return;
  if (!items.length) {
    topTracksContainer.innerHTML = '<div style="color:#cbd5e1">No top tracks found.</div>';
    return;
  }

  topTracksContainer.innerHTML = items.map((t, i) => `
    <div class="track" style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
      <div style="width:48px;height:48px;flex:0 0 48px;"><img src="${t.album.images[2]?.url || t.album.images[0]?.url || ''}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;"/></div>
      <div style="flex:1;color:#e2e8f0;">
        <div style="font-weight:600">${i+1}. ${t.name}</div>
        <div style="color:#94a3b8">${t.artists.map(a => a.name).join(', ')}</div>
      </div>
      <div style="color:#94a3b8;font-size:0.9rem">${millisToMinutesAndSeconds(t.duration_ms)}</div>
    </div>
  `).join('');
}

function renderTopArtists(items) {
  if (!topArtistsContainer) return; 
  if (!items.length) {
    topArtistsContainer.innerHTML = '<div style="color:#cbd5e1">No top artists found.</div>';
    return;
  }

  topArtistsContainer.innerHTML = items.map((a, i) => `
    <div class="artist" style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
      <div style="width:48px;height:48px;flex:0 0 48px;"><img src="${a.images[2]?.url || a.images[0]?.url || ''}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;"/></div>
      <div style="flex:1;color:#e2e8f0;">
        <div style="font-weight:600">${i+1}. ${a.name}</div>
      </div>
    </div>
  `).join('');
}



function millisToMinutesAndSeconds(ms) {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function logout() {
  sessionStorage.removeItem('spotify_auth');
  sessionStorage.removeItem('spotify_code_verifier');
  showLoggedOut();
}

// Event listeners
loginBtn.addEventListener('click', login);
logoutBtn.addEventListener('click', logout);

// Modal: close popup and show lists
modalCloseBtn.addEventListener('click', () => {
  profileModal.classList.add('hidden');
  listsContent.style.display = 'block';
});

// Click on overlay backdrop to close
profileModal.addEventListener('click', (e) => {
  if (e.target === profileModal) {
    profileModal.classList.add('hidden');
    listsContent.style.display = 'block';
  }
});

// Click avatar to re-open profile popup
profileAvatar.addEventListener('click', () => {
  profileModal.classList.remove('hidden');
  listsContent.style.display = 'none';
});

// Init flow: check for code in URL, otherwise check stored auth
(async function init() {
  showLoading();
  try {
    await handleRedirectCallback();

    const auth = getStoredAuth();
    if (auth && auth.access_token) {
      await loadUserData();
    } else {
      hideLoading();
      showLoggedOut();
    }
  } catch (err) {
    showError(err.message);
  }
})();