import React, { useState, useEffect } from "react";
import "./ProfileCard.css";

//default display
const ProfileCard = () => {
  const [profile, setProfile] = useState({
    username: "",
    course: "",
    year: "Year 1",
    password: " ",
    avatarUrl: null,
  });

  //the modified part displayed at the top
  const [displayInfo, setDisplayInfo] = useState({
    name: "",
    course: "Course",
    year: "Year",
  });

  useEffect(() => {
    setDisplayInfo({
      name: profile.username,
      course: profile.course || "Course",
      year: profile.year,
    });
  }, [profile]);

  //avatar upload
  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setProfile((prev) => ({ ...prev, avatarUrl: imageUrl }));
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  //username change
  const getInitials = () => {
    if (!profile.username) return "";
    const words = profile.username.trim().split(" ");
    let initials = words[0].charAt(0);
    if (words.length > 1) {
      initials += words[words.length - 1].charAt(0);
    }
    return initials.toUpperCase();
  };

  //password changge
  const handleChangePassword = () => {
    const newPassword = prompt("Please enter the new password:");
    if (newPassword) {
      alert("The password has been modified successfully!");
    }
  };

  return (
    <div className="profile_page_container">
      <div className="profile_card">
        <header className="card_header">
          {}
          <label
            htmlFor="avatar_input"
            className="avatar_upload"
            style={{
              backgroundImage: profile.avatarUrl
                ? `url(${profile.avatarUrl})`
                : "none",
            }}
          >
            {!profile.avatarUrl && (
              <span id="avatar_text">{getInitials()}</span>
            )}
            <input
              type="file"
              id="avatar_input"
              accept="image/*"
              hidden
              onChange={handleAvatarChange}
            />
          </label>

          {}
          <div className="header_info">
            <input
              type="text"
              className="input_title"
              value={displayInfo.name}
              readOnly
              placeholder="Name will appear here"
            />
            <div className="header_sublime">
              <span>{displayInfo.course}</span>
              <span>{displayInfo.year}</span>
            </div>
          </div>
        </header>

        {}
        <section>
          <div className="section_title">Account Settings</div>
          <div className="grid_container">
            <div className="input_group">
              <label>User Name</label>
              <input
                type="text"
                name="username"
                value={profile.username}
                onChange={handleInputChange}
              />
            </div>
            <div className="input_group">
              <label>User ID</label>
              <input type="text" />
            </div>
            <div className="input_group">
              <label>Email (Read Only)</label>
              <input type="email" readOnly value="user@example.com" />
            </div>
            <div className="input_group">
              <label>Password</label>
              <button className="btn_change" onClick={handleChangePassword}>
                Change Password
              </button>
            </div>
          </div>
        </section>

        {}
        <section>
          <div className="section_title">Public Profile</div>
          <div className="grid_container">
            <div className="input_group">
              <label>Profile Picture</label>
              {}
              <input
                type="file"
                style={{ padding: "8px" }}
                onChange={handleAvatarChange}
              />
            </div>
            <div className="input_group">
              <label>Course Studying</label>
              <input
                type="text"
                name="course"
                value={profile.course}
                onChange={handleInputChange}
              />
            </div>
            <div className="input_group">
              <label>Year in University</label>
              <select
                name="year"
                value={profile.year}
                onChange={handleInputChange}
              >
                <option value="foundation year">foundation year</option>
                <option value="Year 1">Year 1</option>
                <option value="Year 2">Year 2</option>
                <option value="Year 3">Year 3</option>
                <option value="Year 4">Year 4</option>
                <option value="Year 5">Year 5</option>
              </select>
            </div>
            <div className="input_group">
              <label>Hobbies</label>
              <input type="text" placeholder="e.g. Gaming, Football, Chess" />
            </div>
            <div className="footer_actions">
              <button
                className="btn_save"
                onClick={() => alert("Changes Saved!")}
              >
                Save Changes
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ProfileCard;
