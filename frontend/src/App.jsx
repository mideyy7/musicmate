import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { SpotifyPlayerProvider } from './context/SpotifyPlayerContext';
import MiniPlayer from './components/MiniPlayer';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import SSOPage from './pages/SSOPage';
import OnboardingPage from './pages/OnboardingPage';
import SpotifyCallbackPage from './pages/SpotifyCallbackPage';
import CasCallbackPage from './pages/CasCallbackPage';
import HomePage from './pages/HomePage';
import MatchPage from './pages/MatchPage';
import FriendsPage from './pages/FriendsPage';
import PostsPage from './pages/PostsPage';
import FeedPage from './pages/FeedPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <SpotifyPlayerProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/sso" element={<SSOPage />} />
          <Route path="/cas/callback" element={<CasCallbackPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match"
            element={
              <ProtectedRoute>
                <MatchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/friends"
            element={
              <ProtectedRoute>
                <FriendsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/friends/:matchId"
            element={
              <ProtectedRoute>
                <FriendsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/posts"
            element={
              <ProtectedRoute>
                <PostsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/feed"
            element={
              <ProtectedRoute>
                <FeedPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/spotify/callback"
            element={
              <ProtectedRoute>
                <SpotifyCallbackPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
      <MiniPlayer />
      </SpotifyPlayerProvider>
    </AuthProvider>
  );
}

export default App;
