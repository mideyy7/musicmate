import React from "react";
import logo from "../../assets/Logo.png";
import styles from "./Match.module.css"
function Match({ friend }){
    if (!friend) return null;
    return (
        <>
        <div className={`${styles.main_con} ${styles.swipeInRight}`}>
            <div className={styles.profile_con}>
                <img src={logo} alt="profilePhoto" style={{width: "150px", height: "150px", borderRadius: "5%"}}/>
            </div>
            <div className={styles.user_con}>
                <div className={styles.name_con}><h2>{friend.username}</h2></div>
                <div className={styles.subtitle_con}><h3>{friend.subtitle}</h3></div>
                <div className={styles.description_con}>
                    <p>{friend.description}</p>
                </div>
            </div>
            <div className={styles.tag_con}>
                {friend.tags.map((tag, i) => (<div className={styles.item} key={i}>{tag}</div>))}
            </div>
        </div>
        </>
    );
}

export default Match