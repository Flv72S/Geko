import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import useAuthStore from './store/authStore';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';

// Layout per pagine protette
const ProtectedLayout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};

// Componenti placeholder per Profile e Settings
const Profile = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Profilo</h1>
    <p className="text-gray-600">Gestisci le tue informazioni personali</p>
  </div>
);

const Settings = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Impostazioni</h1>
    <p className="text-gray-600">Configura le preferenze dell'applicazione</p>
  </div>
);

function App() {
  const { initialize, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Inizializza lo stato auth all'avvio
    initialize();
  }, [initialize]);

  return (
    <Router>
      <Routes>
        {/* Route pubbliche */}
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
          }
        />
        <Route
          path="/register"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
          }
        />

        {/* Route protette */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProtectedLayout>
                <Profile />
              </ProtectedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <ProtectedLayout>
                <Settings />
              </ProtectedLayout>
            </ProtectedRoute>
          }
        />

        {/* Redirect root */}
        <Route
          path="/"
          element={
            <Navigate
              to={isAuthenticated ? '/dashboard' : '/login'}
              replace
            />
          }
        />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
