import { useSpotifyPlayer } from '../context/SpotifyPlayerContext';

function SpotifyIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.516 17.307a.75.75 0 01-1.031.249c-2.824-1.724-6.38-2.114-10.566-1.158a.75.75 0 01-.332-1.463c4.584-1.044 8.516-.594 11.68 1.341a.75.75 0 01.249 1.031zm1.472-3.27a.937.937 0 01-1.288.312c-3.23-1.985-8.155-2.56-11.973-1.401a.937.937 0 01-.527-1.797c4.368-1.28 9.787-.66 13.476 1.598a.938.938 0 01.312 1.288zm.127-3.405C15.31 8.39 9.2 8.19 5.545 9.3a1.125 1.125 0 01-.637-2.155C9.23 5.888 15.97 6.118 20.26 8.6a1.125 1.125 0 01-1.145 1.942 1.033 1.033 0 010-.91z" />
    </svg>
  );
}

/**
 * TrackActions — two buttons for every track:
 *   1. ▶/⏸  Play via Spotify SDK (Premium) or 30-second audio preview fallback
 *   2.  🟢  Open in Spotify
 *
 * Props:
 *   track — { spotify_id, spotify_url, track_name|name, artist, preview_url? }
 */
export default function TrackActions({ track }) {
  const player = useSpotifyPlayer();

  const spotifyId = track?.spotify_id;
  const previewUrl = track?.preview_url || null;
  const trackName = track?.track_name || track?.name || '';
  const artist = track?.artist || '';

  const spotifyUrl =
    track?.spotify_url ||
    (spotifyId ? `https://open.spotify.com/track/${spotifyId}` : null) ||
    `https://open.spotify.com/search/${encodeURIComponent(`${trackName} ${artist}`)}`;

  const isThisTrackPlaying =
    player?.isPlaying && player?.currentTrackId === spotifyId;

  // Button is enabled whenever we have a spotify_id (can always try preview fallback)
  const canPlay = !!spotifyId;

  function handlePlay(e) {
    e.stopPropagation();
    if (!canPlay) return;
    player?.playTrack(spotifyId, previewUrl, { name: trackName, artist, imageUrl: null });
  }

  function handleSpotify(e) {
    e.stopPropagation();
    window.open(spotifyUrl, '_blank', 'noopener');
  }

  const btnBase = {
    background: 'none',
    border: 'none',
    cursor: canPlay ? 'pointer' : 'default',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '4px 6px',
    borderRadius: '4px',
    flexShrink: 0,
    transition: 'opacity 0.15s',
  };

  const playTitle = isThisTrackPlaying
    ? 'Pause'
    : player?.isReady
    ? 'Play (Spotify Premium)'
    : 'Play preview';

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '2px', flexShrink: 0 }}>
      {/* Play / pause button */}
      <button
        onClick={handlePlay}
        title={playTitle}
        style={{
          ...btnBase,
          color: isThisTrackPlaying
            ? '#1db954'
            : canPlay
            ? 'var(--text-primary, #fff)'
            : 'var(--text-muted, #888)',
          opacity: canPlay ? 1 : 0.35,
          fontSize: '0.85rem',
        }}
      >
        {isThisTrackPlaying ? '⏸' : '▶'}
      </button>

      {/* Open in Spotify button */}
      <button
        onClick={handleSpotify}
        title="Open in Spotify"
        style={{ ...btnBase, cursor: 'pointer', color: '#1db954' }}
      >
        <SpotifyIcon />
      </button>
    </div>
  );
}
