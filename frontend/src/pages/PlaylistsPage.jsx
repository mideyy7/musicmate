import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlaylists } from '../services/api';
import NavBar from '../components/NavBar';
import CreatePlaylistModal from '../components/CreatePlaylistModal';

export default function PlaylistsPage() {
  const navigate = useNavigate();
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    loadPlaylists();
  }, []);

  async function loadPlaylists() {
    try {
      const data = await getPlaylists();
      setPlaylists(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <div className="page-content">
        <div className="page-header">
          <h1>Playlists</h1>
          <button
            className="btn-secondary-small"
            onClick={() => setShowCreate(true)}
          >
            + Group
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="swipe-loading">
            <div className="spotify-loading-icon"></div>
            <p>Loading playlists...</p>
          </div>
        ) : playlists.length === 0 ? (
          <div className="swipe-empty">
            <div className="empty-icon">♫</div>
            <h2>No playlists yet</h2>
            <p>Match with someone to get an auto-generated shared playlist, or create a group playlist!</p>
          </div>
        ) : (
          <div className="playlist-grid">
            {playlists.map((pl) => (
              <div
                key={pl.id}
                className="playlist-card"
                onClick={() => navigate(`/playlists/${pl.id}`)}
              >
                <div className="playlist-card-icon">
                  {pl.playlist_type === 'match' ? '♥' : '♫'}
                </div>
                <div className="playlist-card-info">
                  <h3>{pl.name}</h3>
                  {pl.description && (
                    <p className="playlist-card-desc">{pl.description}</p>
                  )}
                  <div className="playlist-card-meta">
                    <span>{pl.track_count} track{pl.track_count !== 1 ? 's' : ''}</span>
                    <span>{pl.member_count} member{pl.member_count !== 1 ? 's' : ''}</span>
                    <span className={`playlist-type-badge ${pl.playlist_type}`}>
                      {pl.playlist_type}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showCreate && (
        <CreatePlaylistModal
          onClose={() => setShowCreate(false)}
          onCreate={() => {
            setShowCreate(false);
            loadPlaylists();
          }}
        />
      )}

      <NavBar />
    </div>
  );
}
