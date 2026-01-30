import { useState, useEffect } from 'react';
import { uploadCV, getMyCVs, deleteCV } from '../../services/cvService';
import './CVUploader.css';

export default function CVUploader() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [cvList, setCvList] = useState([]);

  const fetchCVs = async () => {
    try {
      const { data } = await getMyCVs();
      setCvList(data);
    } catch (err) {
      setError('Erreur lors du chargement des CVs');
    }
  };

  useEffect(() => {
    fetchCVs();
  }, []);

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      if (f.type !== 'application/pdf') {
        setError('Veuillez sélectionner un fichier PDF');
        return;
      }
      if (f.size > 10 * 1024 * 1024) {
        setError('Le fichier doit faire moins de 10 Mo');
        return;
      }
      setFile(f);
      setError('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }
    setLoading(true);
    setSuccess(false);
    setError('');
    try {
      await uploadCV(file, { upload_date: new Date().toISOString() });
      setSuccess(true);
      setFile(null);
      e.target.reset();
      fetchCVs();
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'upload du CV');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (cvId) => {
    if (!window.confirm('Supprimer ce CV ?')) return;
    try {
      await deleteCV(cvId);
      fetchCVs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  return (
    <div>
      <h1 className="app-page-title">Mes CVs</h1>
      <div className="card cv-uploader-card">
        <h2 className="card-title">Déposer un CV (PDF)</h2>
        <form onSubmit={handleUpload} className="cv-upload-form">
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">CV uploadé et analysé avec succès.</div>}
          <div className="form-group">
            <input
              id="cvInput"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="form-input"
              style={{ padding: '0.5rem' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading || !file}>
            {loading ? 'Upload en cours...' : 'Uploader et analyser'}
          </button>
        </form>
      </div>
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title">Vos CVs</h2>
        {cvList.length === 0 ? (
          <p className="empty-state">Aucun CV pour le moment. Uploadez un PDF ci-dessus.</p>
        ) : (
          <ul className="cv-list">
            {cvList.map((cv) => (
              <li key={cv.id} className="cv-list-item">
                <div>
                  <strong>{cv.nom_fichier}</strong>
                  <span style={{ marginLeft: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                    {cv.date_upload ? new Date(cv.date_upload).toLocaleDateString() : ''}
                  </span>
                </div>
                <button type="button" className="btn btn-ghost" onClick={() => handleDelete(cv.id)} style={{ fontSize: '0.875rem' }}>
                  Supprimer
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
