import React from "react";
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";
import styles from "./Feed.module.css"

function Feed(){
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
                            <h1>See Feed</h1>
                            <h3>Some descriptions</h3>
                        </div>
                    </div>
                    
                </Main>
                <Footer />
            </AppContainer>
        </>
    );
}

export default Feed