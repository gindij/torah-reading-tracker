const API_BASE_URL = 'http://localhost:5001/api';

export const api = {
  async getParshiot() {
    const response = await fetch(`${API_BASE_URL}/parshiot`);
    if (!response.ok) throw new Error('Failed to fetch parshiot');
    return response.json();
  },

  async getParsha(title) {
    const response = await fetch(`${API_BASE_URL}/parshiot/${encodeURIComponent(title)}`);
    if (!response.ok) throw new Error('Failed to fetch parsha');
    return response.json();
  },

  async updateAliyahStatus(parshaTitle, aliyahNumber, isComplete) {
    const response = await fetch(
      `${API_BASE_URL}/parshiot/${encodeURIComponent(parshaTitle)}/aliyot/${aliyahNumber}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_complete: isComplete })
      }
    );
    if (!response.ok) throw new Error('Failed to update aliyah status');
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  }
};
