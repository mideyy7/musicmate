import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { spotifyCallback, syncSpotifyProfile } from '../services/api';

export default function SpotifyCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('Connecting to Spotify...');
  const [error, setError] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError('Spotify authorization was denied.');
      return;
    }

    if (!code) {
      setError('No authorization code received from Spotify.');
      return;
    }

    async function handleCallback() {
      try {
        await spotifyCallback(code);
        setStatus('Syncing your music data...');
        await syncSpotifyProfile();
        setStatus('Done! Redirecting...');
        navigate('/dashboard', { replace: true });
      } catch (err) {
        setError(err.message);
      }
    }

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        {error ? (
          <>
            <div className="error-message">{error}</div>
            <button
              className="btn-primary"
              style={{ marginTop: '1rem' }}
              onClick={() => navigate('/dashboard')}
            >
              Back to Dashboard
            </button>
          </>
        ) : (
          <>
            <div className="spotify-loading-icon"></div>
            <h2>{status}</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Please wait while we set up your music profile.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
