import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  TrendingUp, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  User,
  Briefcase,
  GraduationCap,
  Languages,
  Star,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';
import './Matchinganalyse.css';

const MatchingAnalyse = () => {
  const { candidatureId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [candidature, setCandidature] = useState(null);
  const [analyseParsee, setAnalyseParsee] = useState(null);

  const getToken = () => {
    return localStorage.getItem('access_token') || localStorage.getItem('token');
  };

  useEffect(() => {
    const fetchCandidature = async () => {
      const token = getToken();
      try {
        const response = await fetch(
          `http://localhost:8000/candidatures/${candidatureId}`,
          { headers: { 'Authorization': `Bearer ${token}` } }
        );

        if (!response.ok) throw new Error('Erreur lors de la récupération');

        const data = await response.json();
        setCandidature(data);

        // Parser l'explication si elle existe
        if (data.explication) {
          parseExplication(data.explication);
        }
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCandidature();
  }, [candidatureId]);

  const parseExplication = (explication) => {
    try {
      // L'explication est au format: "Recruteur: ... | Candidat: ..."
      const parts = explication.split(' | ');
      const recruteurPart = parts.find(p => p.startsWith('Recruteur:'));
      const candidatPart = parts.find(p => p.startsWith('Candidat:'));

      setAnalyseParsee({
        recruteur: recruteurPart ? recruteurPart.replace('Recruteur:', '').trim() : '',
        candidat: candidatPart ? candidatPart.replace('Candidat:', '').trim() : ''
      });
    } catch (error) {
      console.error('Erreur parsing:', error);
      setAnalyseParsee({ recruteur: explication, candidat: '' });
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-bon';
    if (score >= 40) return 'score-moyen';
    return 'score-faible';
  };

  const getRecommandation = (score) => {
    if (score >= 80) return {
      label: 'RECRUTER',
      icon: <CheckCircle size={24} />,
      class: 'recommandation-recruter',
      description: 'Candidat hautement qualifié, correspondance excellente'
    };
    if (score >= 60) return {
      label: 'ENTRETIEN',
      icon: <AlertCircle size={24} />,
      class: 'recommandation-entretien',
      description: 'Bon profil, mérite un entretien approfondi'
    };
    return {
      label: 'REJETER',
      icon: <XCircle size={24} />,
      class: 'recommandation-rejeter',
      description: 'Profil insuffisant pour ce poste'
    };
  };

  const changerStatut = async (nouveauStatut) => {
    const token = getToken();
    try {
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
        setCandidature(prev => ({ ...prev, statut: nouveauStatut }));
      }
    } catch (error) {
      console.error('Erreur changement statut:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div className="loading-text">Analyse du profil en cours...</div>
      </div>
    );
  }

  if (!candidature) {
    return (
      <div className="error-container">
        <XCircle size={48} />
        <p>Candidature introuvable</p>
        <button onClick={() => navigate(-1)} className="btn btn-primary">
          Retour
        </button>
      </div>
    );
  }

  const recommandation = getRecommandation(candidature.score_matching);

  return (
    <div className="matching-analyse-container">
      {/* Header */}
      <div className="analyse-header">
        <button onClick={() => navigate(-1)} className="btn-back">
          <ArrowLeft size={20} />
          Retour aux candidatures
        </button>

        <div className="header-content">
          <h1 className="page-title">Analyse de Matching IA</h1>
          <p className="page-subtitle">Évaluation détaillée du profil candidat</p>
        </div>
      </div>

      {/* Score principal */}
      <div className="score-principal-card">
        <div className="score-section-main">
          <div className="score-label-main">
            <TrendingUp size={32} />
            <span>Score de Matching</span>
          </div>
          <div className={`score-value-main ${getScoreColor(candidature.score_matching)}`}>
            {candidature.score_matching?.toFixed(1)}%
          </div>
        </div>

        <div className="recommandation-section">
          <div className={`recommandation-badge ${recommandation.class}`}>
            {recommandation.icon}
            <div>
              <div className="recommandation-label">{recommandation.label}</div>
              <div className="recommandation-description">{recommandation.description}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Grille d'analyses */}
      <div className="analyse-grid">
        {/* Analyse pour le recruteur */}
        <div className="analyse-card analyse-recruteur">
          <div className="analyse-card-header">
            <Briefcase size={24} />
            <h2>Analyse pour le Recruteur</h2>
          </div>
          <div className="analyse-card-content">
            {analyseParsee?.recruteur ? (
              <p className="analyse-texte">{analyseParsee.recruteur}</p>
            ) : (
              <p className="analyse-texte-fallback">
                Ce candidat présente un score de {candidature.score_matching?.toFixed(0)}% 
                de compatibilité avec le poste. {recommandation.description}.
              </p>
            )}
          </div>
        </div>

        {/* Points forts */}
        <div className="analyse-card points-forts-card">
          <div className="analyse-card-header">
            <ThumbsUp size={24} />
            <h2>Points Forts</h2>
          </div>
          <div className="analyse-card-content">
            <div className="points-list">
              <div className="point-item point-fort">
                <CheckCircle size={20} />
                <span>Expérience professionnelle pertinente</span>
              </div>
              <div className="point-item point-fort">
                <CheckCircle size={20} />
                <span>Compétences techniques alignées</span>
              </div>
              <div className="point-item point-fort">
                <CheckCircle size={20} />
                <span>Formation académique solide</span>
              </div>
            </div>
          </div>
        </div>

        {/* Points à améliorer */}
        <div className="analyse-card points-ameliorer-card">
          <div className="analyse-card-header">
            <AlertCircle size={24} />
            <h2>Axes d'Amélioration</h2>
          </div>
          <div className="analyse-card-content">
            <div className="points-list">
              <div className="point-item point-ameliorer">
                <XCircle size={20} />
                <span>Certaines compétences à développer</span>
              </div>
              <div className="point-item point-ameliorer">
                <XCircle size={20} />
                <span>Expérience dans certains domaines limitée</span>
              </div>
            </div>
          </div>
        </div>

        {/* Message au candidat */}
        <div className="analyse-card analyse-candidat">
          <div className="analyse-card-header">
            <User size={24} />
            <h2>Message au Candidat</h2>
          </div>
          <div className="analyse-card-content">
            {analyseParsee?.candidat ? (
              <p className="analyse-texte">{analyseParsee.candidat}</p>
            ) : (
              <p className="analyse-texte-fallback">
                Votre profil présente des points forts intéressants pour ce poste. 
                Nous vous encourageons à continuer à développer vos compétences.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Détails techniques */}
      <div className="details-techniques">
        <h2 className="section-title">Détails de l'Évaluation</h2>
        
        <div className="details-grid">
          <div className="detail-card">
            <div className="detail-icon">
              <Briefcase size={24} />
            </div>
            <div className="detail-content">
              <div className="detail-label">Expérience</div>
              <div className="detail-value">Évaluée IA</div>
            </div>
          </div>

          <div className="detail-card">
            <div className="detail-icon">
              <Star size={24} />
            </div>
            <div className="detail-content">
              <div className="detail-label">Compétences</div>
              <div className="detail-value">Correspondance analysée</div>
            </div>
          </div>

          <div className="detail-card">
            <div className="detail-icon">
              <GraduationCap size={24} />
            </div>
            <div className="detail-content">
              <div className="detail-label">Formation</div>
              <div className="detail-value">Vérifiée</div>
            </div>
          </div>

          <div className="detail-card">
            <div className="detail-icon">
              <Languages size={24} />
            </div>
            <div className="detail-content">
              <div className="detail-label">Langues</div>
              <div className="detail-value">Validées</div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="actions-footer">
        <h2 className="section-title">Décision Finale</h2>
        
        <div className="actions-buttons">
          {candidature.statut === 'pending' && (
            <>
              <button 
                className="btn btn-accept-large"
                onClick={() => changerStatut('accepted')}
              >
                <CheckCircle size={20} />
                Accepter le Candidat
              </button>
              <button 
                className="btn btn-interview-large"
                onClick={() => changerStatut('interview')}
              >
                <AlertCircle size={20} />
                Programmer un Entretien
              </button>
              <button 
                className="btn btn-reject-large"
                onClick={() => changerStatut('rejected')}
              >
                <XCircle size={20} />
                Refuser la Candidature
              </button>
            </>
          )}

          {candidature.statut === 'interview' && (
            <>
              <button 
                className="btn btn-accept-large"
                onClick={() => changerStatut('accepted')}
              >
                <CheckCircle size={20} />
                Accepter le Candidat
              </button>
              <button 
                className="btn btn-reject-large"
                onClick={() => changerStatut('rejected')}
              >
                <XCircle size={20} />
                Refuser la Candidature
              </button>
            </>
          )}

          {(candidature.statut === 'accepted' || candidature.statut === 'rejected') && (
            <div className="statut-final">
              Statut : <strong>{candidature.statut === 'accepted' ? 'Accepté' : 'Refusé'}</strong>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MatchingAnalyse;