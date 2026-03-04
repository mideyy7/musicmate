import styles from "./Feed.module.css";
import { useNavigate } from "react-router-dom";
function Posts(){
    const navigate = useNavigate();
    return(
        <>
        <div className={styles.posts}>
            <img src="https://placehold.co/550x550" alt="UserPost" />
            <h1>See Posts</h1>
            <h2>Author Name Here</h2>
            <h4>Dates here</h4>
            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Nam culpa asperiores rem ut et natus sed dolorem, quis deleniti placeat cum dicta, laboriosam aliquam accusantium minus unde esse ea dolore! Lorem ipsum dolor sit amet consectetur adipisicing elit. Maiores recusandae magni molestiae eveniet illum suscipit inventore velit temporibus facilis ea, veniam consequuntur minus tempore nihil reprehenderit placeat et, aliquam eum. Lorem ipsum dolor sit, amet consectetur adipisicing elit. At, nihil, tempore, earum natus eos pariatur quis illum atque saepe omnis voluptas doloremque nam quasi eligendi ut veniam repellendus culpa aperiam.l Lorem ipsum dolor, sit amet consectetur adipisicing elit. Est, animi! Suscipit nesciunt dolorum accusamus, ratione sequi eos unde eum doloremque pariatur et. Necessitatibus harum totam alias neque rerum sequi enim. Lorem ipsum dolor sit amet consectetur adipisicing elit. Quam, nobis repellendus cumque eaque consectetur sequi ratione inventore suscipit alias at adipisci. Possimus magnam voluptas, illo ea excepturi eaque enim debitis. Lorem ipsum dolor sit amet consectetur, adipisicing elit. Rerum sapiente reprehenderit fugit doloribus perferendis, pariatur excepturi nisi, molestiae ad aut soluta enim itaque at similique, obcaecati adipisci voluptates consequatur sint.</p>
            <div className={styles.btn}>
                <button className={styles.see_btn} onClick={() => navigate("/Friends")}>Connect</button>
            </div>
        </div>
        </>
    )
}

export default Posts