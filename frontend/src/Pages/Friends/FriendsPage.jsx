import Friends from "./Friends.jsx";
import SwipeCard from "./SwipeCard.jsx";

function FriendsPage() {
  const styles = {
    minHeight: "80vh",
    display: "grid",
    placeItems: "center",
    padding: "24px",
  }
  return (
    <div style={styles}>
      <SwipeCard
        onSwipedLeft={() => console.log("Nope")}
        onSwipedRight={() => console.log("Like")}
      >
        <Friends />
      </SwipeCard>
    </div>
  );
}

export default FriendsPage