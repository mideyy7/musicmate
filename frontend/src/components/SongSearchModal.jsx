import { useState, useEffect, useRef } from 'react';
import { searchSong } from '../services/api';

export default function SongSearchModal({ onSelect, onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const inputRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!query.trim()) {
      setResults([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await searchSong(query.trim());
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => clearTimeout(debounceRef.current);
  }, [query]);

  function handleSelect(track) {
    onSelect({
      content: `${track.track_name} - ${track.artist}`,
      message_type: 'song_share',
      song_data: {
        track_name: track.track_name,
        artist: track.artist,
        album: track.album,
        image_url: track.image_url,
        spotify_url: track.spotify_url,
        spotify_id: track.spotify_id,
      },
    });
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="song-search-modal" onClick={(e) => e.stopPropagation()}>
        <div className="song-search-header">
          <h3>Share a Song</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <input
          ref={inputRef}
          type="text"
          className="song-search-input"
          placeholder="Search for a song or artist..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <div className="song-results">
          {searching && <p className="text-muted">Searching...</p>}
          {!searching && query && results.length === 0 && (
            <p className="text-muted">No results found</p>
          )}
          {results.map((track) => (
            <button
              key={track.spotify_id}
              className="song-result-row"
              onClick={() => handleSelect(track)}
            >
              <div className="song-result-art">
                {track.image_url ? (
                  <img src={track.image_url} alt={track.track_name} />
                ) : (
                  <div className="song-art-placeholder">♪</div>
                )}
              </div>
              <div className="song-result-info">
                <span className="song-result-name">{track.track_name}</span>
                <span className="song-result-artist">{track.artist} - {track.album}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
