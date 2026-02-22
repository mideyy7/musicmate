import SignUp from "./Pages/SignUp/SignUp.jsx"
import SignIn from './Pages/SignIn/SignIn.jsx'
import MatchPage from './Pages/Match/MatchPage.jsx'
import Friends from './Pages/Friends/Friends.jsx'
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
                <Route path="/MatchPage" element={<MatchPage />} />
                <Route path="/Friends" element={<Friends />} />
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
