import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function SpotifyCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const token = params.get("access_token");

    if (token) {
      localStorage.setItem("spotify_token", token);
      navigate("/dashboard"); // redirect to your app page
    }
  }, []);

  return <p>Logging you in...</p>;
}

export default SpotifyCallback;