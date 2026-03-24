import React, { useState } from "react";
import "./Feed.css";

const Feed = () => {
  //topsongs state
  const [topSongs] = useState([
    { id: 1, title: "DtMF", artist: "Bad Bunny", rank: 1 },
    { id: 2, title: "Man I Need", artist: "Olivia Dean", rank: 2 },
    { id: 3, title: "BAILE INOLVIDABLE", artist: "Bad Bunny", rank: 3 },
    { id: 4, title: "Golden", artist: "HUNTR/X, EJAE, AUDREY NUNA", rank: 4 },
    { id: 5, title: "Tití Me Preguntó", artist: "Bad Bunny", rank: 5 },
  ]);

  // friend's action
  const [friendActivities] = useState([
    {
      id: 1,
      name: "Sarah",
      action: "is playing...",
      song: "アイドル- yoasobi",
    },
    {
      id: 2,
      name: "David",
      action: "is playing...",
      song: "jump - blackpink",
    },
    {
      id: 3,
      name: "Emily",
      action: "is playing...",
      song: "nonsense - Sabrina Carpenter",
    },
  ]);

  //Campus idol
  const [icons] = useState([
    { id: 1, name: "Bad Bunny" },
    { id: 2, name: "Taylor Swift" },
    { id: 3, name: "Rose" },
    { id: 4, name: "Wolf Alice" },
  ]);

  //style of the tune
  const [genres] = useState([
    { name: "R&B", percent: 45 },
    { name: "Hip Hop", percent: 30 },
    { name: "Electronic", percent: 10 },
  ]);

  return (
    <div className="cp-wrapper">
      <div className="cp-container">
        {/*top title */}
        <h1 className="cp-main-title">Campus Pulse</h1>

        <div className="cp-grid">
          {/* line1: Top 50 and Genre Pulse*/}
          <div className="cp-col">
            {/* Campus Top */}
            <div className="cp-card">
              <div className="cp-card-header">
                <h3>Campus Top 50</h3>
                <span className="cp-icon">🔥</span>
              </div>
              <div className="cp-list">
                {topSongs.map((song) => (
                  <div key={song.id} className="cp-song-item">
                    <div
                      className={`cp-rank ${song.rank <= 3 ? "cp-rank-top" : ""}`}
                    >
                      {song.rank}
                    </div>
                    <div className="cp-cover-placeholder"></div>
                    <div className="cp-song-info">
                      <h4>{song.title}</h4>
                      <p>{song.artist}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Genre Pulse*/}
            <div className="cp-card cp-mt-20">
              <div className="cp-card-header">
                <h3>Genre Pulse</h3>
                <span className="cp-icon">🎸</span>
              </div>
              <div className="cp-genre-list">
                {genres.map((genre, index) => (
                  <div key={index} className="cp-genre-item">
                    <div className="cp-genre-label">
                      <span>{genre.name}</span>
                      <span>{genre.percent}%</span>
                    </div>
                    <div className="cp-progress-bar">
                      <div
                        className="cp-progress-fill"
                        style={{ width: `${genre.percent}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/*line2: Friend Favorites */}
          <div className="cp-col">
            <div className="cp-card cp-full-height">
              <div className="cp-card-header">
                <h3>Friend Favorites</h3>
                <span className="cp-icon">👥</span>
              </div>
              <div className="cp-list">
                {friendActivities.map((friend) => (
                  <div key={friend.id} className="cp-friend-item">
                    <div className="cp-avatar-placeholder"></div>
                    <div className="cp-friend-info">
                      <h4>
                        {friend.name} <span>{friend.action}</span>
                      </h4>
                      <p>{friend.song}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* line3: Campus Icons */}
          <div className="cp-col">
            <div className="cp-card cp-full-height">
              <div className="cp-card-header">
                <h3>Campus Icons</h3>
                <span className="cp-icon">🎤</span>
              </div>
              <div className="cp-icons-grid">
                {icons.map((icon) => (
                  <div key={icon.id} className="cp-icon-item">
                    <div className="cp-avatar-lg-placeholder"></div>
                    <p>{icon.name}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Feed;
