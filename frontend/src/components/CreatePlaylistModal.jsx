import { useEffect, useState } from 'react';
import { getMatches, createPlaylist } from '../services/api';

export default function CreatePlaylistModal({ onClose, onCreate }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [matches, setMatches] = useState([]);
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMatches();
  }, []);

  async function loadMatches() {
    try {
      const data = await getMatches();
      setMatches(data);
    } catch {
      // ignore
    }
  }

  function toggleMember(userId) {
    setSelectedMembers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  }

  async function handleCreate() {
    if (!name.trim()) {
      setError('Please enter a playlist name.');
      return;
    }
    setCreating(true);
    setError('');
    try {
      await createPlaylist({
        name: name.trim(),
        description: description.trim() || null,
        member_ids: selectedMembers,
      });
      onCreate();
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content create-playlist-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create Group Playlist</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Playlist Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Study Vibes, Road Trip Mix"
          />
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What's this playlist about?"
          />
        </div>

        <div className="form-group">
          <label>Add Members from Matches</label>
          {matches.length === 0 ? (
            <p className="text-muted">No matches yet to add.</p>
          ) : (
            <div className="member-select-list">
              {matches.map((match) => (
                <div
                  key={match.other_user.id}
                  className={`member-select-item ${
                    selectedMembers.includes(match.other_user.id) ? 'selected' : ''
                  }`}
                  onClick={() => toggleMember(match.other_user.id)}
                >
                  <span className="member-select-avatar">
                    {match.other_user.display_name.charAt(0).toUpperCase()}
                  </span>
                  <span className="member-select-name">
                    {match.other_user.display_name}
                  </span>
                  <span className="member-select-check">
                    {selectedMembers.includes(match.other_user.id) ? '✓' : ''}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          className="btn-primary"
          onClick={handleCreate}
          disabled={creating || !name.trim()}
        >
          {creating ? 'Creating...' : 'Create Playlist'}
        </button>
      </div>
    </div>
  );
}
