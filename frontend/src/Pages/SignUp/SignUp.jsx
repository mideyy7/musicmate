import { useState } from 'react';
import styles from './SignUp.module.css';
import loginWithSpotify from "./Spotify";
import loginWithUni from "./University";
import { Link } from "react-router-dom";

export default function SignUp() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [focusedField, setFocusedField] = useState({
    username: false,
    email: false,
    password: false,
    confirmPassword: false
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFocus = (field) => {
    setFocusedField(prev => ({ ...prev, [field]: true }));
  };

  const handleBlur = (field) => {
    setFocusedField(prev => ({ ...prev, [field]: false }));
  };

  const isActive = (field) => focusedField[field] || formData[field].length > 0;

  const successMessage = () => {
        return (
            <div
                className="success"
                style={{
                    display: submitted ? "" : "none",
                }}
            >
                <h1>User {username} successfully registered!!</h1>
            </div>
        );
    };

    // Showing error message if error is true
    const errorMessage = () => {
        return (
            <div
                className="error"
                style={{
                    display: error ? "" : "none",
                }}
            >
                <h1>Please enter all the fields</h1>
            </div>
        );
    };


  return (
    <div className={styles.page}>
      <form className={styles.main_con} method="post" action="./Authenticator.php">
        <div className={styles.create_container}>
          <h3>Create Account</h3>
          <h2>Sign up to get started</h2>
          
          <div className={styles.entryArea}>
            <input
              type="text"
              id="username"
              value={formData.username}
              onChange={(e) => handleChange('username', e.target.value)}
              onFocus={() => handleFocus('username')}
              onBlur={() => handleBlur('username')}
              required
              className={isActive('username') ? `${styles.animatedInput} ${styles.active}` : styles.animatedInput}
            />
            <div className={isActive('username') ? `${styles.labelLine} ${styles.labelActive}` : styles.labelLine}>
              Username
            </div>
          </div>

          <div className={styles.entryArea}>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              onFocus={() => handleFocus('email')}
              onBlur={() => handleBlur('email')}
              required
              className={isActive('email') ? `${styles.animatedInput} ${styles.active}` : styles.animatedInput}
            />
            <div className={isActive('email') ? `${styles.labelLine} ${styles.labelActive}` : styles.labelLine}>
              Email
            </div>
          </div>

          <div className={styles.entryArea}>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              onFocus={() => handleFocus('password')}
              onBlur={() => handleBlur('password')}
              required
              className={isActive('password') ? `${styles.animatedInput} ${styles.active}` : styles.animatedInput}
            />
            <div className={isActive('password') ? `${styles.labelLine} ${styles.labelActive}` : styles.labelLine}>
              Password
            </div>
          </div>

          <div className={styles.entryArea}>
            <input
              type="password"
              id="confirmPassword"
              value={formData.confirmPassword}
              onChange={(e) => handleChange('confirmPassword', e.target.value)}
              onFocus={() => handleFocus('confirmPassword')}
              onBlur={() => handleBlur('confirmPassword')}
              required
              className={isActive('confirmPassword') ? `${styles.animatedInput} ${styles.active}` : styles.animatedInput}
            />
            <div className={isActive('confirmPassword') ? `${styles.labelLine} ${styles.labelActive}` : styles.labelLine}>
              Confirm Password
            </div>
          </div>

          <button className={styles.button} id={styles.signup}>
            Sign Up
          </button>
          
          <div className={styles.accLogin}>
            <p id={styles.account}>Already have an account?<Link to="/SignIn" id={styles.hyperlink}>Log In</Link></p>
          </div>



          <div className={styles.otherSignIn}>
            <button className={styles.uniSignIn} onClick="http://studentnet.cs.manchester.ac.uk/authenticate/?url=http://localhost:5173/&csticket=CSTICKET&version=3&command=validate">University</button>
            <button className={styles.spotifySignIn} onClick={loginWithSpotify}>Spotify</button>
          </div>


        </div>
      </form>
    </div>
  );
}
