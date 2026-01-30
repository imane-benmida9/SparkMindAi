import { useState, useEffect } from 'react';
import api from '../../services/api';
import './ProfileForm.css';

export default function ProfileForm() {
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [localisation, setLocalisation] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/candidats/me')
      .then(({ data }) => {
        setNom(data.nom || '');
        setTelephone(data.telephone || '');
        setLocalisation(data.localisation || '');
      })
      .catch(() => setError('Impossible de charger le profil'));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);
    try {
      await api.patch('/candidats/me', { nom, telephone, localisation });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la mise à jour');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Mon profil</h1>
      <div className="card" style={{ maxWidth: '480px' }}>
        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">Profil mis à jour.</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="nom">Nom</label>
            <input
              id="nom"
              type="text"
              className="form-input"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              placeholder="Votre nom"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="telephone">Téléphone</label>
            <input
              id="telephone"
              type="tel"
              className="form-input"
              value={telephone}
              onChange={(e) => setTelephone(e.target.value)}
              placeholder="06 12 34 56 78"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="localisation">Localisation</label>
            <input
              id="localisation"
              type="text"
              className="form-input"
              value={localisation}
              onChange={(e) => setLocalisation(e.target.value)}
              placeholder="Ville ou région"
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Enregistrement...' : 'Enregistrer'}
          </button>
        </form>
      </div>
    </div>
  );
}
