import { Link } from 'react-router-dom';
import { useAuth } from '../App';
import './Home.css';

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="home-page">
        <div className="loading-spinner" />
      </div>
    );
  }

  if (user) {
    return (
      <div className="home-page">
        <div className="home-hero card">
          <h1>Bienvenue, {user.email}</h1>
          <p>Accédez à votre espace.</p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <Link to={user.role === 'candidat' ? '/candidat' : '/recruteur'} className="btn btn-primary">
              Aller au tableau de bord
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <div className="home-hero">
        <h1 className="home-hero__title">🎯 SparkMindAI</h1>
        <p className="home-hero__subtitle">
          Plateforme de recrutement intelligente : matching CV–offres par IA, analyse de CV et recommandations.
        </p>
        <div className="home-hero__actions">
          <Link to="/login" className="btn btn-primary">Se connecter</Link>
          <Link to="/register" className="btn btn-secondary">S'inscrire</Link>
        </div>
      </div>
      <div className="home-features">
        <div className="card home-feature">
          <div className="dashboard-card__icon blue">📄</div>
          <h3>CV analysés par IA</h3>
          <p>Uploadez votre CV PDF, extraction automatique des compétences et expériences.</p>
        </div>
        <div className="card home-feature">
          <div className="dashboard-card__icon green">🎯</div>
          <h3>Matching intelligent</h3>
          <p>Score de compatibilité et explications pour candidats et recruteurs.</p>
        </div>
        <div className="card home-feature">
          <div className="dashboard-card__icon amber">🔍</div>
          <h3>Recherche sémantique</h3>
          <p>Retrouvez les offres ou candidats les plus pertinents grâce aux embeddings.</p>
        </div>
      </div>
    </div>
  );
}
