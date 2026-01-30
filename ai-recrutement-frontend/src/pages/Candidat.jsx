import { Routes, Route, Navigate } from 'react-router-dom';
import CandidatDashboard from '../components/candidat/CandidatDashboard';
import ProfileForm from '../components/candidat/ProfileForm';
import CVUploader from '../components/candidat/CVUploader';
import JobSearch from '../components/candidat/JobSearch';
import ApplicationsList from '../components/candidat/ApplicationsList';

export default function Candidat() {
  return (
    <Routes>
      <Route index element={<CandidatDashboard />} />
      <Route path="profile" element={<ProfileForm />} />
      <Route path="cv" element={<CVUploader />} />
      <Route path="search" element={<JobSearch />} />
      <Route path="applications" element={<ApplicationsList />} />
      <Route path="*" element={<Navigate to="/candidat" replace />} />
    </Routes>
  );
}
