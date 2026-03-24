import React, { useState } from "react";
import ProfileCard from "./ProfileCard";
import ChatPage from "./ChatPage";
import Feed from "./Feed";

const App = () => {
  const [activeTab, setActiveTab] = useState("pulse");

  // 简单的顶部导航栏样式
  const navStyle = {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
    padding: "20px",
    background: "#0f0c29",
    borderBottom: "1px solid rgba(255,255,255,0.1)",
  };

  const btnStyle = (isActive) => ({
    background: isActive ? "#8c67ef" : "rgba(255, 255, 255, 0.1)",
    color: "white",
    border: "none",
    padding: "10px 20px",
    borderRadius: "20px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "0.3s",
  });

  return (
    <div>
      {/* top navigation */}
      <nav style={navStyle}>
        <button
          style={btnStyle(activeTab === "feed")}
          onClick={() => setActiveTab("feed")}
        >
          Feed
        </button>
        <button
          style={btnStyle(activeTab === "chat")}
          onClick={() => setActiveTab("chat")}
        >
          Chat Page
        </button>
        <button
          style={btnStyle(activeTab === "profile")}
          onClick={() => setActiveTab("profile")}
        >
          Profile
        </button>
      </nav>

      {/* page */}
      <div>
        {activeTab === "feed" && <Feed />}
        {activeTab === "chat" && <ChatPage />}
        {activeTab === "profile" && <ProfileCard />}
      </div>
    </div>
  );
};

export default App;
