import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../App';
import './Layout.css';

const CANDIDAT_NAV = [
  { id: 'dashboard', label: 'Tableau de bord', path: '/candidat', icon: '📊' },
  { id: 'profile', label: 'Mon profil', path: '/candidat/profile', icon: '👤' },
  { id: 'cv', label: 'Mes CVs', path: '/candidat/cv', icon: '📄' },
  { id: 'search', label: 'Rechercher offres', path: '/candidat/search', icon: '🔍' },
  { id: 'applications', label: 'Mes candidatures', path: '/candidat/applications', icon: '📋' },
];

const RECRUTEUR_NAV = [
  { id: 'dashboard', label: 'Tableau de bord', path: '/recruteur', icon: '📊' },
  { id: 'offers', label: 'Créer une offre', path: '/recruteur/offers', icon: '➕' },
  { id: 'list', label: 'Mes offres', path: '/recruteur/list', icon: '📋' },
  { id: 'candidatures', label: 'Candidatures', path: '/recruteur/candidatures', icon: '👥' },
  { id: 'matching', label: 'Matching IA', path: '/recruteur/matching', icon: '🎯' },
];

export default function Layout({ role, children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logoutUser } = useAuth();
  const nav = role === 'candidat' ? CANDIDAT_NAV : RECRUTEUR_NAV;

  const isActive = (path) => {
    if (path === '/candidat' || path === '/recruteur') return location.pathname === path;
    return location.pathname.startsWith(path);
  };

  return (
    <div className="app-container">
      <aside className="app-sidebar">
        <div className="app-sidebar__logo">
          <span>🎯</span>
          <span>AI Recruitment</span>
        </div>
        <nav className="app-sidebar__nav">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`app-sidebar__item ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="app-sidebar__footer">
          <p style={{ margin: 0 }}>{user?.email}</p>
          <p style={{ margin: '0.25rem 0 0 0', opacity: 0.8 }}>{role === 'candidat' ? 'Candidat' : 'Recruteur'}</p>
          <button
            type="button"
            className="btn btn-ghost"
            style={{ marginTop: '0.5rem', width: '100%', justifyContent: 'flex-start', fontSize: '0.8125rem' }}
            onClick={() => { logoutUser(); navigate('/login'); }}
          >
            Déconnexion
          </button>
        </div>
      </aside>
      <main className="app-main">
        <header className="app-header">
          <h1 className="app-header__title" style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600 }}>
            {nav.find((i) => isActive(i.path))?.label || 'Tableau de bord'}
          </h1>
        </header>
        <div className="app-content">
          {children}
        </div>
      </main>
    </div>
  );
}
