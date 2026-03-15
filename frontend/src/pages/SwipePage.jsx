import { useEffect, useState } from 'react';
import { getMatchFeed, swipe } from '../services/api';
import NavBar from '../components/NavBar';

export default function SwipePage() {
  const [candidates, setCandidates] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchOverlay, setMatchOverlay] = useState(null);
  const [swiping, setSwiping] = useState(false);

  // Filters
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({ course: '', year: '', faculty: '' });

  useEffect(() => {
    loadFeed();
  }, []);

  async function loadFeed(activeFilters = {}) {
    setLoading(true);
    setError('');
    try {
      const data = await getMatchFeed(activeFilters);
      setCandidates(data);
      setCurrentIndex(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSwipe(action) {
    if (swiping || currentIndex >= candidates.length) return;
    setSwiping(true);

    const candidate = candidates[currentIndex];
    try {
      const result = await swipe(candidate.user_id, action);
      if (result.is_match) {
        setMatchOverlay({
          name: candidate.display_name,
          score: candidate.compatibility_score,
          sharedArtists: candidate.breakdown.shared_artists,
        });
      } else {
        setCurrentIndex((i) => i + 1);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSwiping(false);
    }
  }

  function dismissMatch() {
    setMatchOverlay(null);
    setCurrentIndex((i) => i + 1);
  }

  function applyFilters() {
    const active = {};
    if (filters.course) active.course = filters.course;
    if (filters.year) active.year = filters.year;
    if (filters.faculty) active.faculty = filters.faculty;
    loadFeed(active);
    setShowFilters(false);
  }

  const candidate = candidates[currentIndex];
  const hasMore = currentIndex < candidates.length;

  return (
    <div className="page-container">
      <div className="page-content">
        <div className="page-header">
          <h1>Discover</h1>
          <button
            className="btn-secondary-small"
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="filter-bar">
            <input
              type="text"
              placeholder="Course"
              value={filters.course}
              onChange={(e) => setFilters({ ...filters, course: e.target.value })}
            />
            <input
              type="number"
              placeholder="Year"
              value={filters.year}
              onChange={(e) => setFilters({ ...filters, year: e.target.value })}
            />
            <input
              type="text"
              placeholder="Faculty"
              value={filters.faculty}
              onChange={(e) => setFilters({ ...filters, faculty: e.target.value })}
            />
            <button className="btn-primary filter-apply" onClick={applyFilters}>
              Apply
            </button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="swipe-loading">
            <div className="spotify-loading-icon"></div>
            <p>Finding your music matches...</p>
          </div>
        ) : !hasMore ? (
          <div className="swipe-empty">
            <div className="empty-icon">♪</div>
            <h2>No more people</h2>
            <p>Check back later or adjust your filters to discover more music lovers.</p>
            <button className="btn-primary" onClick={() => loadFeed()}>
              Refresh
            </button>
          </div>
        ) : (
          <div className="swipe-card-wrapper">
            <div className="swipe-card">
              <div className="swipe-card-avatar">
                {candidate.display_name.charAt(0).toUpperCase()}
              </div>
              <h2 className="swipe-card-name">{candidate.display_name}</h2>

              {(candidate.course || candidate.year || candidate.faculty) && (
                <div className="swipe-card-info">
                  {candidate.course && <span>{candidate.course}</span>}
                  {candidate.year && <span>Year {candidate.year}</span>}
                  {candidate.faculty && <span>{candidate.faculty}</span>}
                </div>
              )}

              <div className="compatibility-score">
                <span className="score-value">{Math.round(candidate.compatibility_score)}%</span>
                <span className="score-label">Compatible</span>
              </div>

              {candidate.breakdown.shared_artists.length > 0 && (
                <div className="swipe-section">
                  <h4>Shared Artists</h4>
                  <div className="shared-tags">
                    {candidate.breakdown.shared_artists.map((a) => (
                      <span key={a} className="shared-tag artist-tag">{a}</span>
                    ))}
                  </div>
                </div>
              )}

              {candidate.breakdown.shared_genres.length > 0 && (
                <div className="swipe-section">
                  <h4>Shared Genres</h4>
                  <div className="shared-tags">
                    {candidate.breakdown.shared_genres.map((g) => (
                      <span key={g} className="shared-tag genre-tag">{g}</span>
                    ))}
                  </div>
                </div>
              )}

              {candidate.top_artists.length > 0 && (
                <div className="swipe-section">
                  <h4>Their Top Artists</h4>
                  <div className="shared-tags">
                    {candidate.top_artists.map((a) => (
                      <span key={a} className="shared-tag">{a}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="swipe-actions">
              <button
                className="swipe-btn pass-btn"
                onClick={() => handleSwipe('pass')}
                disabled={swiping}
              >
                ✕
              </button>
              <button
                className="swipe-btn like-btn"
                onClick={() => handleSwipe('like')}
                disabled={swiping}
              >
                ♥
              </button>
            </div>
          </div>
        )}
      </div>

      {matchOverlay && (
        <div className="match-overlay" onClick={dismissMatch}>
          <div className="match-overlay-content">
            <div className="match-sparkle">★</div>
            <h1>It's a Match!</h1>
            <p>You and <strong>{matchOverlay.name}</strong> both liked each other</p>
            <div className="match-score">{Math.round(matchOverlay.score)}% Compatible</div>
            {matchOverlay.sharedArtists.length > 0 && (
              <div className="match-shared">
                <p>You both listen to:</p>
                <div className="shared-tags">
                  {matchOverlay.sharedArtists.map((a) => (
                    <span key={a} className="shared-tag artist-tag">{a}</span>
                  ))}
                </div>
              </div>
            )}
            <button className="btn-primary" style={{ marginTop: '1.5rem' }}>
              Keep Swiping
            </button>
          </div>
        </div>
      )}

      <NavBar />
    </div>
  );
}
