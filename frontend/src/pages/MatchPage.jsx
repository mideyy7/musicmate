import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMatchFeed, swipe } from '../services/api';
import NavBar from '../components/NavBar';

export default function MatchPage() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchOverlay, setMatchOverlay] = useState(null);
  const [swiping, setSwiping] = useState(false);

  useEffect(() => {
    loadFeed();
  }, []);

  async function loadFeed(filters = {}, retries = 2) {
    setLoading(true);
    setError('');
    try {
      const data = await getMatchFeed(filters);
      setCandidates(data);
      setCurrentIndex(0);
    } catch (err) {
      // If profile isn't ready yet, retry once after a short delay
      if (err.message?.includes('sync your music profile') && retries > 0) {
        setTimeout(() => loadFeed(filters, retries - 1), 1500);
        return;
      }
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
          matchId: result.match_id,
          name: candidate.display_name,
          profilePicture: candidate.profile_picture,
          score: candidate.compatibility_score,
          sharedArtists: candidate.breakdown?.shared_artists || [],
        });
      } else {
        setCurrentIndex(i => i + 1);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSwiping(false);
    }
  }

  function dismissMatch() {
    setMatchOverlay(null);
    setCurrentIndex(i => i + 1);
  }

  const candidate = candidates[currentIndex];
  const hasMore = currentIndex < candidates.length;

  // Parse hobbies into tags
  function getHobbies(c) {
    if (!c.hobbies) return [];
    return c.hobbies.split(',').map(h => h.trim()).filter(Boolean);
  }

  return (
    <div className="page-container">
      <NavBar />
      <div className="match-page">
        {error && !error.includes('sync your music profile') && (
          <div className="error-message" style={{ position: 'absolute', top: '80px', left: '50%', transform: 'translateX(-50%)', zIndex: 10 }}>
            {error}
          </div>
        )}

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
            <button className="btn-primary" onClick={() => loadFeed()}>Refresh</button>
          </div>
        ) : (
          <div className="match-stage">
            {/* Pass (X) button — left side */}
            <button
              className="swipe-side-btn swipe-pass-btn"
              onClick={() => handleSwipe('pass')}
              disabled={swiping}
            >
              ✕
            </button>

            {/* Card */}
            <div className="swipe-card-outer">
              <div className="swipe-card-new">
                {candidate.profile_picture ? (
                  <img className="swipe-card-photo" src={candidate.profile_picture} alt={candidate.display_name} />
                ) : (
                  <div className="swipe-card-photo-placeholder">
                    {candidate.display_name.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="swipe-card-body">
                  <div className="swipe-card-name-age">
                    {candidate.display_name}{candidate.age ? `, ${candidate.age}` : ''}
                  </div>
                  {(candidate.course || candidate.year) && (
                    <div className="swipe-card-course">
                      {[candidate.course, candidate.year ? `Year ${candidate.year}` : null].filter(Boolean).join(' • ')}
                    </div>
                  )}
                  {candidate.bio && (
                    <div className="swipe-card-bio">"{candidate.bio}"</div>
                  )}
                  {getHobbies(candidate).length > 0 && (
                    <div className="swipe-card-tags">
                      {getHobbies(candidate).map(h => (
                        <span key={h} className="swipe-card-tag">{h}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Like (✓) button — right side */}
            <button
              className="swipe-side-btn swipe-like-btn"
              onClick={() => handleSwipe('like')}
              disabled={swiping}
            >
              ✓
            </button>
          </div>
        )}
      </div>

      {matchOverlay && (
        <div className="match-overlay" onClick={dismissMatch}>
          <div className="match-overlay-content" onClick={e => e.stopPropagation()}>
            <div className="match-sparkle">★</div>
            {matchOverlay.profilePicture ? (
              <img
                src={matchOverlay.profilePicture}
                alt={matchOverlay.name}
                style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover', border: '3px solid #1db954', margin: '0.5rem auto 1rem' }}
              />
            ) : (
              <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'rgba(29,185,84,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', margin: '0.5rem auto 1rem' }}>
                {matchOverlay.name.charAt(0)}
              </div>
            )}
            <h1>It's a Match!</h1>
            <p>You and <strong>{matchOverlay.name}</strong> both liked each other</p>
            <div className="match-score">{Math.round(matchOverlay.score)}% Compatible</div>
            {matchOverlay.sharedArtists.length > 0 && (
              <div className="match-shared">
                <p>You both listen to:</p>
                <div className="shared-tags">
                  {matchOverlay.sharedArtists.map(a => (
                    <span key={a} className="shared-tag artist-tag">{a}</span>
                  ))}
                </div>
              </div>
            )}
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem', justifyContent: 'center' }}>
              <button
                className="btn-primary"
                onClick={() => { dismissMatch(); navigate(`/friends/${matchOverlay.matchId}`); }}
              >
                💬 Message them!
              </button>
              <button className="btn-secondary" onClick={dismissMatch}>
                Keep Swiping
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
