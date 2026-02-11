import { useState } from 'react';
import { syncSpotifyProfile, disconnectSpotify } from '../services/api';

export default function MusicProfile({ profile, onUpdate, onDisconnect }) {
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState('');

  async function handleSync() {
    setSyncing(true);
    setMessage('');
    try {
      const updated = await syncSpotifyProfile();
      onUpdate(updated);
      setMessage('Profile synced successfully');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSyncing(false);
    }
  }

  async function handleDisconnect() {
    try {
      await disconnectSpotify();
      onDisconnect();
    } catch (err) {
      setMessage(err.message);
    }
  }

  const { top_artists, top_genres, recent_tracks, listening_patterns, last_synced } = profile;

  return (
    <div className="music-profile">
      <div className="music-profile-header">
        <h3>Your Music Profile</h3>
        <div className="music-profile-actions">
          <button
            onClick={handleSync}
            className="btn-spotify-small"
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Refresh'}
          </button>
          <button onClick={handleDisconnect} className="btn-secondary-small">
            Disconnect
          </button>
        </div>
      </div>

      {message && (
        <div className={message.includes('success') ? 'success-message' : 'error-message'}>
          {message}
        </div>
      )}

      {last_synced && (
        <p className="last-synced">
          Last synced: {new Date(last_synced).toLocaleString()}
        </p>
      )}

      {/* Listening Summary */}
      {listening_patterns && (
        <div className="listening-summary">
          {listening_patterns.top_genre && (
            <div className="summary-stat">
              <span className="stat-value">{listening_patterns.top_genre}</span>
              <span className="stat-label">Top Genre</span>
            </div>
          )}
          <div className="summary-stat">
            <span className="stat-value">{listening_patterns.total_artists}</span>
            <span className="stat-label">Artists</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{listening_patterns.total_genres}</span>
            <span className="stat-label">Genres</span>
          </div>
        </div>
      )}

      {/* Top Artists */}
      {top_artists && top_artists.length > 0 && (
        <div className="music-section">
          <h4>Top Artists</h4>
          <div className="artists-grid">
            {top_artists.slice(0, 8).map((artist, i) => (
              <div key={i} className="artist-card">
                {artist.image_url ? (
                  <img src={artist.image_url} alt={artist.name} className="artist-img" />
                ) : (
                  <div className="artist-img-placeholder">{artist.name[0]}</div>
                )}
                <span className="artist-name">{artist.name}</span>
                <span className="artist-rank">#{artist.rank}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Genres */}
      {top_genres && top_genres.length > 0 && (
        <div className="music-section">
          <h4>Top Genres</h4>
          <div className="genre-tags">
            {top_genres.slice(0, 10).map((g, i) => (
              <span key={i} className="genre-tag">
                {g.genre}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recent Tracks */}
      {recent_tracks && recent_tracks.length > 0 && (
        <div className="music-section">
          <h4>Recently Played</h4>
          <div className="tracks-list">
            {recent_tracks.slice(0, 8).map((track, i) => (
              <div key={i} className="track-row">
                {track.image_url ? (
                  <img src={track.image_url} alt={track.album} className="track-img" />
                ) : (
                  <div className="track-img-placeholder"></div>
                )}
                <div className="track-info">
                  <span className="track-name">{track.name}</span>
                  <span className="track-artist">{track.artist}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
