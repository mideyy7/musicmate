import SignUp from "./Pages/SignUp/SignUp.jsx"
import SignIn from './Pages/SignIn/SignIn.jsx'
import Match from './Pages/Match/Match.jsx'
import FriendsPage from './Pages/Friends/FriendsPage.jsx'
import Post from './Pages/Post/Post.jsx'
import Feed from './Pages/Feed/Feed.jsx'
import Home from './Pages/index/index.jsx'
import TestPage from './Pages/Testpage/TestPage.jsx'
import NavBar from "./Components/NavBar/NavBar.jsx";
import {BrowserRouter as Router, Routes, Route,} from "react-router-dom";
function App() {

  return (
    <>
      <Router>
            <NavBar />
            <Routes>
                <Route exact path="/index" element={<Home />} />
                <Route path="/Match" element={<Match />} />
                <Route path="/FriendsPage" element={<FriendsPage />} />
                <Route path="/Post" element={<Post />} />
                <Route path="/Feed" element={<Feed />} />
                <Route path="/SignUp" element={<SignUp />} />
                <Route path="/TestPage" element={<TestPage />} />
                <Route path="/SignIn" element={<SignIn />} />
                

            </Routes>
        </Router>
  
    </>
  )
}

export default App
