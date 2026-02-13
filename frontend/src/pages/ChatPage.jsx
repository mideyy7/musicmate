import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getConversation, sendMessage, markAsRead, getChatPrompts, getMatches } from '../services/api';
import SongSearchModal from '../components/SongSearchModal';

export default function ChatPage() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [otherUser, setOtherUser] = useState(null);
  const [compatScore, setCompatScore] = useState(0);
  const [showSongSearch, setShowSongSearch] = useState(false);
  const [prompts, setPrompts] = useState([]);

  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    loadMatchInfo();
    loadMessages();
    loadPrompts();

    // Poll for new messages every 3 seconds
    pollRef.current = setInterval(loadMessages, 3000);
    return () => clearInterval(pollRef.current);
  }, [matchId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }

  async function loadMatchInfo() {
    try {
      const matches = await getMatches();
      const match = matches.find((m) => m.id === parseInt(matchId));
      if (match) {
        setOtherUser(match.other_user);
        setCompatScore(match.compatibility_score);
      }
    } catch {
      // ignore
    }
  }

  async function loadMessages() {
    try {
      const data = await getConversation(matchId);
      setMessages(data);
      // Mark messages as read
      await markAsRead(matchId);
    } catch (err) {
      if (loading) setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadPrompts() {
    try {
      const data = await getChatPrompts();
      setPrompts(data.prompts || []);
    } catch {
      // ignore
    }
  }

  async function handleSend(e) {
    e?.preventDefault();
    if (!input.trim() || sending) return;

    setSending(true);
    try {
      const msg = await sendMessage(matchId, {
        content: input.trim(),
        message_type: 'text',
      });
      setMessages((prev) => [...prev, msg]);
      setInput('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  async function handleSongShare(songMessage) {
    setShowSongSearch(false);
    setSending(true);
    try {
      const msg = await sendMessage(matchId, songMessage);
      setMessages((prev) => [...prev, msg]);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  function handlePromptClick(prompt) {
    setInput(prompt);
  }

  if (loading) {
    return (
      <div className="chat-container">
        <div className="swipe-loading">
          <div className="spotify-loading-icon"></div>
          <p>Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error && !messages.length) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <button className="chat-back" onClick={() => navigate('/matches')}>←</button>
          <span>Chat</span>
        </div>
        <div className="error-message" style={{ margin: '2rem 1rem' }}>{error}</div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="chat-back" onClick={() => navigate('/matches')}>←</button>
        <div className="chat-header-info">
          {otherUser && (
            <>
              <div className="chat-header-avatar">
                {otherUser.display_name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3>{otherUser.display_name}</h3>
                <span className="chat-header-score">{Math.round(compatScore)}% compatible</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && prompts.length > 0 && (
          <div className="chat-prompts">
            <p className="chat-prompts-title">Start the conversation:</p>
            {prompts.slice(0, 4).map((prompt, i) => (
              <button
                key={i}
                className="chat-prompt-btn"
                onClick={() => handlePromptClick(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg) => {
          const isMine = msg.sender_id === user.id;
          return (
            <div key={msg.id} className={`chat-bubble ${isMine ? 'sent' : 'received'}`}>
              {msg.message_type === 'song_share' && msg.song_data ? (
                <div className="song-share-card">
                  <div className="song-share-art">
                    {msg.song_data.image_url ? (
                      <img src={msg.song_data.image_url} alt={msg.song_data.track_name} />
                    ) : (
                      <div className="song-art-placeholder">♪</div>
                    )}
                  </div>
                  <div className="song-share-info">
                    <span className="song-share-name">{msg.song_data.track_name}</span>
                    <span className="song-share-artist">{msg.song_data.artist}</span>
                    {msg.song_data.album && (
                      <span className="song-share-album">{msg.song_data.album}</span>
                    )}
                  </div>
                </div>
              ) : (
                <p>{msg.content}</p>
              )}
              <span className="chat-time">
                {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-bar" onSubmit={handleSend}>
        <button
          type="button"
          className="chat-song-btn"
          onClick={() => setShowSongSearch(true)}
          title="Share a song"
        >
          ♪
        </button>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
        />
        <button type="submit" className="chat-send-btn" disabled={!input.trim() || sending}>
          →
        </button>
      </form>

      {showSongSearch && (
        <SongSearchModal
          onSelect={handleSongShare}
          onClose={() => setShowSongSearch(false)}
        />
      )}
    </div>
  );
}
