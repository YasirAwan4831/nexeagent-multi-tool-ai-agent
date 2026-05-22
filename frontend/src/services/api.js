const API_BASE = import.meta.env.VITE_API_URL || '';

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
  } catch {
    throw new Error(
      'Cannot reach the API. Start the backend: cd backend && python app.py'
    );
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || data.message || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  health: () => request('/api/health'),

  sendMessage: (message, sessionId = 'default') =>
    request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    }),

  getChatHistory: (sessionId = 'default') =>
    request(`/api/chat/history?session_id=${sessionId}`),

  searchJobs: (query, limit = 20) =>
    request('/api/jobs/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    }),

  getSavedJobs: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/jobs/saved${qs ? `?${qs}` : ''}`);
  },

  getNotes: (tag) =>
    request(`/api/notes${tag ? `?tag=${encodeURIComponent(tag)}` : ''}`),

  createNote: (note) =>
    request('/api/notes', { method: 'POST', body: JSON.stringify(note) }),

  updateNote: (id, note) =>
    request(`/api/notes/${id}`, { method: 'PUT', body: JSON.stringify(note) }),

  deleteNote: (id) =>
    request(`/api/notes/${id}`, { method: 'DELETE' }),

  sendEmail: (payload) =>
    request('/api/email/send', { method: 'POST', body: JSON.stringify(payload) }),

  emailStatus: () => request('/api/email/status'),

  runTool: (name, payload) =>
    request(`/api/tools/${name}`, { method: 'POST', body: JSON.stringify(payload) }),
};

export default api;
