import api from './api';

export const uploadCV = async (file, metadata = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  if (Object.keys(metadata).length) {
    formData.append('metadata', JSON.stringify(metadata));
  }
  const { data } = await api.post('/cvs/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return { data };
};

export const indexCV = async (cvId, cvJson, metadata = {}) => {
  await api.post('/cvs/index', { cv_id: cvId, cv_json: cvJson, metadata });
};

export const getMyCVs = async () => {
  const { data } = await api.get('/cvs/my-cvs');
  return { data: Array.isArray(data) ? data : [] };
};

export const getCV = async (cvId) => {
  const { data } = await api.get(`/cvs/${cvId}`);
  return { data };
};

export const deleteCV = async (cvId) => {
  await api.delete(`/cvs/${cvId}`);
};
