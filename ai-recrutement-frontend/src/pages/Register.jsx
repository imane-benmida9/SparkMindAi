import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { register, login, getMe, setTokens } from '../services/authService';
import './Auth.css';

export default function Register() {
  const navigate = useNavigate();
  const { loginSuccess } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nom, setNom] = useState('');
  const [role, setRole] = useState('candidat');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password, role, nom || undefined);
      const tokenData = await login(email, password);
      // Sauvegarder les tokens AVANT d'appeler getMe()
      setTokens(tokenData.access_token, tokenData.refresh_token);
      const userData = await getMe();
      loginSuccess(tokenData, userData);
      navigate(userData.role === 'candidat' ? '/candidat' : '/recruteur');
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="auth-card__logo">🎯 SparkMindAI</div>
        <h1 className="auth-card__title">Inscription</h1>
        <p className="auth-card__subtitle">Créez votre compte candidat ou recruteur</p>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.com"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Mot de passe (min. 6 caractères)</label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="nom">Nom ou entreprise (optionnel)</label>
            <input
              id="nom"
              type="text"
              className="form-input"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              placeholder={role === 'recruteur' ? 'Nom de l\'entreprise' : 'Votre nom'}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Profil</label>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.25rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input type="radio" name="role" value="candidat" checked={role === 'candidat'} onChange={() => setRole('candidat')} />
                Candidat
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input type="radio" name="role" value="recruteur" checked={role === 'recruteur'} onChange={() => setRole('recruteur')} />
                Recruteur
              </label>
            </div>
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={loading}>
            {loading ? 'Inscription...' : "S'inscrire"}
          </button>
        </form>
        <p className="auth-card__footer">
          Déjà inscrit ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
