import React from "react";
import { Nav , NavMenu, NavLink} from "./NavBarElements.jsx";
import logo from "../../assets/Logo.png";
import styles from "./NavBar.module.css"
const NavBar = () => {
    return (
        <>
            <Nav>
                <span className={styles.nav_left}>
                                    <img src={logo} alt="MusicMate_Logo" />
                                    <h1>MusicMate</h1>
                                </span>
                <NavMenu>
                    <NavLink to="/index" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>Home</h1>
                    </NavLink>
                    <NavLink to="/Match" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>Match</h1>
                    </NavLink>
                    <NavLink to="/FriendsPage" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>Friends</h1>
                    </NavLink>
                    <NavLink to="/Post" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>Post</h1>
                    </NavLink>
                    <NavLink to="/Feed" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>Feed</h1>
                    </NavLink>
                    <NavLink to="/SignUp" className={({ isActive }) => (isActive ? "active" : "")}>
                        <h1>SignUp</h1>
                    </NavLink>
                </NavMenu>
            </Nav>
        </>
    );
};

export default NavBar;