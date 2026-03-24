import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { updateProfile, getSpotifyAuthUrl, getSpotifyStatus, getMusicProfile, syncSpotifyProfile, spotifyCallback, uploadProfilePicture } from '../services/api';
import MusicProfile from '../components/MusicProfile';
import NavBar from '../components/NavBar';

export default function HomePage() {
  const { user, logout, updateUser } = useAuth();
  const [formData, setFormData] = useState({
    display_name: '',
    nickname: '',
    course: '',
    year: '',
    hobbies: '',
    fun_fact: '',
    bio: '',
    age: '',
    show_course: true,
    show_year: true,
    show_faculty: true,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');

  // Spotify state
  const [spotifyConnected, setSpotifyConnected] = useState(false);
  const [musicProfile, setMusicProfile] = useState(null);
  const [spotifyLoading, setSpotifyLoading] = useState(true);
  const [spotifyEmail, setSpotifyEmail] = useState('');
  const [spotifyEmailError, setSpotifyEmailError] = useState('');

  useEffect(() => {
    setFormData({
      display_name: user.display_name || '',
      nickname: user.nickname || '',
      course: user.course || '',
      year: user.year ? String(user.year) : '',
      hobbies: user.hobbies || '',
      fun_fact: user.fun_fact || '',
      bio: user.bio || '',
      age: user.age ? String(user.age) : '',
      show_course: user.show_course ?? true,
      show_year: user.show_year ?? true,
      show_faculty: user.show_faculty ?? true,
    });
    if (user.spotify_email) setSpotifyEmail(user.spotify_email);
    loadSpotifyData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadSpotifyData() {
    try {
      const status = await getSpotifyStatus();
      setSpotifyConnected(status.connected);
      if (status.connected) {
        try {
          const profile = await getMusicProfile();
          setMusicProfile(profile);
        } catch {
          // Profile not synced yet — trigger a sync now
          try {
            const profile = await syncSpotifyProfile();
            setMusicProfile(profile);
          } catch { /* still failed, show reconnect message */ }
        }
      }
    } catch { /* not connected */ }
    finally { setSpotifyLoading(false); }
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      const updates = {
        display_name: formData.display_name || undefined,
        nickname: formData.nickname || null,
        course: formData.course || null,
        year: formData.year ? parseInt(formData.year) : null,
        hobbies: formData.hobbies || null,
        fun_fact: formData.fun_fact || null,
        bio: formData.bio || null,
        age: formData.age ? parseInt(formData.age) : null,
        show_course: formData.show_course,
        show_year: formData.show_year,
        show_faculty: formData.show_faculty,
      };
      const updated = await updateProfile(updates);
      updateUser(updated);
      setMessage('Profile saved successfully!');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handlePictureChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const updated = await uploadProfilePicture(file);
      updateUser(updated);
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleChangePassword(e) {
    e.preventDefault();
    if (!newPassword || newPassword.length < 6) {
      setPasswordMsg('Password must be at least 6 characters.');
      return;
    }
    try {
      const updated = await updateProfile({ password: newPassword });
      updateUser(updated);
      setPasswordMsg('Password updated!');
      setNewPassword('');
      setTimeout(() => { setShowChangePassword(false); setPasswordMsg(''); }, 1500);
    } catch (err) {
      setPasswordMsg(err.message);
    }
  }

  async function handleConnectSpotify() {
    if (!spotifyEmail.trim()) { setSpotifyEmailError('Please enter your Spotify email.'); return; }
    setSpotifyEmailError('');
    try {
      const updated = await updateProfile({ spotify_email: spotifyEmail.trim() });
      updateUser(updated);
      const { auth_url } = await getSpotifyAuthUrl();
      if (auth_url.startsWith('mock://')) {
        // Mock mode: skip OAuth, connect and sync directly
        await spotifyCallback('mock_code');
        const profile = await syncSpotifyProfile();
        setMusicProfile(profile);
        setSpotifyConnected(true);
      } else {
        window.location.href = auth_url;
      }
    } catch (err) {
      setSpotifyEmailError(err.message);
    }
  }

  const initials = user.display_name ? user.display_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : '?';
  const courseYear = [user.course, user.year ? `Year ${user.year}` : null].filter(Boolean).join(' • ');

  return (
    <div className="page-container">
      <NavBar />
      <div className="home-page">
        {/* Profile Header */}
        <div className="home-profile-header">
          <div className="home-avatar">
            {user.profile_picture
              ? <img src={user.profile_picture} alt="avatar" />
              : initials}
          </div>
          <div className="home-avatar-info">
            <h2>{user.display_name}</h2>
            {courseYear && <p>{courseYear}</p>}
          </div>
        </div>

        <form onSubmit={handleSave}>
          {/* Account Settings */}
          <div className="home-section">
            <div className="home-section-title">Account Settings</div>
            <div className="settings-grid">
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" name="display_name" value={formData.display_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Nickname</label>
                <input type="text" name="nickname" value={formData.nickname} onChange={handleChange} placeholder="e.g. Johnny" />
              </div>
              <div className="form-group">
                <label>Email (Read Only)</label>
                <div className="input-readonly">{user.email}</div>
              </div>
              <div className="form-group">
                <label>Password</label>
                {!showChangePassword ? (
                  <button type="button" className="change-password-btn" onClick={() => setShowChangePassword(true)}>
                    Change Password
                  </button>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={e => setNewPassword(e.target.value)}
                      placeholder="New password"
                    />
                    {passwordMsg && <span style={{ fontSize: '0.8rem', color: passwordMsg.includes('!') ? 'var(--success)' : 'var(--error)' }}>{passwordMsg}</span>}
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button type="button" className="btn-primary" style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem', marginTop: 0 }} onClick={handleChangePassword}>Save</button>
                      <button type="button" className="btn-secondary" style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }} onClick={() => { setShowChangePassword(false); setPasswordMsg(''); }}>Cancel</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Public Profile */}
          <div className="home-section">
            <div className="home-section-title">Public Profile</div>
            <div className="settings-grid">
              <div className="form-group">
                <label>Profile Picture</label>
                <input type="file" accept="image/*" onChange={handlePictureChange} />
              </div>
              <div className="form-group">
                <label>Course Studying</label>
                <input type="text" name="course" value={formData.course} onChange={handleChange} placeholder="e.g. Computer Science" />
              </div>
              <div className="form-group">
                <label>Year in University</label>
                <select name="year" value={formData.year} onChange={handleChange}>
                  <option value="">Select year</option>
                  <option value="1">Year 1</option>
                  <option value="2">Year 2</option>
                  <option value="3">Year 3</option>
                  <option value="4">Year 4</option>
                  <option value="5">Year 5</option>
                  <option value="6">Year 6</option>
                </select>
              </div>
              <div className="form-group">
                <label>Age</label>
                <input type="number" name="age" value={formData.age} onChange={handleChange} placeholder="e.g. 20" min="16" max="99" />
              </div>
              <div className="form-group full-width">
                <label>Hobbies (comma separated)</label>
                <input type="text" name="hobbies" value={formData.hobbies} onChange={handleChange} placeholder="e.g. Gaming, Football, Chess" />
              </div>
              <div className="form-group full-width">
                <label>Fun Fact</label>
                <input type="text" name="fun_fact" value={formData.fun_fact} onChange={handleChange} placeholder="Something interesting about you..." />
              </div>
              <div className="form-group full-width">
                <label>Bio</label>
                <textarea name="bio" value={formData.bio} onChange={handleChange} placeholder='e.g. "I love coffee, indie music, and late night study sessions."' />
              </div>
            </div>
          </div>

          {message && (
            <div className={message.includes('success') || message.includes('!') ? 'success-message' : 'error-message'} style={{ marginBottom: '1rem' }}>
              {message}
            </div>
          )}

          <button type="submit" className="btn-primary home-save-btn" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>

        {/* Spotify Section */}
        <div className="spotify-section" style={{ marginTop: '2.5rem' }}>
          <div className="home-section-title" style={{ marginBottom: '1.25rem' }}>Spotify & Music Profile</div>
          {spotifyLoading ? (
            <div className="spotify-card"><p className="text-muted">Loading Spotify status...</p></div>
          ) : !spotifyConnected ? (
            <div className="spotify-card spotify-connect-card">
              <div className="spotify-connect-content">
                <h3>Connect Your Spotify</h3>
                <p>Your MusicMate account uses your university email. Enter the email associated with your Spotify account to link it.</p>
                <div className="spotify-email-form">
                  <div className="form-group">
                    <label>Spotify Email</label>
                    <input type="email" placeholder="your.email@example.com" value={spotifyEmail} onChange={e => setSpotifyEmail(e.target.value)} />
                  </div>
                  {spotifyEmailError && <div className="error-message" style={{ marginBottom: '0.75rem' }}>{spotifyEmailError}</div>}
                  <button onClick={handleConnectSpotify} className="btn-spotify" style={{ width: '100%' }}>Connect Spotify</button>
                </div>
              </div>
            </div>
          ) : (
            musicProfile
              ? <MusicProfile profile={musicProfile} onUpdate={setMusicProfile} onDisconnect={() => { setSpotifyConnected(false); setMusicProfile(null); }} />
              : <div className="spotify-card"><h3>Spotify Connected</h3><p className="text-muted">Your profile is being set up. Try refreshing.</p></div>
          )}
        </div>

        {/* Logout */}
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
          <button onClick={logout} className="btn-secondary">Log Out</button>
        </div>
      </div>
    </div>
  );
}
