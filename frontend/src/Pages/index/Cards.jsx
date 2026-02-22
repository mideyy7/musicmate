import styles from "./index.module.css";
function Cards(){
    return(
        <div className={styles.feature_pics}>
                <div className={styles.feature} id={styles.card1}>
                    <h2 className={styles.feature_head}>Match</h2>
                    <img src="https://placehold.co/250x200" alt="feature picture" className={styles.feature_img}/>
                </div>
                <div className={styles.feature} id={styles.card2}>
                    <h2 className={styles.feature_head}>Friends</h2>
                    <img src="https://placehold.co/250x200" alt="feature picture" className={styles.feature_img}/>
                </div>
                <div className={styles.feature} id={styles.card3}>
                    <h2 className={styles.feature_head}>Post</h2>
                    <img src="https://placehold.co/250x200" alt="feature picture" className={styles.feature_img}/>
                </div>
                <div className={styles.feature} id={styles.card4}>
                    <h2 className={styles.feature_head}>Feed</h2>
                    <img src="https://placehold.co/250x200" alt="feature picture" className={styles.feature_img}/>
                </div>

            </div>
    );
}

export default Cards