import apiClient from './axiosConfig';

export const ragApi = {
  // --- SEND CHAT MESSAGE ---
  sendMessage: async ({sessionId, message, documentHash = null}) => {
    const payload = {
      content: message,
      session_id: sessionId,
    };

    // create optional ?hash=...
    const params = documentHash ? `?hash=${documentHash}` : '';

    const response = await apiClient.post(`/rag/chat${params}`, payload);
    return response.data;
  },

  // --- UPLOAD DOCUMENT ---
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/rag/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },

  // --- LIST CHAT SESSIONS ---
  getChatSessions: async () => {
    const response = await apiClient.get('/rag/sessions/');
    return response.data;
  },

  // --- GET CHAT SESSION BY ID ---
  getChatSessionById: async (sessionId) => {
    const response = await apiClient.get(`/rag/sessions/${sessionId}`);
    return response.data;
  },
};
