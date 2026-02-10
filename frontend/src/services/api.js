import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const predictNews = async (text) => {
    const response = await api.post('/predict', { text });
    return response.data;
};

export default api;
