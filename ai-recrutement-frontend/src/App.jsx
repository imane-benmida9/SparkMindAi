import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect, createContext, useContext } from 'react';
import { getMe, getStoredUser, setStoredUser, setTokens, logout } from './services/authService';

// Dans vos routes protégées pour recruteur :

import Layout from './components/shared/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Candidat from './pages/Candidat';
import RecruteurCandidatures  from './pages/RecruteurCandidatures';
import MatchingAnalyse from './pages/Matchinganalyse';
import Recruteur from './pages/Recruteur';

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((data) => {
        setUser(data);
        setStoredUser(data);
      })
      .catch(() => {
        logout();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const loginSuccess = (tokenData, userData) => {
    setTokens(tokenData.access_token, tokenData.refresh_token);
    setStoredUser(userData || tokenData);
    setUser(userData || { id: tokenData.id, email: tokenData.email, role: tokenData.role });
  };

  const logoutUser = () => {
    logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginSuccess, logoutUser, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="app-main" style={{ marginLeft: 260, padding: '2rem', textAlign: 'center' }}>
        <div className="loading-spinner" />
        <p>Chargement...</p>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to={user.role === 'candidat' ? '/candidat' : '/recruteur'} replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-spinner" style={{ margin: '2rem auto' }} />;
  if (user) {
    return <Navigate to={user.role === 'candidat' ? '/candidat' : '/recruteur'} replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route
            path="/candidat/*"
            element={
              <ProtectedRoute role="candidat">
                <Layout role="candidat">
                  <Candidat />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruteur/candidatures"
            element={
              <ProtectedRoute role="recruteur">
              <Layout role="recruteur">
              <RecruteurCandidatures />
              </Layout>
              </ProtectedRoute>
           }
          />
        
          <Route
            path="/recruteur/*"
            element={
              <ProtectedRoute role="recruteur">
                <Layout role="recruteur">
                  <Recruteur />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
