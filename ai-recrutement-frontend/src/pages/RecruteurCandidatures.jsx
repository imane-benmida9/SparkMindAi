import React, { useState, useEffect } from 'react';
import { X, User, Calendar, TrendingUp, Eye, Filter } from 'lucide-react';
import './RecruteurCandidatures.css';

const RecruteurCandidatures = () => {
  const [candidatures, setCandidatures] = useState([]);
  const [filteredCandidatures, setFilteredCandidatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidature, setSelectedCandidature] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [sortBy, setSortBy] = useState('score');
  const [filterStatut, setFilterStatut] = useState('all');
  const [offres, setOffres] = useState([]);
  const [selectedOffre, setSelectedOffre] = useState(null);

  // ✅ FONCTION UNIQUE POUR RÉCUPÉRER LE TOKEN
  const getToken = () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    console.log('🔑 Token récupéré:', token ? `${token.substring(0, 20)}...` : 'NULL');
    return token;
  };

  // 1. Charger les offres du recruteur
  useEffect(() => {
    const fetchOffres = async () => {
      const token = getToken();
      
      if (!token) {
        console.error('❌ Aucun token trouvé ! Veuillez vous reconnecter.');
        setLoading(false);
        return;
      }

      try {
        console.log('📡 Récupération des offres...');
        const response = await fetch('http://localhost:8000/offres?mine=true', { 
        // Ajout de ?mine=true pour ne voir QUE vos offres
          headers: {
            'Authorization': `Bearer ${token}`  // ✅ Utilise la variable
  }
});
        if (!response.ok) {
          console.error('❌ Erreur HTTP:', response.status);
          throw new Error('Erreur lors de la récupération des offres');
        }
        
        const data = await response.json();
        console.log('✅ Offres reçues:', data.length);
        setOffres(data);
        
        if (data && data.length > 0) {
          setSelectedOffre(data[0].id);
          console.log('📋 Offre sélectionnée:', data[0].titre);
        } else {
          console.warn('⚠️ Aucune offre trouvée');
          setLoading(false);
        }
      } catch (error) {
        console.error('❌ Erreur chargement offres:', error);
        setLoading(false);
      }
    };
    fetchOffres();
  }, []);

  // 2. Charger les candidatures pour l'offre sélectionnée
  useEffect(() => {
    if (!selectedOffre) {
      console.log('⏳ Aucune offre sélectionnée');
      return;
    }

    const fetchCandidatures = async () => {
      setLoading(true);
      const token = getToken();
      
      if (!token) {
        console.error('❌ Aucun token trouvé !');
        setLoading(false);
        return;
      }

      try {
        console.log('📡 Récupération des candidatures pour offre:', selectedOffre);
        const response = await fetch(
           `http://localhost:8000/candidatures?offre_id=${selectedOffre}`,
        {
           headers: {
      'Authorization': `Bearer ${token}`  // ✅ Utilise la variable
    }
        }
);

        console.log('📊 Réponse HTTP:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ Erreur API:', errorText);
          
          if (response.status === 401) {
            alert('Session expirée. Veuillez vous reconnecter.');
          }
          
          throw new Error('Erreur lors de la récupération des candidatures');
        }

        const data = await response.json();
        console.log('✅ Candidatures reçues:', data);
        
        const candidaturesArray = Array.isArray(data) ? data : [];
        setCandidatures(candidaturesArray);
        setFilteredCandidatures(candidaturesArray);
        
        console.log(`📈 ${candidaturesArray.length} candidature(s) chargée(s)`);
      } catch (error) {
        console.error('❌ Erreur chargement candidatures:', error);
        setCandidatures([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCandidatures();
  }, [selectedOffre]);

  // 3. Appliquer les filtres et le tri
  useEffect(() => {
    let result = [...candidatures];

    if (filterStatut !== 'all') {
      result = result.filter(c => c.statut === filterStatut);
    }

    result.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return (b.score_matching || 0) - (a.score_matching || 0);
        case 'date':
          return new Date(b.date_candidature) - new Date(a.date_candidature);
        case 'statut':
          return (a.statut || "").localeCompare(b.statut || "");
        default:
          return 0;
      }
    });

    setFilteredCandidatures(result);
  }, [candidatures, sortBy, filterStatut]);

  // Changer le statut
  const changerStatut = async (candidatureId, nouveauStatut) => {
    const token = getToken();
    try {
      console.log(`🔄 Changement statut → ${nouveauStatut}`);
      const response = await fetch(
        `http://localhost:8000/candidatures/${candidatureId}/statut`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ statut: nouveauStatut })
        }
      );

      if (response.ok) {
        console.log('✅ Statut mis à jour');
        setCandidatures(prev =>
          prev.map(c => c.id === candidatureId ? { ...c, statut: nouveauStatut } : c)
        );
      } else {
        console.error('❌ Erreur changement statut:', await response.text());
      }
    } catch (error) {
      console.error('❌ Erreur changement statut:', error);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-bon';
    if (score >= 40) return 'score-moyen';
    return 'score-faible';
  };

  const getStatutBadge = (statut) => {
    const labels = {
      pending: 'En attente',
      accepted: 'Accepté',
      rejected: 'Refusé',
      interview: 'Entretien'
    };

    return (
      <span className={`badge badge-${statut}`}>
        {labels[statut] || statut}
      </span>
    );
  };

  const ouvrirDetails = async (candidature) => {
    const token = getToken();
    try {
      const response = await fetch(
        `http://localhost:8000/candidatures/${candidature.id}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const data = await response.json();
      setSelectedCandidature(data);
      setShowModal(true);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div className="loading-text">Analyse des candidatures...</div>
      </div>
    );
  }

  return (
    <div className="candidatures-container">
      <div className="candidatures-header">
        <h1 className="page-title">Gestion des Candidatures</h1>
        <p className="page-subtitle">Évaluez et gérez les candidatures avec l'aide de l'IA</p>
      </div>

      <div className="filters-grid">
        <div className="filter-group">
          <label>Offre d'emploi</label>
          <select value={selectedOffre || ''} onChange={(e) => setSelectedOffre(e.target.value)}>
            {offres.length === 0 ? (
              <option>Aucune offre disponible</option>
            ) : (
              offres.map(offre => (
                <option key={offre.id} value={offre.id}>{offre.titre}</option>
              ))
            )}
          </select>
        </div>

        <div className="filter-group">
          <label>Filtrer par statut</label>
          <select value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)}>
            <option value="all">Tous les statuts</option>
            <option value="pending">En attente</option>
            <option value="interview">Entretien</option>
            <option value="accepted">Accepté</option>
            <option value="rejected">Refusé</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Trier par</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Score IA (décroissant)</option>
            <option value="date">Date (récent)</option>
            <option value="statut">Statut</option>
          </select>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card stat-total">
          <div className="stat-label">Total</div>
          <div className="stat-value">{candidatures.length}</div>
        </div>
        <div className="stat-card stat-pending">
          <div className="stat-label">En attente</div>
          <div className="stat-value">{candidatures.filter(c => c.statut === 'pending').length}</div>
        </div>
        <div className="stat-card stat-interview">
          <div className="stat-label">Entretiens</div>
          <div className="stat-value">{candidatures.filter(c => c.statut === 'interview').length}</div>
        </div>
        <div className="stat-card stat-accepted">
          <div className="stat-label">Acceptés</div>
          <div className="stat-value">{candidatures.filter(c => c.statut === 'accepted').length}</div>
        </div>
      </div>

      <div className="candidatures-list">
        {filteredCandidatures.length === 0 ? (
          <div className="empty-state">
            <Filter size={48} />
            <p>Aucune candidature trouvée pour cette offre.</p>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              {candidatures.length === 0 
                ? "Aucune candidature n'a été soumise pour le moment." 
                : "Essayez de changer les filtres ci-dessus."}
            </p>
          </div>
        ) : (
          filteredCandidatures.map((candidature) => (
            <div key={candidature.id} className="candidature-card">
              <div className="candidature-header-content">
                <div className="candidature-info">
                  <div className="candidature-title">
                    <User size={20} />
                    <h3>Candidat #{candidature.candidat_id?.substring(0, 8)}</h3>
                    {getStatutBadge(candidature.statut)}
                  </div>
                  <div className="candidature-date">
                    <Calendar size={16} />
                    {new Date(candidature.date_candidature).toLocaleDateString('fr-FR')}
                  </div>
                </div>

                <div className="score-section">
                  <div className="score-label">
                    <TrendingUp size={20} />
                    <span>Score IA</span>
                  </div>
                  <div className={`score-value ${getScoreClass(candidature.score_matching)}`}>
                    {candidature.score_matching?.toFixed(0) || 'N/A'}%
                  </div>
                </div>
              </div>

              <div className="candidature-actions">
                <button className="btn btn-details" onClick={() => ouvrirDetails(candidature)}>
                  <Eye size={16} /> Voir détails
                </button>

                {candidature.statut === 'pending' && (
                  <>
                    <button className="btn btn-interview" onClick={() => changerStatut(candidature.id, 'interview')}>
                      Entretien
                    </button>
                    <button className="btn btn-accept" onClick={() => changerStatut(candidature.id, 'accepted')}>
                      Accepter
                    </button>
                    <button className="btn btn-reject" onClick={() => changerStatut(candidature.id, 'rejected')}>
                      Refuser
                    </button>
                  </>
                )}

                {candidature.statut === 'interview' && (
                  <>
                    <button className="btn btn-accept" onClick={() => changerStatut(candidature.id, 'accepted')}>
                      Accepter
                    </button>
                    <button className="btn btn-reject" onClick={() => changerStatut(candidature.id, 'rejected')}>
                      Refuser
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && selectedCandidature && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Détails de la candidature</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={24} />
              </button>
            </div>

            <div className="modal-body">
              <div className="score-detail">
                <div>
                  <div className="score-detail-label">Score de matching IA</div>
                  <div className={`score-detail-value ${getScoreClass(selectedCandidature.score_matching)}`}>
                    {selectedCandidature.score_matching?.toFixed(1) || 'N/A'}%
                  </div>
                </div>
                <TrendingUp size={48} className="score-icon" />
              </div>

              <div className="detail-section">
                <div className="detail-label">Statut actuel</div>
                {getStatutBadge(selectedCandidature.statut)}
              </div>

              {selectedCandidature.explication && (
                <div className="detail-section">
                  <div className="detail-label">Analyse IA du matching</div>
                  <div className="explication-box">
                    {selectedCandidature.explication}
                  </div>
                </div>
              )}

              <div className="detail-section">
                <div className="detail-label">Date de candidature</div>
                <div className="date-info">
                  <Calendar size={16} />
                  {new Date(selectedCandidature.date_candidature).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>

              <div className="ids-section">
                <div>
                  <div className="id-label">ID Candidature</div>
                  <div className="id-value">{selectedCandidature.id}</div>
                </div>
                <div>
                  <div className="id-label">ID Candidat</div>
                  <div className="id-value">{selectedCandidature.candidat_id}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecruteurCandidatures;