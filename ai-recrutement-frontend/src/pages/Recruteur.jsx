import { Routes, Route, Navigate } from 'react-router-dom';
import RecruteurDashboard from '../components/recruteur/RecruteurDashboard';
import JobOfferForm from '../components/recruteur/JobOfferForm';
import OffresList from '../components/recruteur/OffresList';
import CandidaturesRecruteur from '../components/recruteur/CandidaturesRecruteur';
import MatchingResults from '../components/recruteur/MatchingResults';

export default function Recruteur() {
  return (
    <Routes>
      <Route index element={<RecruteurDashboard />} />
      <Route path="offers" element={<JobOfferForm />} />
      <Route path="list" element={<OffresList />} />
      <Route path="candidatures" element={<CandidaturesRecruteur />} />
      <Route path="matching" element={<MatchingResults />} />
      <Route path="*" element={<Navigate to="/recruteur" replace />} />
    </Routes>
  );
}
