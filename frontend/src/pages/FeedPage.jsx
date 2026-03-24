import { useEffect, useState } from 'react';
import { getCampusPulse } from '../services/api';
import NavBar from '../components/NavBar';
import TrackActions from '../components/TrackActions';

// Mock fallback data matching screenshots
const MOCK_DATA = {
  campus_top_50: [
    { rank: 1, song_name: '505', artist: 'Arctic Monkeys', likes: 42, spotify_id: '0BxE4FqsDD1Ot4YuBXwAPp', spotify_url: 'https://open.spotify.com/track/0BxE4FqsDD1Ot4YuBXwAPp' },
    { rank: 2, song_name: 'Blinding Lights', artist: 'The Weeknd', likes: 38, spotify_id: '0VjIjW4GlUZAMYd2vXMi4', spotify_url: 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi4' },
    { rank: 3, song_name: 'The Less I Know The Better', artist: 'Tame Impala', likes: 31, spotify_id: '6K4t31amVTZDgR3sKmwUJJ', spotify_url: 'https://open.spotify.com/track/6K4t31amVTZDgR3sKmwUJJ' },
    { rank: 4, song_name: 'Pink + White', artist: 'Frank Ocean', likes: 24, spotify_id: '3xKsf9qdS1CyvXSMEid6g8', spotify_url: 'https://open.spotify.com/track/3xKsf9qdS1CyvXSMEid6g8' },
    { rank: 5, song_name: 'As It Was', artist: 'Harry Styles', likes: 19, spotify_id: '4LRPiXqCikLlN15c3yImP7', spotify_url: 'https://open.spotify.com/track/4LRPiXqCikLlN15c3yImP7' },
  ],
  friend_favorites: [
    { user_id: 1, display_name: 'Emma', song_name: '505', artist: 'Arctic Monkeys', profile_picture: 'https://i.pravatar.cc/300?img=5', spotify_id: '0BxE4FqsDD1Ot4YuBXwAPp', spotify_url: 'https://open.spotify.com/track/0BxE4FqsDD1Ot4YuBXwAPp' },
    { user_id: 2, display_name: 'James', song_name: 'Blinding Lights', artist: 'The Weeknd', profile_picture: 'https://i.pravatar.cc/300?img=33', spotify_id: '0VjIjW4GlUZAMYd2vXMi4', spotify_url: 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi4' },
    { user_id: 3, display_name: 'Sophie', song_name: 'The Less I Know The Better', artist: 'Tame Impala', profile_picture: 'https://i.pravatar.cc/300?img=9', spotify_id: '6K4t31amVTZDgR3sKmwUJJ', spotify_url: 'https://open.spotify.com/track/6K4t31amVTZDgR3sKmwUJJ' },
  ],
  campus_icons: [
    { name: 'Theophilus Sunday', image_url: null, count: 18 },
    { name: 'Michael Smith', image_url: null, count: 14 },
    { name: 'Don Moen', image_url: null, count: 12 },
    { name: 'Minister GUC', image_url: null, count: 9 },
  ],
  genre_pulse: [
    { genre: 'Gospel', percentage: 45 },
    { genre: 'Hip Hop', percentage: 30 },
    { genre: 'Electronic', percentage: 10 },
    { genre: 'R&B', percentage: 8 },
    { genre: 'Pop', percentage: 7 },
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
