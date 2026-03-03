import React, { useState } from "react";
import "./ChatPage.css";

const ChatPage = () => {
  //friends data
  const [friends] = useState([
    {
      id: 1,
      name: "Sarah",
    },
    {
      id: 2,
      name: "David",
    },
    {
      id: 3,
      name: "Emily",
      lastMessage: "I heard the queue is huge though.",
    },
  ]);

  const [activeFriendId, setActiveFriendId] = useState(null);
  const [inputMessage, setInputMessage] = useState("");

  //message
  const [messages, setMessages] = useState({
    3: [
      { text: "Have you tried that new bubble tea place?", isMe: true },
      { text: "Not yet! Is it good?", isMe: false },
      { text: "I heard the queue is huge though.", isMe: false },
    ],
  });

  //send message
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    if (!activeFriendId) return;

    const oldMessages = messages[activeFriendId] || [];
    const newMessage = { text: inputMessage, isMe: true };
    const newMessages = [...oldMessages, newMessage];

    setMessages({
      ...messages,
      [activeFriendId]: newMessages,
    });
    setInputMessage("");
  };

  const activeFriend = friends.find((friend) => friend.id === activeFriendId);

  return (
    <div className="app-wrapper">
      <div className="chat-container">
        {/* friends list */}
        <div className="sidebar">
          <h3 className="sidebar-title">Friends</h3>
          <div className="friends-list">
            {friends.map((friend) => (
              <div
                key={friend.id}
                onClick={() => setActiveFriendId(friend.id)}
                className={`friend-item ${
                  activeFriendId === friend.id ? "active" : ""
                }`}
              >
                <img src={friend.avatar} alt={friend.name} className="avatar" />
                <div className="friend-info">
                  <span className="friend-name">{friend.name}</span>
                  <span className="friend-last-msg">{friend.lastMessage}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* chat area */}
        <div className="chat-area">
          {activeFriend ? (
            <>
              {/* top of chat */}
              <div className="chat-header">
                <img
                  src={activeFriend.avatar}
                  alt={activeFriend.name}
                  className="avatar"
                />
                <div className="header-info">
                  <h2>{activeFriend.name}</h2>
                  <span className="status-online">Online</span>
                </div>
              </div>

              {/* message list */}
              <div className="messages-container">
                {(messages[activeFriendId] || []).map((msg, index) => (
                  <div
                    key={index}
                    className={`message-wrapper ${msg.isMe ? "me" : "other"}`}
                  >
                    <div className="message-bubble">
                      {typeof msg === "string" ? msg : msg.text}
                    </div>
                  </div>
                ))}
              </div>

              {/* input area */}
              <div className="input-area-wrapper">
                <div className="input-area">
                  <input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type a message..."
                    onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  />
                  <button className="send-btn" onClick={handleSendMessage}>
                    {/* logo */}
                    <svg
                      viewBox="0 0 24 24"
                      width="18"
                      height="18"
                      fill="white"
                    >
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                    </svg>
                  </button>
                </div>
              </div>
            </>
          ) : (
            /* empty state */
            <div className="empty-chat">
              <div className="empty-header">Select a friend</div>
              <div className="empty-content">
                {/* Chat Bubbles */}
                <svg
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="rgba(255, 255, 255, 0.4)"
                >
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-3 12H7v-2h10v2zm0-3H7V9h10v2zm0-3H7V6h10v2z" />
                </svg>
                <p>Select a friend to start chatting</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
