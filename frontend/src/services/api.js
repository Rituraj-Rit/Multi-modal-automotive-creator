import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error.response?.data || error);
  }
);

// API Functions

// Health Check
export const healthCheck = async () => {
  return api.get('/health');
};

// Generate Narrative
export const generateNarrative = async (prompt, context = null) => {
  return api.post('/narrative', { prompt, context });
};

// Generate Image
export const generateImage = async (prompt, options = {}) => {
  const {
    size = '1024x1024',
    quality = 'standard',
    style = 'vivid',
    enhance_prompt = true,
  } = options;
  return api.post('/image', {
    prompt,
    size,
    quality,
    style,
    enhance_prompt,
  });
};

// Generate Both (Narrative + Image)
export const generateBoth = async (prompt, options = {}) => {
  const {
    context = null,
    image_size = '1024x1024',
    image_quality = 'standard',
    image_style = 'vivid',
    save_to_history = true,
  } = options;
  return api.post('/generate', {
    prompt,
    context,
    image_size,
    image_quality,
    image_style,
    save_to_history,
  });
};

// Chat
export const chat = async (messages, context = null) => {
  return api.post('/chat', { messages, context });
};

// Enhance Prompt
export const enhancePrompt = async (prompt) => {
  return api.post('/prompt/enhance', { prompt });
};

// Get History
export const getHistory = async (limit = 20) => {
  return api.get(`/history?limit=${limit}`);
};

// Search Similar
export const searchSimilar = async (query, n_results = 5) => {
  return api.post('/search', { query, n_results });
};

// Delete History Item
export const deleteHistoryItem = async (recordId) => {
  return api.delete(`/history/${recordId}`);
};

export default api;
