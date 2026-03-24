function Spotify(){
    const CLIENT_ID = "";
    const REDIRECT_URI = "http://localhost:5173/";
    const SCOPES = [
    "user-read-email",
    "user-read-private"
    ];

    function loginWithSpotify() {
    const authUrl =
        "https://accounts.spotify.com/authorize" +
        "?response_type=token" +
        "&client_id=" + CLIENT_ID +
        "&scope=" + encodeURIComponent(SCOPES.join(" ")) +
        "&redirect_uri=" + encodeURIComponent(REDIRECT_URI);

    window.location.href = authUrl;
    }
    return loginWithSpotify
}

export default Spotify