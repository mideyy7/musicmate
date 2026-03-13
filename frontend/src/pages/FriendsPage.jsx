import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getMatches, getUnreadCount, getConversation, sendMessage, markAsRead, getChatPrompts } from '../services/api';
import SongSearchModal from '../components/SongSearchModal';
import NavBar from '../components/NavBar';

export default function FriendsPage() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [matches, setMatches] = useState([]);
  const [unreadByMatch, setUnreadByMatch] = useState({});
  const [selectedMatchId, setSelectedMatchId] = useState(matchId ? parseInt(matchId) : null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [prompts, setPrompts] = useState([]);
  const [showSongSearch, setShowSongSearch] = useState(false);

  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    loadMatches();
    loadUnread();
  }, []);

  useEffect(() => {
    if (selectedMatchId) {
      navigate(`/friends/${selectedMatchId}`, { replace: true });
      loadMessages(selectedMatchId);
      loadPrompts();

      clearInterval(pollRef.current);
      pollRef.current = setInterval(() => loadMessages(selectedMatchId), 3000);
    }
    return () => clearInterval(pollRef.current);
  }, [selectedMatchId, navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function loadMatches() {
    try {
      const data = await getMatches();
      setMatches(data);
    } catch { /* ignore */ }
  }

  async function loadUnread() {
    try {
      const data = await getUnreadCount();
      setUnreadByMatch(data.by_match || {});
    } catch { /* ignore */ }
  }

  async function loadMessages(mid) {
    try {
      const data = await getConversation(mid);
      setMessages(data);
      await markAsRead(mid);
      setUnreadByMatch(prev => ({ ...prev, [mid]: 0 }));
    } catch { /* ignore */ }
    finally { setLoadingMessages(false); }
  }

  async function loadPrompts() {
    try {
      const data = await getChatPrompts();
      setPrompts(data.prompts || []);
    } catch { /* ignore */ }
  }

  async function handleSend(e) {
    e?.preventDefault();
    if (!input.trim() || sending || !selectedMatchId) return;
    setSending(true);
    try {
      const msg = await sendMessage(selectedMatchId, { content: input.trim(), message_type: 'text' });
      setMessages(prev => [...prev, msg]);
      setInput('');
    } catch { /* ignore */ }
    finally { setSending(false); }
  }

  async function handleSongShare(songMessage) {
    setShowSongSearch(false);
    if (!selectedMatchId) return;
    setSending(true);
    try {
      const msg = await sendMessage(selectedMatchId, songMessage);
      setMessages(prev => [...prev, msg]);
    } catch { /* ignore */ }
    finally { setSending(false); }
  }

  function selectMatch(mid) {
    setMessages([]);
    setLoadingMessages(true);
    setSelectedMatchId(mid);
  }

  const selectedMatch = matches.find(m => m.id === selectedMatchId);

  function getLastMessage(match) {
    // We don't store last message per match client-side, show score as fallback
    return `${Math.round(match.compatibility_score)}% compatible`;
  }

  function getAvatar(u) {
    if (u?.profile_picture) return <img src={u.profile_picture} alt={u.display_name} />;
    return (u?.display_name || '?').charAt(0).toUpperCase();
  }

  return (
    <div className="page-container" style={{ overflow: 'hidden' }}>
      <NavBar />
      <div className="friends-page">
        <div className="friends-container-card">
          {/* Sidebar */}
          <div className="friends-sidebar">
            <div className="friends-sidebar-header">Friends</div>
            <div className="friends-list">
              {matches.length === 0 ? (
                <div style={{ padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No matches yet. Start swiping!
                </div>
              ) : (
                matches.map(match => (
                  <div
                    key={match.id}
                    className={`friend-item ${selectedMatchId === match.id ? 'active' : ''}`}
                    onClick={() => selectMatch(match.id)}
                  >
                    <div className="friend-avatar">{getAvatar(match.other_user)}</div>
                    <div className="friend-info">
                      <div className="friend-name">{match.other_user.display_name}</div>
                      <div className="friend-last-msg">{getLastMessage(match)}</div>
                    </div>
                    {unreadByMatch[match.id] > 0 && (
                      <div className="friend-unread">{unreadByMatch[match.id]}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Chat Area */}
          <div className="friends-chat-area">
            {!selectedMatch ? (
              <div className="friends-chat-empty">
                <div className="friends-chat-empty-icon">💬</div>
                <span>Select a friend to start chatting</span>
              </div>
            ) : (
              <>
                {/* Chat Header */}
                <div className="friends-chat-header">
                  <div className="friend-avatar" style={{ width: 36, height: 36, fontSize: '0.9rem' }}>
                    {getAvatar(selectedMatch.other_user)}
                  </div>
                  <h3>{selectedMatch.other_user.display_name}</h3>
                  <span className="friends-chat-score">{Math.round(selectedMatch.compatibility_score)}% compatible</span>
                </div>

                {/* Messages */}
                <div className="friends-messages">
                  {loadingMessages ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                      <div className="spotify-loading-icon" style={{ margin: 0 }}></div>
                    </div>
                  ) : (
                    <>
                      {messages.length === 0 && prompts.length > 0 && (
                        <div className="chat-prompts">
                          <p className="chat-prompts-title">Start the conversation:</p>
                          {prompts.slice(0, 4).map((prompt, i) => (
                            <button key={i} className="chat-prompt-btn" onClick={() => setInput(prompt)}>
                              {prompt}
                            </button>
                          ))}
                        </div>
                      )}
                      {messages.map(msg => {
                        const isMine = msg.sender_id === user.id;
                        return (
                          <div key={msg.id} className={`chat-bubble ${isMine ? 'sent' : 'received'}`}>
                            {msg.message_type === 'song_share' && msg.song_data ? (
                              <div className="song-share-card">
                                <div className="song-share-art">
                                  {msg.song_data.image_url
                                    ? <img src={msg.song_data.image_url} alt={msg.song_data.track_name} />
                                    : <div className="song-art-placeholder">♪</div>}
                                </div>
                                <div className="song-share-info">
                                  <span className="song-share-name">{msg.song_data.track_name}</span>
                                  <span className="song-share-artist">{msg.song_data.artist}</span>
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
                    </>
                  )}
                </div>

                {/* Input Bar */}
                <form className="friends-input-bar" onSubmit={handleSend}>
                  <button type="button" className="chat-song-btn" onClick={() => setShowSongSearch(true)} title="Share a song">
                    ♪
                  </button>
                  <input
                    type="text"
                    className="friends-input"
                    placeholder="Type a message..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    disabled={sending}
                  />
                  <button type="submit" className="chat-send-btn" disabled={!input.trim() || sending}>
                    →
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>

      {showSongSearch && (
        <SongSearchModal onSelect={handleSongShare} onClose={() => setShowSongSearch(false)} />
      )}
    </div>
  );
}
