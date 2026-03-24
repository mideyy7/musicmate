import { useEffect, useState } from 'react';
import { getCampusPulse } from '../services/api';
import NavBar from '../components/NavBar';
import TrackActions from '../components/TrackActions';

// Mock fallback data — gospel theme
const MOCK_DATA = {
  campus_top_50: [
    { rank: 1, song_name: 'Way Maker',            artist: 'Sinach',              likes: 42, spotify_id: '6y0igZArWVi6Iz0rj35c1Y', spotify_url: 'https://open.spotify.com/search/Way%20Maker%20Sinach' },
    { rank: 2, song_name: 'The Blessing',          artist: 'Elevation Worship',   likes: 38, spotify_id: '3Blp2bAlBcxp8CBPF0T8W7', spotify_url: 'https://open.spotify.com/search/The%20Blessing%20Elevation%20Worship' },
    { rank: 3, song_name: 'Goodness of God',       artist: 'CeCe Winans',         likes: 31, spotify_id: '1xR3kzx9OHTQP6UPKfSQfz', spotify_url: 'https://open.spotify.com/search/Goodness%20of%20God%20CeCe%20Winans' },
    { rank: 4, song_name: 'What A Beautiful Name', artist: 'Hillsong Worship',    likes: 24, spotify_id: '0BjC1NfoEOOusryehmNe5R', spotify_url: 'https://open.spotify.com/search/What%20A%20Beautiful%20Name%20Hillsong' },
    { rank: 5, song_name: 'Joyful',                artist: 'Dante Bowe',          likes: 19, spotify_id: '0MoSqJpK8mglxq5W7YsJmj', spotify_url: 'https://open.spotify.com/search/Joyful%20Dante%20Bowe' },
  ],
  friend_favorites: [
    { user_id: 1, display_name: 'Adaeze', song_name: 'Way Maker',       artist: 'Sinach',            profile_picture: 'https://randomuser.me/api/portraits/women/1.jpg', spotify_id: '6y0igZArWVi6Iz0rj35c1Y', spotify_url: 'https://open.spotify.com/search/Way%20Maker%20Sinach' },
    { user_id: 2, display_name: 'Joshua', song_name: 'The Blessing',    artist: 'Elevation Worship', profile_picture: 'https://randomuser.me/api/portraits/men/3.jpg',   spotify_id: '3Blp2bAlBcxp8CBPF0T8W7', spotify_url: 'https://open.spotify.com/search/The%20Blessing%20Elevation%20Worship' },
    { user_id: 3, display_name: 'Grace',  song_name: 'Goodness of God', artist: 'CeCe Winans',       profile_picture: 'https://randomuser.me/api/portraits/women/5.jpg', spotify_id: '1xR3kzx9OHTQP6UPKfSQfz', spotify_url: 'https://open.spotify.com/search/Goodness%20of%20God%20CeCe%20Winans' },
  ],
  campus_icons: [
    { name: 'Elevation Worship',   image_url: 'https://i.pravatar.cc/150?u=elevationworship', count: 18 },
    { name: 'Kirk Franklin',       image_url: 'https://i.pravatar.cc/150?u=kirkfranklin',     count: 15 },
    { name: 'Maverick City Music', image_url: 'https://i.pravatar.cc/150?u=maverickcity',     count: 13 },
    { name: 'Hillsong Worship',    image_url: 'https://i.pravatar.cc/150?u=hillsongworship',  count: 11 },
    { name: 'Tasha Cobbs Leonard', image_url: 'https://i.pravatar.cc/150?u=tashacobbs',       count: 9  },
    { name: 'Sinach',              image_url: 'https://i.pravatar.cc/150?u=sinach',           count: 7  },
  ],
  genre_pulse: [
    { genre: 'Gospel',               percentage: 40 },
    { genre: 'Contemporary Worship', percentage: 28 },
    { genre: 'Urban Gospel',         percentage: 16 },
    { genre: 'African Gospel',       percentage: 10 },
    { genre: 'Traditional Gospel',   percentage: 6  },
  ],
};

function rankClass(rank) {
  if (rank === 1) return 'gold';
  if (rank === 2) return 'silver';
  if (rank === 3) return 'bronze';
  return '';
}

