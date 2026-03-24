import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { casComplete, getMe } from '../services/api';

export default function CasCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { loginWithToken } = useAuth();
  const [error, setError] = useState('');
  const [status, setStatus] = useState('Verifying with University of Manchester...');
  const calledRef = useRef(false);

  useEffect(() => {
    if (calledRef.current) return;
    calledRef.current = true;

    const username = searchParams.get('username');
    const fullname = searchParams.get('fullname');
    const csticket = localStorage.getItem('cas_csticket');

    const fail = (msg) => setTimeout(() => setError(msg), 300);

    if (!username || !fullname) {
      fail('Authentication failed — no credentials received from the university.');
      return;
    }

    if (!csticket) {
      fail('Session expired. Please try signing in again.');
      return;
    }

    async function complete() {
      try {
        setStatus('Setting up your account...');
        const { access_token, is_new_user } = await casComplete(username, fullname, csticket);
        
        // Remove ticket only AFTER successfully used
        localStorage.removeItem('cas_csticket');
        localStorage.setItem('token', access_token);
        
        setStatus('Loading your profile...');
        const user = await getMe();
        loginWithToken(access_token, user);

        if (is_new_user) {
          navigate('/onboarding', {
            replace: true,
            state: { casData: { display_name: fullname, username } },
          });
        } else {
          navigate('/home', { replace: true });
        }
      } catch (err) {
        setError(err.message);
      }
    }

    complete();
  }, [searchParams, navigate, loginWithToken]);

  if (error) {
    return (
      <div className="auth-container">
        <div className="auth-card" style={{ textAlign: 'center' }}>
          <div className="error-message">{error}</div>
          <button
            className="btn-primary"
            style={{ marginTop: '1rem' }}
            onClick={() => navigate('/sso')}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <div className="spotify-loading-icon"></div>
        <h2 style={{ marginTop: '1rem' }}>{status}</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Please wait a moment.
        </p>
      </div>
    </div>
  );
}
