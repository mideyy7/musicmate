import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMatches, getUnreadCount } from '../services/api';
import NavBar from '../components/NavBar';

export default function MatchesPage() {
  const navigate = useNavigate();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState(null);
  const [unreadByMatch, setUnreadByMatch] = useState({});

  useEffect(() => {
    loadMatches();
    loadUnread();
  }, []);

  async function loadMatches() {
    try {
      const data = await getMatches();
      setMatches(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadUnread() {
    try {
      const data = await getUnreadCount();
      setUnreadByMatch(data.by_match || {});
    } catch {
      // ignore
    }
  }

  function toggleExpand(matchId) {
    setExpanded(expanded === matchId ? null : matchId);
  }

  return (
    <div className="page-container">
      <div className="page-content">
        <div className="page-header">
          <h1>Matches</h1>
          <span className="match-count">{matches.length} match{matches.length !== 1 ? 'es' : ''}</span>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="swipe-loading">
            <div className="spotify-loading-icon"></div>
            <p>Loading your matches...</p>
          </div>
        ) : matches.length === 0 ? (
          <div className="swipe-empty">
            <div className="empty-icon">★</div>
            <h2>No matches yet</h2>
            <p>Start swiping on Discover to find your music matches!</p>
          </div>
        ) : (
          <div className="matches-list">
            {matches.map((match) => (
              <div
                key={match.id}
                className={`match-card ${expanded === match.id ? 'expanded' : ''}`}
                onClick={() => toggleExpand(match.id)}
              >
                <div className="match-card-main">
                  <div className="match-card-avatar">
                    {match.other_user.display_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="match-card-info">
                    <h3>{match.other_user.display_name}</h3>
                    <div className="match-card-meta">
                      {match.other_user.course && <span>{match.other_user.course}</span>}
                      {match.other_user.year && <span>Year {match.other_user.year}</span>}
                    </div>
                  </div>
                  <div className="match-card-actions">
                    <div className="match-card-score">
                      <span className="score-value">{Math.round(match.compatibility_score)}%</span>
                    </div>
                    <button
                      className="chat-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/chat/${match.id}`);
                      }}
                    >
                      Chat
                      {unreadByMatch[match.id] > 0 && (
                        <span className="unread-badge">{unreadByMatch[match.id]}</span>
                      )}
                    </button>
                  </div>
                </div>

                {expanded === match.id && (
                  <div className="match-card-details">
                    {match.breakdown.shared_artists.length > 0 && (
                      <div className="match-detail-section">
                        <h4>Shared Artists</h4>
                        <div className="shared-tags">
                          {match.breakdown.shared_artists.map((a) => (
                            <span key={a} className="shared-tag artist-tag">{a}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {match.breakdown.shared_genres.length > 0 && (
                      <div className="match-detail-section">
                        <h4>Shared Genres</h4>
                        <div className="shared-tags">
                          {match.breakdown.shared_genres.map((g) => (
                            <span key={g} className="shared-tag genre-tag">{g}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="match-detail-stats">
                      <div className="detail-stat">
                        <span className="detail-stat-value">
                          {Math.round(match.breakdown.artist_overlap_pct * 100)}%
                        </span>
                        <span className="detail-stat-label">Artist Overlap</span>
                      </div>
                      <div className="detail-stat">
                        <span className="detail-stat-value">
                          {Math.round(match.breakdown.genre_overlap_pct * 100)}%
                        </span>
                        <span className="detail-stat-label">Genre Overlap</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <NavBar />
    </div>
  );
}
