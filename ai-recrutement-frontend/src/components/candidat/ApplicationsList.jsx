import { useState, useEffect } from 'react';
import { getMyCandidatures } from '../../services/matchingService';
import './ApplicationsList.css';

export default function ApplicationsList() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getMyCandidatures()
      .then(({ data }) => setList(data))
      .catch(() => setError('Erreur lors du chargement des candidatures'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-spinner" />;
  if (error) return <div className="alert alert-error">{error}</div>;

  const statutLabel = (s) => {
    switch (s) {
      case 'pending': return 'En attente';
      case 'accepted': return 'Acceptée';
      case 'rejected': return 'Refusée';
      default: return s;
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Mes candidatures</h1>
      {list.length === 0 ? (
        <div className="card">
          <p className="empty-state">Vous n'avez pas encore de candidature. Recherchez des offres et postulez.</p>
        </div>
      ) : (
        <div className="applications-list">
          {list.map((c) => (
            <div key={c.id} className="card application-card">
              <div className="application-card__header">
                <span className="application-card__statut" data-statut={c.statut}>
                  {statutLabel(c.statut)}
                </span>
                <span className="application-card__date">
                  {c.date_candidature ? new Date(c.date_candidature).toLocaleDateString() : ''}
                </span>
              </div>
              <p className="application-card__meta">
                Offre ID : {c.offre_id} • Score : {c.score_matching != null ? `${c.score_matching}%` : '—'}
              </p>
              {c.explication && (
                <p className="application-card__explication">{c.explication}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
