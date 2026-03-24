import { useSpotifyPlayer } from '../context/SpotifyPlayerContext';

export default function MiniPlayer() {
  const player = useSpotifyPlayer();

  if (!player?.currentTrackId) return null;

  const { currentTrackInfo, isPlaying, playTrack, stopTrack, currentTrackId } = player;

  return (
    <div style={{
      position: 'fixed',
      bottom: '1.25rem',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 1000,
      background: 'var(--card-bg, #1e1e2e)',
      border: '1px solid rgba(29,185,84,0.35)',
      borderRadius: '14px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.6rem 0.9rem',
      minWidth: '280px',
      maxWidth: '420px',
    }}>
      {/* Album art */}
      {currentTrackInfo?.imageUrl ? (
        <img
          src={currentTrackInfo.imageUrl}
          alt=""
          style={{ width: 40, height: 40, borderRadius: 6, objectFit: 'cover', flexShrink: 0 }}
        />
      ) : (
        <div style={{
          width: 40, height: 40, borderRadius: 6, flexShrink: 0,
          background: 'rgba(29,185,84,0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.1rem',
        }}>♪</div>
      )}

      {/* Track info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 600, fontSize: '0.85rem',
          color: 'var(--text-primary, #fff)',
          overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis',
        }}>
          {currentTrackInfo?.name || 'Playing...'}
        </div>
        <div style={{
          fontSize: '0.75rem', color: 'var(--text-muted, #888)',
          overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis',
        }}>
          {currentTrackInfo?.artist || ''}
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
        {/* Pause / Resume */}
        <button
          onClick={() => playTrack(currentTrackId, null, currentTrackInfo)}
          title={isPlaying ? 'Pause' : 'Resume'}
          style={{
            background: 'rgba(29,185,84,0.15)',
            border: '1px solid rgba(29,185,84,0.3)',
            borderRadius: '50%',
            width: 32, height: 32,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
            color: '#1db954',
            fontSize: '0.8rem',
          }}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>

        {/* Stop / dismiss */}
        <button
          onClick={stopTrack}
          title="Stop"
          style={{
            background: 'none',
            border: 'none',
            borderRadius: '50%',
            width: 28, height: 28,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
            color: 'var(--text-muted, #888)',
            fontSize: '1rem',
          }}
        >
          ✕
        </button>
      </div>

      {/* Animated playing indicator */}
      {isPlaying && (
        <div style={{
          position: 'absolute', top: 6, right: 10,
          display: 'flex', gap: '2px', alignItems: 'flex-end', height: 10,
        }}>
          {[1, 2, 3].map(i => (
            <div key={i} style={{
              width: 2, borderRadius: 1,
              background: '#1db954',
              animation: `minibar ${0.6 + i * 0.15}s ease-in-out infinite alternate`,
              height: `${4 + i * 2}px`,
            }} />
          ))}
        </div>
      )}

      <style>{`
        @keyframes minibar {
          from { transform: scaleY(0.4); }
          to   { transform: scaleY(1.2); }
        }
      `}</style>
    </div>
  );
}
