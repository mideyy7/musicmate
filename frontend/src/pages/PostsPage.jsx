import { useEffect, useState } from 'react';
import { getPosts, postTune, reactToTune } from '../services/api';
import NavBar from '../components/NavBar';

export default function PostsPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [songName, setSongName] = useState('');
  const [artist, setArtist] = useState('');
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPosts();
  }, []);

  async function loadPosts() {
    try {
      const data = await getPosts();
      setPosts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handlePost(e) {
    e.preventDefault();
    if (!songName.trim() || !artist.trim()) return;
    setPosting(true);
    setError('');
    try {
      const newPost = await postTune({ song_name: songName.trim(), artist: artist.trim() });
      setPosts(prev => [newPost, ...prev]);
      setSongName('');
      setArtist('');
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  async function handleReact(postId, type) {
    try {
      const updated = await reactToTune(postId, type);
      setPosts(prev => prev.map(p => p.id === postId ? updated : p));
    } catch { /* ignore */ }
  }

  function getAvatar(post) {
    if (post.profile_picture) {
      return <img src={post.profile_picture} alt={post.display_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />;
    }
    return (post.display_name || '?').charAt(0).toUpperCase();
  }

  return (
    <div className="page-container">
      <NavBar />
      <div className="posts-page">
        {/* Post Form */}
        <div className="post-form-card">
          <div className="post-form-title">
            <span>🎵</span> Share your Tune of the Day
          </div>
          <form onSubmit={handlePost}>
            <div className="post-form-fields">
              <input
                type="text"
                placeholder="Song Name"
                value={songName}
                onChange={e => setSongName(e.target.value)}
                disabled={posting}
              />
              <input
                type="text"
                placeholder="Artist"
                value={artist}
                onChange={e => setArtist(e.target.value)}
                disabled={posting}
              />
            </div>
            {error && <div className="error-message" style={{ marginBottom: '0.75rem' }}>{error}</div>}
            <button type="submit" className="btn-primary" disabled={posting || !songName.trim() || !artist.trim()} style={{ marginTop: 0 }}>
              {posting ? 'Posting...' : 'Post Tune'}
            </button>
          </form>
        </div>

        {/* Posts Feed */}
        {loading ? (
          <div className="swipe-loading">
            <div className="spotify-loading-icon"></div>
            <p>Loading posts...</p>
          </div>
        ) : (
          <div className="posts-feed">
            {posts.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 0' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🎵</div>
                <p>No tunes posted yet. Be the first!</p>
              </div>
            ) : (
              posts.map(post => (
                <div key={post.id} className="post-card">
                  <div className="post-card-header">
                    <div className="post-avatar">{getAvatar(post)}</div>
                    <div className="post-user-info">
                      <h4>{post.display_name}</h4>
                      <div className="post-time">{post.time_ago}</div>
                    </div>
                  </div>

                  <div className="post-song-card">
                    <div className="post-song-icon">♪</div>
                    <div className="post-song-info">
                      <div className="post-song-name">{post.song_name}</div>
                      <div className="post-song-artist">{post.artist}</div>
                    </div>
                    <button className="post-play-btn" title="Play">▶</button>
                  </div>

                  <div className="post-actions">
                    <button
                      className={`post-action-btn ${post.my_reaction === 'like' ? 'liked' : ''}`}
                      onClick={() => handleReact(post.id, 'like')}
                    >
                      <span>♥</span>
                      <span>{post.likes}</span>
                    </button>
                    <button
                      className={`post-action-btn ${post.my_reaction === 'dislike' ? 'disliked' : ''}`}
                      onClick={() => handleReact(post.id, 'dislike')}
                    >
                      <span>👎</span>
                    </button>
                    <button className="post-action-btn">
                      <span>+</span>
                      <span>Add</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
