import api from './api';

export const createOffre = async (body) => {
  const { data } = await api.post('/offres', body);
  return data;
};

export const getOffresRecruteur = async (page = 1, limit = 50) => {
  const { data } = await api.get('/offres', { params: { page, limit, mine: true } });
  return { data: Array.isArray(data) ? data : [] };
};

export const getCandidaturesForOffre = async (offreId) => {
  const { data } = await api.get('/candidatures', { params: { offre_id: offreId } });
  return { data: Array.isArray(data) ? data : [] };
};

export const getMeilleursCandidats = async (offreId, topK = 10) => {
  const { data } = await api.post(`/matching/search-candidats/${offreId}`, null, {
    params: { top_k: topK, generer_explications: true },
  });
  return data;
};
