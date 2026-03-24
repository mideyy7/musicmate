import { useState } from 'react';
import { Link } from 'react-router-dom';
import { casInitiate } from '../services/api';

export default function SSOPage() {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleCASLogin() {
    setError('');
    setIsLoading(true);

    try {
      const callbackUrl = `${window.location.origin}/cas/callback`;
      const { cas_url, csticket } = await casInitiate(callbackUrl);
      // Store the ticket so CasCallbackPage can retrieve it after CAS redirects back
      localStorage.setItem('cas_csticket', csticket);
      // Redirect the browser to the UoM CAS login page
      window.location.href = cas_url;
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Sign in with University</h1>
          <p>
            Click below to authenticate with your University of Manchester
            account. Only UoM students can access MusicMate.
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="btn-primary"
          onClick={handleCASLogin}
          disabled={isLoading}
          style={{ width: '100%', marginTop: '1rem' }}
        >
          {isLoading ? 'Redirecting...' : 'Sign in with UoM'}
        </button>

        <Link to="/login" className="back-link">
          Back to login
        </Link>
      </div>
    </div>
  );
}
