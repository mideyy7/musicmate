import React from "react";
import styles from "./Friends.module.css"
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";
function Friends(){
    return (
        <>
            <AppContainer>
                <Main>
                    <div><h1>This is the Friend page</h1></div>
                </Main>
                <Footer />
            </AppContainer>

        </>
    );
}

export default Friends