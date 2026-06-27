import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import DomainSelection from './pages/DomainSelection';
import Roadmap from './pages/Roadmap';
import TopicPage from './pages/TopicPage';

// Protected Route checks JWT and profile session
const ProtectedRoute: React.FC = () => {
  const auth = useContext(AuthContext);
  const token = localStorage.getItem('token');

  if (!auth) return null;
  const { user, loading } = auth;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-slate-400 text-sm mt-3 font-semibold">Loading AlgoPath...</span>
      </div>
    );
  }

  if (!user && !token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

// Common Layout with Navbar
const AppLayout: React.FC = () => {
  return (
    <div className="bg-slate-950 min-h-screen text-slate-100 flex flex-col">
      <Navbar />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            {/* Public Routes */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/domains" element={<DomainSelection />} />
              <Route path="/domains/:domainSlug/roadmap" element={<Roadmap />} />
              <Route path="/topics/:topicSlug" element={<TopicPage />} />
              <Route path="/dashboard" element={<Navigate to="/domains/dsa/roadmap" replace />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
