import React from "react";
import logo from "../../assets/Logo.png";
import styles from "./Friends.module.css"
function Friends(){
    return (
        <>
        <div className={`${styles.main_con} ${styles.swipeInRight}`}>
            <div className={styles.profile_con}>
                <img src={logo} alt="profilePhoto" style={{width: "150px", height: "150px", bordeRadius: "5%"}}/>
            </div>
            <div className={styles.user_con}>
                <div className={styles.name_con}><h2>Username</h2></div>
                <div className={styles.subtitle_con}><h3>UserSub</h3></div>
                <div className={styles.description_con}>
                    <p>
                        Lorem ipsum dolor sit amet consectetur adipisicing elit. Aspernatur suscipit id dignissimos debitis velit deleniti.
                        </p>
                </div>
            </div>
            <div className={styles.tag_con}>
                <div className={styles.item}>tag1</div>
                <div className={styles.item}>tag1</div>
                <div className={styles.item}>tag1</div>
            </div>
            
        </div>
        </>
    );
}

export default Friends