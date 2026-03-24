import React from "react";
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";
import styles from "./Feed.module.css"
import Posts from "./Posts";
import Cards from "./Cards";

function Post(){
    return(
        <>
            <AppContainer>
                <Main>
                    <div className={styles.top_layer}
                        style={{
                            height: "100vh",
                            objectFit: "cover",
                            overflow: "hidden",
                            width: "100%"
                        }}>
                        <div className={styles.title}>
                            <h1>See Posts</h1>
                            <h3>Some descriptions</h3>
                        </div>
                    </div>
                    <Posts />
                    <Cards />
                    
                </Main>
                <Footer />
            </AppContainer>
        </>
    );
}

export default Post