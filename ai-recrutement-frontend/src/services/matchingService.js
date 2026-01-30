import api from './api';

export const getJobOffers = async (page = 1, limit = 10, filters = {}) => {
  const { data } = await api.get('/offres', {
    params: { page, limit, ...filters },
  });
  return { data: Array.isArray(data) ? data : [] };
};

/** Offres du recruteur connecté uniquement (mine=true) */
export const getMyJobOffers = async (page = 1, limit = 50) => {
  const { data } = await api.get('/offres', {
    params: { page, limit, mine: true },
  });
  return { data: Array.isArray(data) ? data : [] };
};

export const getJobOfferDetail = async (offerId) => {
  const { data } = await api.get(`/offres/${offerId}`);
  return { data };
};

export const getRecommendedOffers = async (cvJson, topK = 10) => {
  const { data } = await api.post('/cvs/search-offres', {
    cv_json: cvJson,
    top_k: topK,
  });
  return { data };
};

export const matchCandidateToOffer = async (candidate, job) => {
  const { data } = await api.post('/matching/match', { candidate, job });
  return data;
};

export const getMatchingScore = async (cvId, offerId, genererExplications = true) => {
  const { data } = await api.post('/matching/score', {
    cv_id: cvId,
    offre_id: offerId,
    generer_explications: genererExplications,
  });
  return data;
};

export const searchOffresForCV = async (cvId, topK = 10) => {
  const { data } = await api.post('/matching/search-offres', {
    cv_id: cvId,
    top_k: topK,
    generer_explications: false,
  });
  return data;
};

export const getCandidateCVs = async () => {
  const { data } = await api.get('/cvs/my-cvs');
  return { data: Array.isArray(data) ? data : [] };
};

export const applyToOffer = async (offreId, cvId) => {
  const { data } = await api.post('/candidatures', { offre_id: offreId, cv_id: cvId });
  return data;
};

export const getMyCandidatures = async () => {
  const { data } = await api.get('/candidatures');
  return { data: Array.isArray(data) ? data : [] };
};

export const getCandidatureDetail = async (candidatureId) => {
  const { data } = await api.get(`/candidatures/${candidatureId}`);
  return { data };
};
