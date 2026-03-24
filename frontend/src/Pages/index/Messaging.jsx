import styles from "./index.module.css";
import { useNavigate } from "react-router-dom";

function Messaging(){
    const navigate = useNavigate();
    return(
        <>
            <div className={styles.messaging}>
                        <img src="https://placehold.co/550x350" alt="UserPost" />
                        <h1>Messaging</h1>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Nam culpa asperiores rem ut et natus sed dolorem, quis deleniti placeat cum dicta, laboriosam aliquam accusantium minus unde esse ea dolore! Lorem ipsum dolor sit amet consectetur adipisicing elit. Maiores recusandae magni molestiae eveniet illum suscipit inventore velit temporibus facilis ea, veniam consequuntur minus tempore nihil reprehenderit placeat et, aliquam eum. Lorem ipsum dolor sit, amet consectetur adipisicing elit. At, nihil, tempore, earum natus eos pariatur quis illum atque saepe omnis voluptas doloremque nam quasi eligendi ut veniam repellendus culpa aperiam.</p>
                        <button className={styles.message_btn} onClick={() => navigate("/Friends")}>Message</button>
                    </div>
        </>
    );
}

export default Messaging