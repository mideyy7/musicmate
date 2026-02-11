import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { updateProfile, getSpotifyAuthUrl, getSpotifyStatus, getMusicProfile } from '../services/api';
import MusicProfile from '../components/MusicProfile';

export default function DashboardPage() {
  const { user, logout, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Spotify state
  const [spotifyConnected, setSpotifyConnected] = useState(false);
  const [musicProfile, setMusicProfile] = useState(null);
  const [spotifyLoading, setSpotifyLoading] = useState(true);

  useEffect(() => {
    async function loadSpotifyData() {
      try {
        const status = await getSpotifyStatus();
        setSpotifyConnected(status.connected);
        if (status.connected) {
          try {
            const profile = await getMusicProfile();
            setMusicProfile(profile);
          } catch {
            // Profile not synced yet — that's fine
          }
        }
      } catch {
        // Spotify not connected
      } finally {
        setSpotifyLoading(false);
      }
    }
    loadSpotifyData();
  }, []);

  async function handleConnectSpotify() {
    try {
      const { auth_url } = await getSpotifyAuthUrl();
      window.location.href = auth_url;
    } catch (err) {
      setMessage(err.message);
    }
  }

  function startEditing() {
    setFormData({
      display_name: user.display_name,
      course: user.course || '',
      year: user.year || '',
      faculty: user.faculty || '',
      show_course: user.show_course,
      show_year: user.show_year,
      show_faculty: user.show_faculty,
    });
    setEditing(true);
    setMessage('');
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const updates = {
        ...formData,
        year: formData.year ? parseInt(formData.year) : null,
        course: formData.course || null,
        faculty: formData.faculty || null,
      };
      const updatedUser = await updateProfile(updates);
      updateUser(updatedUser);
      setEditing(false);
      setMessage('Profile updated successfully');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>MusicMate</h1>
        <button onClick={logout} className="btn-secondary">
          Log Out
        </button>
      </header>

      {/* Profile Card */}
      <div className="profile-card">
        <div className="profile-header">
          <div className="avatar">{user.display_name[0].toUpperCase()}</div>
          <div>
            <h2>{user.display_name}</h2>
            <p className="email">{user.email}</p>
          </div>
        </div>

        {message && (
          <div className={message.includes('success') ? 'success-message' : 'error-message'}>
            {message}
          </div>
        )}

        {!editing ? (
          <div className="profile-details">
            {user.student_id && (
              <div className="detail-row">
                <span className="detail-label">Student ID</span>
                <span>{user.student_id}</span>
              </div>
            )}
            {user.course && (
              <div className="detail-row">
                <span className="detail-label">Course</span>
                <span>
                  {user.course}
                  {!user.show_course && <span className="hidden-badge">Hidden</span>}
                </span>
              </div>
            )}
            {user.year && (
              <div className="detail-row">
                <span className="detail-label">Year</span>
                <span>
                  {user.year}
                  {!user.show_year && <span className="hidden-badge">Hidden</span>}
                </span>
              </div>
            )}
            {user.faculty && (
              <div className="detail-row">
                <span className="detail-label">Faculty</span>
                <span>
                  {user.faculty}
                  {!user.show_faculty && <span className="hidden-badge">Hidden</span>}
                </span>
              </div>
            )}
            <div className="detail-row">
              <span className="detail-label">Status</span>
              <span className="verified-badge">Verified Student</span>
            </div>

            <button onClick={startEditing} className="btn-primary">
              Edit Profile
            </button>
          </div>
        ) : (
          <form onSubmit={handleSave} className="auth-form">
            <div className="form-group">
              <label htmlFor="edit-display_name">Display Name</label>
              <input
                id="edit-display_name"
                name="display_name"
                type="text"
                value={formData.display_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-course">Course</label>
                <input
                  id="edit-course"
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
                  Visible
                </label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-year">Year</label>
                <input
                  id="edit-year"
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
                  Visible
                </label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-faculty">Faculty</label>
                <input
                  id="edit-faculty"
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
                  Visible
                </label>
              </div>
            </div>

            <div className="button-row">
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setEditing(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Spotify Section */}
      <div className="spotify-section">
        {spotifyLoading ? (
          <div className="spotify-card">
            <p className="text-muted">Loading Spotify status...</p>
          </div>
        ) : !spotifyConnected ? (
          <div className="spotify-card spotify-connect-card">
            <div className="spotify-connect-content">
              <h3>Connect Your Spotify</h3>
              <p>Link your Spotify account to build your music profile and find matches.</p>
              <button onClick={handleConnectSpotify} className="btn-spotify">
                Connect Spotify
              </button>
            </div>
          </div>
        ) : (
          <>
            {musicProfile ? (
              <MusicProfile
                profile={musicProfile}
                onUpdate={setMusicProfile}
                onDisconnect={() => {
                  setSpotifyConnected(false);
                  setMusicProfile(null);
                }}
              />
            ) : (
              <div className="spotify-card">
                <h3>Spotify Connected</h3>
                <p className="text-muted">Your profile is being set up. Try refreshing.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
