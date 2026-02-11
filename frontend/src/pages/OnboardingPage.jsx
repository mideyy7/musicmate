import { useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ssoComplete, getMe } from '../services/api';

export default function OnboardingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { loginWithToken } = useAuth();

  const ssoData = location.state?.ssoData;

  const [formData, setFormData] = useState({
    display_name: '',
    password: '',
    confirmPassword: '',
    student_id: ssoData?.student_id || '',
    course: ssoData?.course || '',
    year: ssoData?.year || '',
    faculty: ssoData?.faculty || '',
    show_course: true,
    show_year: true,
    show_faculty: true,
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!ssoData) {
    return <Navigate to="/sso" replace />;
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      const { access_token } = await ssoComplete({
        email: ssoData.email,
        password: formData.password,
        display_name: formData.display_name,
        student_id: formData.student_id || null,
        course: formData.course || null,
        year: formData.year ? parseInt(formData.year) : null,
        faculty: formData.faculty || null,
        show_course: formData.show_course,
        show_year: formData.show_year,
        show_faculty: formData.show_faculty,
      });

      localStorage.setItem('token', access_token);
      const user = await getMe();
      loginWithToken(access_token, user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card onboarding-card">
        <div className="auth-header">
          <h1>Welcome to MusicMate</h1>
          <p>
            Verified: <strong>{ssoData.email}</strong>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="display_name">Display Name</label>
            <input
              id="display_name"
              name="display_name"
              type="text"
              value={formData.display_name}
              onChange={handleChange}
              placeholder="How should others see you?"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Create Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 6 characters"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
            />
          </div>

          <h3>Academic Info (detected from SSO)</h3>

          <div className="form-group">
            <label htmlFor="student_id">Student ID</label>
            <input
              id="student_id"
              name="student_id"
              type="text"
              value={formData.student_id}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="course">Course</label>
              <input
                id="course"
                name="course"
                type="text"
                value={formData.course}
                onChange={handleChange}
              />
            </div>
            <div className="form-group visibility-toggle">
              <label>
                <input
                  type="checkbox"
                  name="show_course"
                  checked={formData.show_course}
                  onChange={handleChange}
                />
                Visible on profile
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="year">Year</label>
              <input
                id="year"
                name="year"
                type="number"
                min="1"
                max="7"
                value={formData.year}
                onChange={handleChange}
              />
            </div>
            <div className="form-group visibility-toggle">
              <label>
                <input
                  type="checkbox"
                  name="show_year"
                  checked={formData.show_year}
                  onChange={handleChange}
                />
                Visible on profile
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="faculty">Faculty</label>
              <input
                id="faculty"
                name="faculty"
                type="text"
                value={formData.faculty}
                onChange={handleChange}
              />
            </div>
            <div className="form-group visibility-toggle">
              <label>
                <input
                  type="checkbox"
                  name="show_faculty"
                  checked={formData.show_faculty}
                  onChange={handleChange}
                />
                Visible on profile
              </label>
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Complete Signup'}
          </button>
        </form>
      </div>
    </div>
  );
}