export default function FeedPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeed();
  }, []);

  async function loadFeed() {
    try {
      const result = await getCampusPulse();
      // Use real data if available, merge with mock for empty arrays
      setData({
        campus_top_50: result.campus_top_50?.length ? result.campus_top_50 : MOCK_DATA.campus_top_50,
        friend_favorites: result.friend_favorites?.length ? result.friend_favorites : MOCK_DATA.friend_favorites,
        campus_icons: result.campus_icons?.length ? result.campus_icons : MOCK_DATA.campus_icons,
        genre_pulse: result.genre_pulse?.length ? result.genre_pulse : MOCK_DATA.genre_pulse,
      });
    } catch {
      setData(MOCK_DATA);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <NavBar />
        <div className="swipe-loading" style={{ paddingTop: '5rem' }}>
          <div className="spotify-loading-icon"></div>
          <p>Loading Campus Pulse...</p>
        </div>
      </div>
    );
  }

  const { campus_top_50, friend_favorites, campus_icons, genre_pulse } = data;

  return (
    <div className="page-container">
      <NavBar />
      <div className="feed-page">
        <div className="feed-page-title">Campus Pulse</div>

        {/* Top 3 cards grid */}
        <div className="feed-top-grid">
          {/* Campus Top 50 */}
          <div className="feed-card">
            <div className="feed-card-title">
              Campus Top 50
              <span className="feed-card-icon">🔥</span>
            </div>
            <div className="top50-list">
              {campus_top_50.slice(0, 5).map(item => (
                <div key={item.rank} className="top50-item">
                  <div className={`top50-rank ${rankClass(item.rank)}`}>{item.rank}</div>
                  {item.cover_image
                    ? <img src={item.cover_image} alt={item.song_name} style={{ width: 36, height: 36, borderRadius: 4, objectFit: 'cover', flexShrink: 0 }} />
                    : <div className="top50-img" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>♪</div>
                  }
                  <div className="top50-info">
                    <div className="top50-song">{item.song_name}</div>
                    <div className="top50-artist">{item.artist}</div>
                  </div>
                  <TrackActions track={{ track_name: item.song_name, artist: item.artist, spotify_id: item.spotify_id, spotify_url: item.spotify_url, preview_url: item.preview_url }} />
                </div>
              ))}
            </div>
          </div>

          {/* Friend Favorites */}
          <div className="feed-card">
            <div className="feed-card-title">
              Friend Favorites
              <span className="feed-card-icon">👥</span>
            </div>
            <div className="friend-fav-list">
              {friend_favorites.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Match with people to see their favorites.</p>
              ) : (
                friend_favorites.map(fav => (
                  <div key={fav.user_id} className="friend-fav-item">
                    <div className="friend-fav-avatar">
                      {fav.profile_picture
                        ? <img src={fav.profile_picture} alt={fav.display_name} />
                        : fav.display_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="friend-fav-info">
                      <div className="friend-fav-playing">{fav.display_name} is playing...</div>
                      <div className="friend-fav-song">{fav.song_name} - {fav.artist}</div>
                    </div>
                    <TrackActions track={{ track_name: fav.song_name, artist: fav.artist, spotify_id: fav.spotify_id, spotify_url: fav.spotify_url, preview_url: fav.preview_url }} />
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Campus Icons */}
          <div className="feed-card">
            <div className="feed-card-title">
              Campus Icons
              <span className="feed-card-icon">🎤</span>
            </div>
            <div className="campus-icons-grid">
              {campus_icons.slice(0, 6).map(icon => (
                <div key={icon.name} className="campus-icon-item">
                  {icon.image_url ? (
                    <img className="campus-icon-img" src={icon.image_url} alt={icon.name} />
                  ) : (
                    <div className="campus-icon-placeholder">
                      {icon.name.charAt(0)}
                    </div>
                  )}
                  <div className="campus-icon-name">{icon.name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Genre Pulse */}
        <div className="feed-card" style={{ maxWidth: '400px' }}>
          <div className="feed-card-title">
            Genre Pulse
            <span className="feed-card-icon">🎸</span>
          </div>
          <div className="genre-pulse-list">
            {genre_pulse.map(g => (
              <div key={g.genre} className="genre-pulse-item">
                <span className="genre-pulse-name">{g.genre}</span>
                <div className="genre-pulse-bar-bg">
                  <div className="genre-pulse-bar" style={{ width: `${g.percentage}%` }} />
                </div>
                <span className="genre-pulse-pct">{g.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
