import { useState, useEffect } from 'react';
import { getJobOffers } from '../../services/matchingService';
import { getCandidaturesForOffre } from '../../services/offresService';
import './CandidaturesRecruteur.css';

export default function CandidaturesRecruteur() {
  const [offres, setOffres] = useState([]);
  const [selectedOffreId, setSelectedOffreId] = useState('');
  const [candidatures, setCandidatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getOffresRecruteur(1, 100)
      .then(({ data }) => {
        setOffres(data);
        if (data.length) setSelectedOffreId(data[0].id);
      })
      .catch(() => setError('Erreur chargement des offres'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedOffreId) return;
    setLoading(true);
    getCandidaturesForOffre(selectedOffreId)
      .then(({ data }) => setCandidatures(data))
      .catch(() => setCandidatures([]))
      .finally(() => setLoading(false));
  }, [selectedOffreId]);

  const statutLabel = (s) => {
    switch (s) {
      case 'pending': return 'En attente';
      case 'accepted': return 'Acceptée';
      case 'rejected': return 'Refusée';
      default: return s;
    }
  };

  if (offres.length === 0 && !loading) {
    return (
      <div>
        <h1 className="app-page-title">Candidatures</h1>
        <div className="card">
          <p className="empty-state">Aucune offre. Créez une offre pour recevoir des candidatures.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="app-page-title">Candidatures</h1>
      <div className="form-group" style={{ marginBottom: '1rem' }}>
        <label className="form-label">Offre</label>
        <select
          className="form-input"
          value={selectedOffreId}
          onChange={(e) => setSelectedOffreId(e.target.value)}
          style={{ maxWidth: '400px' }}
        >
          {offres.map((o) => (
            <option key={o.id} value={o.id}>{o.titre}</option>
          ))}
        </select>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <div className="loading-spinner" />
      ) : candidatures.length === 0 ? (
        <div className="card">
          <p className="empty-state">Aucune candidature pour cette offre.</p>
        </div>
      ) : (
        <div className="candidatures-recruteur-list">
          {candidatures.map((c) => (
            <div key={c.id} className="card candidature-recruteur-card">
              <div className="candidature-recruteur-card__header">
                <span className="candidature-recruteur-card__statut" data-statut={c.statut}>
                  {statutLabel(c.statut)}
                </span>
                <span className="candidature-recruteur-card__score">
                  {c.score_matching != null ? `Score : ${c.score_matching}%` : '—'}
                </span>
              </div>
              <p className="candidature-recruteur-card__meta">Candidat ID : {c.candidat_id}</p>
              {c.explication && <p className="candidature-recruteur-card__explication">{c.explication}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
