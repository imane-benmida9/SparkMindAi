import { useState } from 'react';
import { createOffre } from '../../services/offresService';
import './JobOfferForm.css';

export default function JobOfferForm() {
  const [titre, setTitre] = useState('');
  const [description, setDescription] = useState('');
  const [localisation, setLocalisation] = useState('');
  const [typeContrat, setTypeContrat] = useState('CDI');
  const [salaireMin, setSalaireMin] = useState('');
  const [salaireMax, setSalaireMax] = useState('');
  const [experienceRequise, setExperienceRequise] = useState('');
  const [competences, setCompetences] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);
    try {
      await createOffre({
        titre,
        description,
        localisation: localisation || undefined,
        type_contrat: typeContrat,
        salaire_min: salaireMin ? Number(salaireMin) : undefined,
        salaire_max: salaireMax ? Number(salaireMax) : undefined,
        experience_requise: experienceRequise ? parseInt(experienceRequise, 10) : undefined,
        competences_requises: competences ? competences.split(',').map((s) => s.trim()).filter(Boolean) : undefined,
      });
      setSuccess(true);
      setTitre('');
      setDescription('');
      setLocalisation('');
      setSalaireMin('');
      setSalaireMax('');
      setExperienceRequise('');
      setCompetences('');
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la création de l\'offre');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Créer une offre</h1>
      <div className="card" style={{ maxWidth: '560px' }}>
        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">Offre créée avec succès.</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="titre">Titre *</label>
            <input
              id="titre"
              type="text"
              className="form-input"
              value={titre}
              onChange={(e) => setTitre(e.target.value)}
              placeholder="Ex. Développeur Full Stack"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="description">Description *</label>
            <textarea
              id="description"
              className="form-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Décrivez le poste, les missions..."
              rows={4}
              required
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
              placeholder="Paris, télétravail..."
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="type_contrat">Type de contrat</label>
            <select
              id="type_contrat"
              className="form-input"
              value={typeContrat}
              onChange={(e) => setTypeContrat(e.target.value)}
            >
              <option value="CDI">CDI</option>
              <option value="CDD">CDD</option>
              <option value="Stage">Stage</option>
              <option value="Freelance">Freelance</option>
            </select>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="salaire_min">Salaire min (€)</label>
              <input
                id="salaire_min"
                type="number"
                className="form-input"
                value={salaireMin}
                onChange={(e) => setSalaireMin(e.target.value)}
                placeholder="35000"
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="salaire_max">Salaire max (€)</label>
              <input
                id="salaire_max"
                type="number"
                className="form-input"
                value={salaireMax}
                onChange={(e) => setSalaireMax(e.target.value)}
                placeholder="45000"
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="experience">Années d'expérience requises</label>
            <input
              id="experience"
              type="number"
              min="0"
              className="form-input"
              value={experienceRequise}
              onChange={(e) => setExperienceRequise(e.target.value)}
              placeholder="3"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="competences">Compétences requises (séparées par des virgules)</label>
            <input
              id="competences"
              type="text"
              className="form-input"
              value={competences}
              onChange={(e) => setCompetences(e.target.value)}
              placeholder="React, Node.js, PostgreSQL"
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Création...' : 'Publier l\'offre'}
          </button>
        </form>
      </div>
    </div>
  );
}
