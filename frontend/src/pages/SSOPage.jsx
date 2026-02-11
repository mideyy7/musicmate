import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ssoInitiate } from '../services/api';

export default function SSOPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSSO(e) {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const ssoData = await ssoInitiate(email);
      navigate('/onboarding', { state: { ssoData } });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>University SSO</h1>
          <p>Enter your University of Manchester email to verify your student status</p>
        </div>

        <form onSubmit={handleSSO} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="sso-email">University Email</label>
            <input
              id="sso-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.name@manchester.ac.uk"
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Verifying...' : 'Verify with SSO'}
          </button>
        </form>

        <Link to="/login" className="back-link">
          Back to login
        </Link>
      </div>
    </div>
  );
}
