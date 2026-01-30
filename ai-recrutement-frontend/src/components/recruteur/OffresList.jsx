import { useState, useEffect } from 'react';
import { getJobOffers } from '../../services/matchingService';
import './OffresList.css';

export default function OffresList() {
  const [offres, setOffres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getOffresRecruteur(1, 50)
      .then(({ data }) => setOffres(data))
      .catch(() => setError('Erreur chargement des offres'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-spinner" />;
  if (error) return <div className="alert alert-error">{error}</div>;

  return (
    <div>
      <h1 className="app-page-title">Mes offres</h1>
      {offres.length === 0 ? (
        <div className="card">
          <p className="empty-state">Aucune offre pour le moment. Créez une offre dans « Créer une offre ».</p>
        </div>
      ) : (
        <div className="offres-list">
          {offres.map((o) => (
            <div key={o.id} className="card offre-card">
              <h3 className="offre-card__title">{o.titre}</h3>
              <p className="offre-card__desc">{o.description?.slice(0, 180)}…</p>
              <div className="offre-card__meta">
                {o.localisation && <span>{o.localisation}</span>}
                {o.type_contrat && <span>{o.type_contrat}</span>}
                {o.experience_requise != null && <span>Exp. {o.experience_requise} an(s)</span>}
              </div>
              <span className="offre-card__statut" data-statut={o.statut}>{o.statut === 'ouverte' ? 'Ouverte' : 'Fermée'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
