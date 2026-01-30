import { useNavigate } from 'react-router-dom';

export default function RecruteurDashboard() {
  const navigate = useNavigate();
  const cards = [
    { id: 'offers', icon: '➕', title: 'Créer une offre', desc: 'Publier une nouvelle offre d\'emploi', path: '/recruteur/offers', iconClass: 'blue' },
    { id: 'list', icon: '📋', title: 'Mes offres', desc: 'Gérer vos offres publiées', path: '/recruteur/list', iconClass: 'green' },
    { id: 'candidatures', icon: '👥', title: 'Candidatures', desc: 'Voir les candidatures reçues', path: '/recruteur/candidatures', iconClass: 'amber' },
    { id: 'matching', icon: '🎯', title: 'Matching IA', desc: 'Trouver les meilleurs candidats pour une offre', path: '/recruteur/matching', iconClass: 'slate' },
  ];

  return (
    <div>
      <h1 className="app-page-title">Tableau de bord recruteur</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        Gérez vos offres, consultez les candidatures et utilisez le matching IA pour shortlister les candidats.
      </p>
      <div className="dashboard-grid">
        {cards.map((c) => (
          <div
            key={c.id}
            className="dashboard-card"
            role="button"
            tabIndex={0}
            onClick={() => navigate(c.path)}
            onKeyDown={(e) => e.key === 'Enter' && navigate(c.path)}
          >
            <div className={`dashboard-card__icon ${c.iconClass}`}>{c.icon}</div>
            <h3 className="dashboard-card__title">{c.title}</h3>
            <p className="dashboard-card__desc">{c.desc}</p>
            <span className="btn btn-secondary" style={{ fontSize: '0.875rem' }}>Accéder →</span>
          </div>
        ))}
      </div>
    </div>
  );
}
