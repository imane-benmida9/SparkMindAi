import { useState, useEffect } from 'react';
import { getJobOffers, getCandidateCVs, applyToOffer, getMatchingScore } from '../../services/matchingService';
import './JobSearch.css';

export default function JobSearch() {
  const [jobs, setJobs] = useState([]);
  const [cvs, setCvs] = useState([]);
  const [selectedCvId, setSelectedCvId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [matchingResult, setMatchingResult] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ statut: 'ouverte' });

  useEffect(() => {
    getCandidateCVs()
      .then(({ data }) => {
        setCvs(data);
        if (data.length) setSelectedCvId(data[0].id);
      })
      .catch(() => setError('Erreur chargement CVs'));
  }, []);

  useEffect(() => {
    setLoading(true);
    getJobOffers(page, 10, filters)
      .then(({ data }) => setJobs(data))
      .catch(() => setError('Erreur chargement offres'))
      .finally(() => setLoading(false));
  }, [page, filters]);

  const handleMatch = async (job) => {
    if (!selectedCvId) {
      setError('Veuillez sélectionner un CV');
      return;
    }
    setLoading(true);
    setError('');
    setMatchingResult(null);
    setSelectedJob(job);
    try {
      const cv = cvs.find((c) => c.id === selectedCvId);
      const result = await getMatchingScore(cv.id, job.id, true);
      setMatchingResult(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du matching');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (job) => {
    if (!selectedCvId) {
      setError('Veuillez sélectionner un CV');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await applyToOffer(job.id, selectedCvId);
      setMatchingResult(null);
      setSelectedJob(null);
      setError('');
      alert('Candidature envoyée.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la candidature');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Rechercher des offres</h1>
      {cvs.length === 0 && (
        <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
          Uploadez au moins un CV dans « Mes CVs » pour postuler et voir votre score de matching.
        </div>
      )}
      {cvs.length > 0 && (
        <div className="form-group" style={{ marginBottom: '1rem' }}>
          <label className="form-label">CV utilisé pour postuler</label>
          <select
            className="form-input"
            value={selectedCvId}
            onChange={(e) => setSelectedCvId(e.target.value)}
            style={{ maxWidth: '320px' }}
          >
            {cvs.map((cv) => (
              <option key={cv.id} value={cv.id}>{cv.nom_fichier}</option>
            ))}
          </select>
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}
      {loading && !matchingResult && <div className="loading-spinner" />}
      {!loading && (
        <div className="job-list">
          {jobs.map((job) => (
            <div key={job.id} className="card job-card">
              <div className="job-card__header">
                <h3 className="job-card__title">{job.titre}</h3>
                {job.localisation && <span className="job-card__location">{job.localisation}</span>}
              </div>
              <p className="job-card__desc">{job.description?.slice(0, 200)}…</p>
              <div className="job-card__meta">
                {job.type_contrat && <span>{job.type_contrat}</span>}
                {job.experience_requise != null && <span>Exp. {job.experience_requise} an(s)</span>}
              </div>
              <div className="job-card__actions">
                <button type="button" className="btn btn-secondary" onClick={() => handleMatch(job)} disabled={!selectedCvId}>
                  Voir le score matching
                </button>
                <button type="button" className="btn btn-primary" onClick={() => handleApply(job)} disabled={!selectedCvId}>
                  Postuler
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {matchingResult && selectedJob && (
        <div className="card matching-result-card">
          <h3 className="card-title">Score de matching : {selectedJob.titre}</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            {matchingResult.score_final}%
          </p>
          <p style={{ margin: '0.5rem 0', color: 'var(--color-text-muted)' }}>
            Recommandation : {matchingResult.recommandation}
          </p>
          {matchingResult.explications?.pour_candidat?.message_principal && (
            <p style={{ marginTop: '1rem', fontSize: '0.9375rem' }}>
              {matchingResult.explications.pour_candidat.message_principal}
            </p>
          )}
          <button type="button" className="btn btn-ghost" onClick={() => { setMatchingResult(null); setSelectedJob(null); }}>
            Fermer
          </button>
        </div>
      )}
    </div>
  );
}
