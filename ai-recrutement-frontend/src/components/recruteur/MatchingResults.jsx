import { useState, useEffect } from 'react';
import { getJobOffers } from '../../services/matchingService';
import { getMeilleursCandidats } from '../../services/offresService';
import './MatchingResults.css';

export default function MatchingResults() {
  const [offres, setOffres] = useState([]);
  const [selectedOffreId, setSelectedOffreId] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getOffresRecruteur(1, 100)
      .then(({ data }) => {
        setOffres(data);
        if (data.length) setSelectedOffreId(data[0].id);
      })
      .catch(() => setError('Erreur chargement des offres'));
  }, []);

  const handleSearch = async () => {
    if (!selectedOffreId) return;
    setLoading(true);
    setError('');
    setResults(null);
    try {
      const data = await getMeilleursCandidats(selectedOffreId, 10);
      setResults(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du matching');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Matching IA</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        Sélectionnez une offre pour afficher les meilleurs candidats selon le score de matching.
      </p>
      <div className="card" style={{ marginBottom: '1.5rem', maxWidth: '480px' }}>
        <div className="form-group">
          <label className="form-label">Offre</label>
          <select
            className="form-input"
            value={selectedOffreId}
            onChange={(e) => setSelectedOffreId(e.target.value)}
          >
            {offres.map((o) => (
              <option key={o.id} value={o.id}>{o.titre}</option>
            ))}
          </select>
        </div>
        <button type="button" className="btn btn-primary" onClick={handleSearch} disabled={loading}>
          {loading ? 'Recherche...' : 'Voir les meilleurs candidats'}
        </button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {results && (
        <div className="card matching-results-card">
          <h2 className="card-title">Résultats ({results.total_results ?? results.matches?.length ?? 0} candidats)</h2>
          {results.matches?.length === 0 ? (
            <p className="empty-state">Aucun candidat indexé pour le moment.</p>
          ) : (
            <ul className="matching-results-list">
              {(results.matches || []).map((m, i) => (
                <li key={i} className="matching-result-item">
                  <span className="matching-result-item__score">{m.score_final}%</span>
                  <span className="matching-result-item__reco">{m.recommandation}</span>
                  {m.explications?.pour_recruteur?.synthese && (
                    <p className="matching-result-item__synthese">{m.explications.pour_recruteur.synthese}</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
