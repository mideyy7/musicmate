import React from "react";
import styles from "./index.module.css";
import { useNavigate } from "react-router-dom";
import Footer from "../../Components/Footer/Footer";
import Cards from "./Cards";
import Posts from "./Posts";
import Messaging from "./Messaging";
import { AppContainer, Main } from "../PageContainer";
import bg from "../../assets/Background.png";

function Home(){
    const navigate = useNavigate();
    return(
        <>
            <AppContainer>
                <Main>
                    <div className={styles.top_layer}
                        style={{
                            backgroundImage: `url(${bg})`,
                            backgroundSize: "cover",
                            backgroundPosition: "center",
                            backgroundRepeat: "no-repeat",
                            height: "100vh",
                            objectFit: "cover",
                            overflow: "hidden",
                            width: "100%"
                        }}
                    >
                        <div className={styles.title}>
                            <h1>MusicMate</h1>
                            <h3>Find your University Buddies</h3>
                        </div>
                        <div className={styles.btns}>
                            <button className={styles.make_friend} onClick={() => navigate("/Friends")}> Make Friends</button>
                            <button className={styles.learn_more} onClick={() => navigate("/")}>Learn More</button>
                        </div>
                        <Cards />
                    </div>
                    

                    
                    <Posts />
                    <Messaging />
                </Main>

                <Footer />
            </AppContainer>


            
        </>
    );
}

export default Home
