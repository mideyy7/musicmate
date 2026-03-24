import { createContext, useContext, useEffect, useRef, useState } from 'react';

const SpotifyPlayerContext = createContext(null);

export function useSpotifyPlayer() {
  return useContext(SpotifyPlayerContext);
}

async function fetchFreshToken() {
  try {
    const res = await fetch('/api/spotify/token', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    const data = await res.json();
    return data.access_token || null;
  } catch {
    return null;
  }
}

export function SpotifyPlayerProvider({ children }) {
  const [isReady, setIsReady] = useState(false);
  const [isPremiumError, setIsPremiumError] = useState(false);
  const [currentTrackId, setCurrentTrackId] = useState(null);
  const [currentTrackInfo, setCurrentTrackInfo] = useState(null); // { name, artist, imageUrl }
  const [isPlaying, setIsPlaying] = useState(false);
  const deviceIdRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    async function init() {
      const token = await fetchFreshToken();
      if (!token) return; // not connected or mock mode

      if (window.Spotify) {
        setupPlayer();
      } else {
        window.onSpotifyWebPlaybackSDKReady = setupPlayer;
        const script = document.createElement('script');
        script.src = 'https://sdk.scdn.co/spotify-player.js';
        script.async = true;
        document.body.appendChild(script);
      }
    }

    function setupPlayer() {
      const player = new window.Spotify.Player({
        name: 'MusicMate',
        getOAuthToken: async cb => {
          const t = await fetchFreshToken();
          if (t) cb(t);
        },
        volume: 0.8,
      });

      player.addListener('ready', ({ device_id }) => {
        deviceIdRef.current = device_id;
        setIsReady(true);
      });

      player.addListener('not_ready', () => {
        deviceIdRef.current = null;
        setIsReady(false);
      });

      player.addListener('player_state_changed', state => {
        if (!state) return;
        const track = state.track_window?.current_track;
        setCurrentTrackId(track?.id || null);
        setIsPlaying(!state.paused);
        if (track) {
          setCurrentTrackInfo({
            name: track.name,
            artist: track.artists?.map(a => a.name).join(', ') || '',
            imageUrl: track.album?.images?.[0]?.url || null,
          });
        }
      });

      // Non-premium accounts can't use the SDK
      player.addListener('account_error', () => setIsPremiumError(true));
      player.addListener('authentication_error', () => setIsReady(false));

      player.connect();
      playerRef.current = player;
    }

    init();

    return () => {
      playerRef.current?.disconnect();
    };
  }, []);

  async function stopTrack() {
    await playerRef.current?.pause();
    setCurrentTrackId(null);
    setCurrentTrackInfo(null);
    setIsPlaying(false);
  }

  async function playTrack(spotifyId) {
    if (!deviceIdRef.current) return;

    // Same track: toggle play/pause
    if (currentTrackId === spotifyId) {
      if (isPlaying) {
        playerRef.current?.pause();
      } else {
        playerRef.current?.resume();
      }
      return;
    }

    // New track: start playback via Web API
    const token = await fetchFreshToken();
    if (!token) return;
    await fetch(
      `https://api.spotify.com/v1/me/player/play?device_id=${deviceIdRef.current}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uris: [`spotify:track:${spotifyId}`] }),
      }
    );
  }

  return (
    <SpotifyPlayerContext.Provider
      value={{ isReady, isPremiumError, currentTrackId, currentTrackInfo, isPlaying, playTrack, stopTrack }}
    >
      {children}
    </SpotifyPlayerContext.Provider>
  );
}
