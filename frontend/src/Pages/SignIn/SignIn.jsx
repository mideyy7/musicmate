import { useState } from "react";
import styles from "./SignIn.module.css"

function SignIn (){
    const [formData, setFormData] = useState({
        username: '',
        password: '',
      });
    
      const [focusedField, setFocusedField] = useState({
        username: false,
        password: false,
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
    return (
        <div className={styles.page}>
              <form className={styles.main_con} method="post" action="./Authenticator.php">
                <div className={styles.create_container}>
                  <h3>Sign In</h3>
                  <h2>Sign in to continue</h2>
                  
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
                  <button className={styles.button} id={styles.signup}>
                              Sign In
                            </button>
                </div>
            </form>
        </div>        
        );
}
export default SignIn