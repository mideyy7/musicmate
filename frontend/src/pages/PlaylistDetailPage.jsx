import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getPlaylist,
  addTrackToPlaylist,
  removeTrackFromPlaylist,
  removePlaylistMember,
  getWeeklyRecap,
  searchSong,
} from '../services/api';
import { useAuth } from '../context/AuthContext';
import SongSearchModal from '../components/SongSearchModal';

export default function PlaylistDetailPage() {
  const { playlistId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [playlist, setPlaylist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSongSearch, setShowSongSearch] = useState(false);
  const [recap, setRecap] = useState(null);

  useEffect(() => {
    loadPlaylist();
    loadRecap();
  }, [playlistId]);

  async function loadPlaylist() {
    try {
      const data = await getPlaylist(playlistId);
      setPlaylist(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadRecap() {
    try {
      const data = await getWeeklyRecap(playlistId);
      if (data) setRecap(data);
    } catch {
      // no recap yet
    }
  }

  async function handleAddTrack(track) {
    try {
      const trackData = {
        track_name: track.track_name,
        artist: track.artist,
        album: track.album,
        image_url: track.image_url,
        spotify_url: track.spotify_url,
        spotify_id: track.spotify_id,
      };
      const updated = await addTrackToPlaylist(playlistId, trackData);
      setPlaylist(updated);
      setShowSongSearch(false);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRemoveTrack(spotifyId) {
    try {
      const updated = await removeTrackFromPlaylist(playlistId, spotifyId);
      setPlaylist(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRemoveMember(userId) {
    try {
      const updated = await removePlaylistMember(playlistId, userId);
      setPlaylist(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  const isOwner = playlist?.members?.some(
    (m) => m.user_id === user?.id && m.role === 'owner'
  );

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-content">
          <div className="swipe-loading">
            <div className="spotify-loading-icon"></div>
            <p>Loading playlist...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !playlist) {
    return (
      <div className="page-container">
        <div className="page-content">
          <div className="error-message">{error}</div>
          <button className="btn-secondary" onClick={() => navigate('/playlists')}>
            Back to Playlists
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-content playlist-detail">
        <div className="playlist-detail-header">
          <button className="back-btn" onClick={() => navigate('/playlists')}>
            &larr;
          </button>
          <div className="playlist-detail-title">
            <h1>{playlist.name}</h1>
            {playlist.description && <p>{playlist.description}</p>}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {/* Members */}
        <div className="playlist-members">
          <h3>Members</h3>
          <div className="member-pills">
            {playlist.members.map((m) => (
              <div key={m.user_id} className="member-pill">
                <span className="member-avatar">
                  {m.display_name.charAt(0).toUpperCase()}
                </span>
                <span className="member-name">{m.display_name}</span>
                <span className="member-role">{m.role}</span>
                {isOwner &&
                  m.user_id !== user?.id &&
                  playlist.playlist_type === 'group' && (
                    <button
                      className="member-remove"
                      onClick={() => handleRemoveMember(m.user_id)}
                    >
                      &times;
                    </button>
                  )}
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Recap */}
        {recap && recap.recap_data && recap.recap_data.tracks_added > 0 && (
          <div className="weekly-recap-card">
            <h3>This Week's Recap</h3>
            <div className="recap-stats">
              <div className="recap-stat">
                <span className="recap-stat-value">{recap.recap_data.tracks_added}</span>
                <span className="recap-stat-label">Tracks Added</span>
              </div>
              <div className="recap-stat">
                <span className="recap-stat-value">{recap.recap_data.total_tracks}</span>
                <span className="recap-stat-label">Total Tracks</span>
              </div>
            </div>
          </div>
        )}

        {/* Tracks */}
        <div className="playlist-tracks-section">
          <div className="playlist-tracks-header">
            <h3>Tracks ({playlist.track_count})</h3>
            <button
              className="btn-primary-small"
              onClick={() => setShowSongSearch(true)}
            >
              + Add Track
            </button>
          </div>

          {playlist.tracks.length === 0 ? (
            <div className="playlist-empty-tracks">
              <p>No tracks yet. Add some songs to get started!</p>
            </div>
          ) : (
            <div className="playlist-track-list">
              {playlist.tracks.map((track, i) => (
                <div key={track.spotify_id || i} className="playlist-track-item">
                  <div className="track-number">{i + 1}</div>
                  <div className="track-info">
                    <span className="track-name">{track.track_name}</span>
                    <span className="track-artist">{track.artist}</span>
                    {track.album && (
                      <span className="track-album">{track.album}</span>
                    )}
                  </div>
                  <button
                    className="track-remove-btn"
                    onClick={() => handleRemoveTrack(track.spotify_id)}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showSongSearch && (
        <SongSearchModal
          onClose={() => setShowSongSearch(false)}
          onSelect={handleAddTrack}
        />
      )}
    </div>
  );
}
