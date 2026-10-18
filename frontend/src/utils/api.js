import axios from 'axios';

const api = axios.create({ baseURL: '' });

export const predictCrop = (data) => api.post('/predict', data).then((r) => r.data);
export const getModelInfo = () => api.get('/model-info').then((r) => r.data);
export const getDefaults = (country) =>
  api.post('/get_defaults', { country }).then((r) => r.data);
export const healthCheck = () => api.get('/health').then((r) => r.data);
