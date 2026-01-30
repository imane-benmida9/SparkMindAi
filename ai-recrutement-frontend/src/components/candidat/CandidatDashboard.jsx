import { useNavigate } from 'react-router-dom';
import './CandidatDashboard.css';

export default function CandidatDashboard() {
  const navigate = useNavigate();
  const cards = [
    { id: 'cv', icon: '📄', title: 'Mes CVs', desc: 'Gérez vos CVs et profilez votre candidature', path: '/candidat/cv', iconClass: 'blue' },
    { id: 'search', icon: '🔍', title: "Offres d'emploi", desc: "Trouvez les offres correspondant à votre profil", path: '/candidat/search', iconClass: 'green' },
    { id: 'applications', icon: '📋', title: 'Mes candidatures', desc: "Suivez l'état de vos candidatures", path: '/candidat/applications', iconClass: 'amber' },
    { id: 'profile', icon: '👤', title: 'Mon profil', desc: 'Mettez à jour vos informations personnelles', path: '/candidat/profile', iconClass: 'slate' },
  ];

  return (
    <div>
      <h1 className="app-page-title">Tableau de bord</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        Bienvenue sur votre espace candidat. Accédez rapidement à vos CVs, offres et candidatures.
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
      <div className="card" style={{ marginTop: '1.5rem', padding: '1rem 1.25rem' }}>
        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>💡 Conseil</h3>
        <p style={{ margin: 0, fontSize: '0.9375rem', color: 'var(--color-text-muted)' }}>
          Assurez-vous que votre profil est complet et que vous avez uploadé au moins un CV pour bénéficier du meilleur matching avec les offres.
        </p>
      </div>
    </div>
  );
}
