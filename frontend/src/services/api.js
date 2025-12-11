// frontend/src/api/api.js
const API_URL = "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || 'Something went wrong');
  }
  return response.json();
}

export function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
}

// Auth endpoints
export async function register(email, name, password) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, username: email, full_name: name, password: password }),
  });
  return await handleResponse(res);
}

export async function login(email, password) {
  const formData = new FormData();
  formData.append('username', email); // API expects 'username' field
  formData.append('password', password);

  const res = await fetch(`${API_URL}/auth/token`, {
    method: 'POST',
    body: formData,
  });
  return await handleResponse(res);
}

// Chat endpoints
export async function startSession(userId, query) {
  // note: userId param might be deprecated in backend but keeping signature if needed, 
  // though backend now uses token. We'll rely on token.
  const res = await fetch(`${API_URL}/chat/session/start`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ query })
  });
  return await handleResponse(res);
}

export async function sendMessage(sessionId, userId, query) {
  const res = await fetch(`${API_URL}/chat/session/${sessionId}/message`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ query })
  });
  return await handleResponse(res);
}

export async function getSessions(userId) {
  const res = await fetch(`${API_URL}/chat/sessions`, {
    headers: getAuthHeaders()
  });
  return await handleResponse(res);
}

export async function getSessionMessages(userId, sessionId) {
  const res = await fetch(`${API_URL}/chat/sessions/${sessionId}/messages`, {
    headers: getAuthHeaders()
  });
  return await handleResponse(res);
}
