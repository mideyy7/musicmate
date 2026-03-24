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

async function fetchPreviewUrl(spotifyId) {
  try {
    const res = await fetch(`/api/spotify/preview/${spotifyId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    const data = await res.json();
    return data.preview_url || null;
  } catch {
    return null;
  }
}

export function SpotifyPlayerProvider({ children }) {
  const [isReady, setIsReady] = useState(false);
  const [isPremiumError, setIsPremiumError] = useState(false);
  const [currentTrackId, setCurrentTrackId] = useState(null);
  const [currentTrackInfo, setCurrentTrackInfo] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const deviceIdRef = useRef(null);
  const playerRef = useRef(null);
  const audioRef = useRef(null);
  const audioTrackIdRef = useRef(null);

  // Set up HTML5 Audio element for preview fallback
  useEffect(() => {
    const audio = new Audio();
    audio.volume = 0.8;
    audio.addEventListener('play', () => setIsPlaying(true));
    audio.addEventListener('pause', () => setIsPlaying(false));
    audio.addEventListener('ended', () => {
      setIsPlaying(false);
      setCurrentTrackId(null);
      setCurrentTrackInfo(null);
      audioTrackIdRef.current = null;
    });
    audioRef.current = audio;
    return () => {
      audio.pause();
      audio.src = '';
    };
  }, []);

  // Initialize Spotify Web Playback SDK (requires Premium)
  useEffect(() => {
    let retryTimer = null;
    let initialized = false;

    async function init() {
      const token = await fetchFreshToken();
      if (!token) {
        // Retry every 5s — will auto-start once Spotify is connected
        retryTimer = setTimeout(init, 5000);
        return;
      }
      if (initialized) return;
      initialized = true;

      if (window.Spotify) {
        setupPlayer();
      } else {
        window.onSpotifyWebPlaybackSDKReady = setupPlayer;
        if (!document.querySelector('script[src*="spotify-player"]')) {
          const script = document.createElement('script');
          script.src = 'https://sdk.scdn.co/spotify-player.js';
          script.async = true;
          document.body.appendChild(script);
        }
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
        // Stop audio fallback if SDK took over
        if (track && audioRef.current && !audioRef.current.paused) {
          audioRef.current.pause();
          audioRef.current.src = '';
          audioTrackIdRef.current = null;
        }
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

      player.addListener('account_error', () => setIsPremiumError(true));
      player.addListener('authentication_error', () => setIsReady(false));

      player.connect();
      playerRef.current = player;
    }

    init();

    return () => {
      clearTimeout(retryTimer);
      playerRef.current?.disconnect();
    };
  }, []);

  async function stopTrack() {
    if (isReady && playerRef.current) {
      await playerRef.current.pause();
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioTrackIdRef.current = null;
    }
    setCurrentTrackId(null);
    setCurrentTrackInfo(null);
    setIsPlaying(false);
  }

  // playTrack(spotifyId, previewUrl?, trackInfo?)
  // 1. If SDK ready → use full Spotify playback
  // 2. Else → fall back to 30-second audio preview
  async function playTrack(spotifyId, previewUrl, trackInfo) {
    if (!spotifyId) return;

    // --- SDK path ---
    if (isReady && deviceIdRef.current) {
      // Same track via SDK: toggle
      if (currentTrackId === spotifyId && audioTrackIdRef.current !== spotifyId) {
        if (isPlaying) {
          playerRef.current?.pause();
        } else {
          playerRef.current?.resume();
        }
        return;
      }

      const token = await fetchFreshToken();
      if (token) {
        const res = await fetch(
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
        if (res.ok || res.status === 204) {
          // Stop audio fallback if running
          if (audioRef.current && !audioRef.current.paused) {
            audioRef.current.pause();
            audioRef.current.src = '';
            audioTrackIdRef.current = null;
          }
          return;
        }
        // SDK play failed — fall through to preview
      }
    }

    // --- Audio preview fallback ---
    // Toggle if same track
    if (audioTrackIdRef.current === spotifyId) {
      if (audioRef.current.paused) {
        await audioRef.current.play().catch(() => {});
      } else {
        audioRef.current.pause();
      }
      return;
    }

    // Get preview URL
    let url = previewUrl || null;
    if (!url) {
      url = await fetchPreviewUrl(spotifyId);
    }

    if (!url) {
      // No preview available — show in mini player but can't play audio
      setCurrentTrackId(spotifyId);
      setCurrentTrackInfo(trackInfo || { name: 'No preview available', artist: 'Open in Spotify to listen' });
      setIsPlaying(false);
      return;
    }

    // Stop whatever was playing
    if (isReady && playerRef.current) {
      await playerRef.current.pause().catch(() => {});
    }
    audioRef.current.pause();

    // Play preview
    audioRef.current.src = url;
    audioTrackIdRef.current = spotifyId;
    setCurrentTrackId(spotifyId);
    setCurrentTrackInfo(trackInfo || { name: 'Preview', artist: '' });
    await audioRef.current.play().catch(() => {
      setIsPlaying(false);
    });
  }

  return (
    <SpotifyPlayerContext.Provider
      value={{ isReady, isPremiumError, currentTrackId, currentTrackInfo, isPlaying, playTrack, stopTrack }}
    >
      {children}
    </SpotifyPlayerContext.Provider>
  );
}
