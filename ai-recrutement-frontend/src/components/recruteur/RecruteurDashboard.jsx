import React, { useState, useEffect } from 'react';
import { FileText, Users, Clock, TrendingUp, Star, MapPin, Phone } from 'lucide-react';
import './RecruiterDashboard.css';

/* ============================================================
   HELPERS
   ============================================================ */
const STATUT_LABELS = {
  pending:   'En attente',
  accepted:  'Accepté',
  rejected:  'Rejeté',
  interview: 'Entretien',
};

function badgeClass(statut) {
  return `badge badge--${statut || 'pending'}`;
}

function scoreClass(score) {
  if (score >= 80) return 'score--excellent';
  if (score >= 60) return 'score--good';
  if (score >= 40) return 'score--average';
  return 'score--low';
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/* ============================================================
   COMPONENT
   ============================================================ */
const RecruiterDashboard = () => {
  const [stats, setStats]                       = useState(null);
  const [topCandidats, setTopCandidats]         = useState([]);
  const [dernières, setDernières]               = useState([]);
  const [listeCandidats, setListeCandidats]     = useState([]);
  const [loading, setLoading]                   = useState(true);
  const [activeTab, setActiveTab]               = useState('overview');

  /* ---- fetch ---- */
  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const h = {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      };
      const [sR, tR, dR, lR] = await Promise.all([
        fetch('/api/dashboard/stats',                      { headers: h }),
        fetch('/api/dashboard/top-candidats?limit=5',      { headers: h }),
        fetch('/api/dashboard/dernieres-candidatures?limit=8', { headers: h }),
        fetch('/api/dashboard/liste-candidats',            { headers: h }),
      ]);
      setStats(await sR.json());
      setTopCandidats(await tR.json());
      setDernières(await dR.json());
      setListeCandidats(await lR.json());
    } catch (e) {
      console.error('Dashboard fetch error', e);
    } finally {
      setLoading(false);
    }
  };

  /* ---- loading ---- */
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Chargement du tableau de bord…</p>
      </div>
    );
  }

  /* ---- render ---- */
  return (
    <div className="dashboard-root">

      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="dashboard-header__inner">
          <h1>Tableau de bord</h1>
          <p>Vue d'ensemble de vos recrutements et candidatures</p>
        </div>
      </header>

      <div className="dashboard-body">

        {/* ===== STAT CARDS ===== */}
        <div className="stats-grid">
          <StatCard label="Offres ouvertes"     value={stats?.offres_ouvertes     || 0} Icon={FileText}   iconMod="blue"   />
          <StatCard label="Total candidatures"  value={stats?.total_candidatures  || 0} Icon={Users}      iconMod="purple" />
          <StatCard label="En attente"          value={stats?.candidatures_pending|| 0} Icon={Clock}      iconMod="yellow" />
          <StatCard label="Acceptés"            value={stats?.candidatures_accepted||0} Icon={TrendingUp} iconMod="green"  />
        </div>

        {/* ===== ACTIVITÉ RÉCENTE ===== */}
        <div className="activity-banner">
          <h2>Activité récente</h2>
          <span>{stats?.candidatures_recentes || 0} candidatures ces 7 derniers jours</span>
        </div>

        {/* ===== TABS ===== */}
        <div className="tabs-container">
          <nav className="tabs-nav">
            <button className={activeTab === 'overview'   ? 'active' : ''} onClick={() => setActiveTab('overview')}>
              Vue d'ensemble
            </button>
            <button className={activeTab === 'candidats'  ? 'active' : ''} onClick={() => setActiveTab('candidats')}>
              Liste des candidats
            </button>
          </nav>

          <div className="tabs-content">

            {/* ---------- OVERVIEW ---------- */}
            {activeTab === 'overview' && (
              <div className="overview-grid">

                {/* Top candidats */}
                <section>
                  <h3 className="section-title">
                    <Star style={{ color: '#f59e0b' }} /> Top candidats
                  </h3>
                  <div className="card-list">
                    {topCandidats.length === 0 && <EmptyState Icon={Users} msg="Aucun candidat pour le moment" />}
                    {topCandidats.map((c, i) => (
                      <div key={c.id} className="card-item">
                        <div className="top-card">
                          <div className="top-card__left">
                            <div className="top-card__header">
                              <span className="top-card__rank">#{i + 1}</span>
                              <span className="top-card__name">{c.nom}</span>
                            </div>
                            <div className="top-card__meta">
                              {c.localisation && (
                                <span><MapPin /> {c.localisation}</span>
                              )}
                              <span>{c.nombre_candidatures} candidature(s)</span>
                            </div>
                          </div>
                          <div className="top-card__score">
                            <span className={`score-value ${scoreClass(c.score_moyen)}`}>{c.score_moyen}%</span>
                            <span className="score-label">Score moyen</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Dernières candidatures */}
                <section>
                  <h3 className="section-title">
                    <Clock style={{ color: '#3b82f6' }} /> Dernières candidatures
                  </h3>
                  <div className="card-list">
                    {dernières.length === 0 && <EmptyState Icon={FileText} msg="Aucune candidature récente" />}
                    {dernières.map((c) => (
                      <div key={c.id} className="card-item">
                        <div className="cand-card__top">
                          <div>
                            <div className="cand-card__name">{c.candidat_nom}</div>
                            <div className="cand-card__offre">{c.offre_titre}</div>
                          </div>
                          <span className={badgeClass(c.statut)}>{STATUT_LABELS[c.statut] || c.statut}</span>
                        </div>
                        <div className="cand-card__bottom">
                          <span className="cand-card__date">{formatDate(c.date_candidature)}</span>
                          {c.score_matching != null && (
                            <span className={`cand-card__match ${scoreClass(c.score_matching)}`}>
                              Match&nbsp;: {c.score_matching}%
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            )}

            {/* ---------- LISTE CANDIDATS ---------- */}
            {activeTab === 'candidats' && (
              <div>
                <h3 className="section-title" style={{ marginBottom: 20 }}>
                  <Users style={{ color: '#8b5cf6' }} /> Tous les candidats ({listeCandidats.length})
                </h3>

                {listeCandidats.length === 0 ? (
                  <EmptyState Icon={Users} msg="Aucun candidat trouvé" />
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Candidat</th>
                          <th>Offre</th>
                          <th>Statut</th>
                          <th>Score</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {listeCandidats.map((c) => (
                          <tr key={c.candidature_id}>
                            <td>
                              <div className="td-candidate__name">{c.nom}</div>
                              {c.localisation && (
                                <div className="td-candidate__sub"><MapPin /> {c.localisation}</div>
                              )}
                              {c.telephone && (
                                <div className="td-candidate__sub"><Phone /> {c.telephone}</div>
                              )}
                            </td>
                            <td>{c.offre_titre}</td>
                            <td>
                              <span className={badgeClass(c.statut)}>{STATUT_LABELS[c.statut] || c.statut}</span>
                            </td>
                            <td>
                              {c.score_matching != null ? (
                                <span className={`td-score ${scoreClass(c.score_matching)}`}>{c.score_matching}%</span>
                              ) : (
                                <span className="td-score td-score--none">—</span>
                              )}
                            </td>
                            <td className="td-date">{formatDate(c.date_candidature)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
};

/* ============================================================
   SUB-COMPONENTS
   ============================================================ */

/* Carte stat réutilisable */
const StatCard = ({ label, value, Icon, iconMod }) => (
  <div className="stat-card">
    <div className="stat-card__text">
      <p className="label">{label}</p>
      <p className="value">{value}</p>
    </div>
    <div className={`stat-card__icon stat-card__icon--${iconMod}`}>
      <Icon />
    </div>
  </div>
);

/* État vide réutilisable */
const EmptyState = ({ Icon, msg }) => (
  <div className="empty-state">
    <Icon />
    <p>{msg}</p>
  </div>
);

export default RecruiterDashboard;