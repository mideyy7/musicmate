import React from "react";
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";

function Feed(){
    return(
        <>
            <AppContainer>
                <Main>
                    <div><h1>This is the Feed page</h1></div>
                </Main>
                <Footer />
            </AppContainer>
        </>
    );
}

export default Feed