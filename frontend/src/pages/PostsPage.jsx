import { useEffect, useRef, useState } from 'react';
import { getPosts, postTune, reactToTune, searchSpotifySongs, saveTrackToSpotify } from '../services/api';
import NavBar from '../components/NavBar';
import TrackActions from '../components/TrackActions';

function SpotifyIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style={{ display: 'inline', verticalAlign: 'middle' }}>
      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.516 17.307a.75.75 0 01-1.031.249c-2.824-1.724-6.38-2.114-10.566-1.158a.75.75 0 01-.332-1.463c4.584-1.044 8.516-.594 11.68 1.341a.75.75 0 01.249 1.031zm1.472-3.27a.937.937 0 01-1.288.312c-3.23-1.985-8.155-2.56-11.973-1.401a.937.937 0 01-.527-1.797c4.368-1.28 9.787-.66 13.476 1.598a.938.938 0 01.312 1.288zm.127-3.405C15.31 8.39 9.2 8.19 5.545 9.3a1.125 1.125 0 01-.637-2.155C9.23 5.888 15.97 6.118 20.26 8.6a1.125 1.125 0 01-1.145 1.942 1.033 1.033 0 010-.91z"/>
    </svg>
  );
}

export default function PostsPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [posting, setPosting] = useState(false);

  // Song picker state
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selectedTrack, setSelectedTrack] = useState(null); // { track_name, artist, image_url, spotify_id, spotify_url }
  const searchTimeout = useRef(null);

  // Save-to-Spotify feedback per post
  const [savedTracks, setSavedTracks] = useState({});

  useEffect(() => { loadPosts(); }, []);

  async function loadPosts() {
    try {
      setPosts(await getPosts());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleQueryChange(e) {
    const val = e.target.value;
    setQuery(val);
    setSelectedTrack(null);
    clearTimeout(searchTimeout.current);
    if (!val.trim()) { setSearchResults([]); return; }
    searchTimeout.current = setTimeout(async () => {
      setSearching(true);
      try {
        const results = await searchSpotifySongs(val.trim());
        setSearchResults(results);
      } catch { setSearchResults([]); }
      finally { setSearching(false); }
    }, 350);
  }

  function selectTrack(track) {
    setSelectedTrack(track);
    setQuery(track.track_name);
    setSearchResults([]);
  }

  async function handlePost(e) {
    e.preventDefault();
    if (!selectedTrack && !query.trim()) return;
    setPosting(true);
    setError('');
    try {
      const payload = selectedTrack
        ? { song_name: selectedTrack.track_name, artist: selectedTrack.artist, spotify_id: selectedTrack.spotify_id, spotify_url: selectedTrack.spotify_url, cover_image: selectedTrack.image_url, preview_url: selectedTrack.preview_url }
        : { song_name: query.trim(), artist: '' };
      const newPost = await postTune(payload);
      setPosts(prev => [newPost, ...prev]);
      setQuery('');
      setSelectedTrack(null);
      setSearchResults([]);
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

  async function handleSave(post) {
    if (!post.spotify_id) {
      // No Spotify ID — open Spotify search instead
      openSpotify(post);
      return;
    }
    try {
      await saveTrackToSpotify(post.spotify_id);
      setSavedTracks(prev => ({ ...prev, [post.id]: true }));
      setTimeout(() => setSavedTracks(prev => { const n = {...prev}; delete n[post.id]; return n; }), 3000);
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
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="Search for a song on Spotify..."
                value={query}
                onChange={handleQueryChange}
                disabled={posting}
                style={{ width: '100%', boxSizing: 'border-box' }}
                autoComplete="off"
              />
              {/* Search dropdown */}
              {(searchResults.length > 0 || searching) && !selectedTrack && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                  background: 'var(--card-bg, #1e1e2e)', border: '1px solid var(--border)',
                  borderRadius: '8px', marginTop: '4px', maxHeight: '280px', overflowY: 'auto',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.4)'
                }}>
                  {searching && <div style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Searching...</div>}
                  {searchResults.map((track, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => selectTrack(track)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        width: '100%', padding: '0.6rem 0.9rem', background: 'none',
                        border: 'none', cursor: 'pointer', textAlign: 'left',
                        borderBottom: '1px solid var(--border)'
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--hover-bg, rgba(255,255,255,0.06))'}
                      onMouseLeave={e => e.currentTarget.style.background = 'none'}
                    >
                      {track.image_url
                        ? <img src={track.image_url} alt="" style={{ width: 40, height: 40, borderRadius: 4, objectFit: 'cover', flexShrink: 0 }} />
                        : <div style={{ width: 40, height: 40, borderRadius: 4, background: 'var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>♪</div>
                      }
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>{track.track_name}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{track.artist}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Selected track preview */}
            {selectedTrack && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.6rem 0.75rem', background: 'rgba(29,185,84,0.1)', borderRadius: '8px', marginTop: '0.5rem', border: '1px solid rgba(29,185,84,0.3)' }}>
                {selectedTrack.image_url && <img src={selectedTrack.image_url} alt="" style={{ width: 44, height: 44, borderRadius: 4, objectFit: 'cover' }} />}
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedTrack.track_name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{selectedTrack.artist}</div>
                </div>
                <button type="button" onClick={() => { setSelectedTrack(null); setQuery(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '1.2rem' }}>×</button>
              </div>
            )}

            {error && <div className="error-message" style={{ marginTop: '0.5rem', marginBottom: '0.75rem' }}>{error}</div>}
            <button type="submit" className="btn-primary" disabled={posting || (!selectedTrack && !query.trim())} style={{ marginTop: '0.75rem' }}>
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
                    {post.cover_image
                      ? <img src={post.cover_image} alt={post.song_name} style={{ width: 52, height: 52, borderRadius: 6, objectFit: 'cover', flexShrink: 0 }} />
                      : <div className="post-song-icon">♪</div>
                    }
                    <div className="post-song-info">
                      <div className="post-song-name">{post.song_name}</div>
                      <div className="post-song-artist">{post.artist}</div>
                    </div>
                    <TrackActions track={{ track_name: post.song_name, artist: post.artist, spotify_id: post.spotify_id, spotify_url: post.spotify_url, preview_url: post.preview_url }} />
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
                    <button
                      className="post-action-btn"
                      onClick={() => handleSave(post)}
                      title="Save to Spotify Liked Songs"
                      style={savedTracks[post.id] ? { color: '#1db954' } : {}}
                    >
                      <SpotifyIcon />
                      <span>{savedTracks[post.id] ? 'Saved!' : 'Save'}</span>
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
