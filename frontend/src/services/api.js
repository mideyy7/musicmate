const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong');
  }

  return data;
}

export function ssoInitiate(email) {
  return request('/auth/sso/initiate', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export function ssoComplete(userData) {
  return request('/auth/sso/complete', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export function getMe() {
  return request('/auth/me');
}

export function updateProfile(updates) {
  return request('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

// Spotify
export function getSpotifyAuthUrl() {
  return request('/spotify/auth-url');
}

export function spotifyCallback(code) {
  return request('/spotify/callback', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export function getSpotifyStatus() {
  return request('/spotify/status');
}

export function syncSpotifyProfile() {
  return request('/spotify/sync', { method: 'POST' });
}

export function getMusicProfile() {
  return request('/spotify/profile');
}

export function disconnectSpotify() {
  return request('/spotify/disconnect', { method: 'DELETE' });
}

// Match
export function getMatchFeed(filters = {}) {
  const params = new URLSearchParams();
  if (filters.course) params.set('course', filters.course);
  if (filters.year) params.set('year', filters.year);
  if (filters.faculty) params.set('faculty', filters.faculty);
  const qs = params.toString();
  return request(`/match/feed${qs ? `?${qs}` : ''}`);
}

export function swipe(targetUserId, action) {
  return request('/match/swipe', {
    method: 'POST',
    body: JSON.stringify({ target_user_id: targetUserId, action }),
  });
}

export function getMatches() {
  return request('/match/matches');
}
