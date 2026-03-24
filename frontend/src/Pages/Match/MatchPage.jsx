import { useState } from "react";
import Match from "./Match.jsx";
import SwipeCard from "./SwipeCard.jsx";
import styles from "./Match.module.css"
import friendList from "./friendList.json"
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";

const friendsList = friendList

function MatchPage
() {
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
    <>
      <AppContainer>
        <Main>
          <div style={pageStyles}>
            <div className={styles.card_wrapper}>
              <button className={styles.match_btn} id={styles.reject} onClick={handleReject}>×</button>
              <SwipeCard
                key={friend.id}  
                onSwipedLeft={handleReject}
                onSwipedRight={handleAccept}
              >
                <Match friend={friend} />
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
        </Main>
        
        <Footer />
      </AppContainer>

    </>
  );
}

export default MatchPage
