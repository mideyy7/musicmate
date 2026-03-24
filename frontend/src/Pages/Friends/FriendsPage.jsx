import { useState } from "react";
import Friends from "./Friends.jsx";
import SwipeCard from "./SwipeCard.jsx";
import styles from "./Friends.module.css"
import friendList from "./friendList.json"

const friendsList = friendList

function FriendsPage() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const pageStyles = {
    minHeight: "80vh",
    display: "grid",
    placeItems: "center",
    padding: "24px",
  }

  const handleReject = () => {console.log("Pass");
                              setCurrentIndex((prev) => prev + 1);
                            };
  const handleAccept = () => {console.log("Smash");
                              setCurrentIndex((prev) => prev + 1);
                            };

  if (currentIndex >= friendsList.length) {
    return (
      <div style={pageStyles}>
        <h2 style={{ color: "#fff" }}>No more friends to show, you know everyone in this University🎉</h2>
      </div>
    );
  }
  const friend = friendsList[currentIndex];

  return (
    <div style={pageStyles}>
      <div className={styles.card_wrapper}>
        <button className={styles.match_btn} id={styles.reject} onClick={handleReject}>×</button>
        <SwipeCard
          key={friend.id}  
          onSwipedLeft={handleReject}
          onSwipedRight={handleAccept}
        >
          <Friends friend={friend} />
        </SwipeCard>
        <button
          className={styles.match_btn}
          id={styles.accept}
          onClick={handleAccept}
        >
          ✓
        </button>
      </div>
    </div>
  );
}

export default FriendsPage