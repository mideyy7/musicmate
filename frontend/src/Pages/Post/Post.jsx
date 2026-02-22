import React from "react";
import Footer from "../../Components/Footer/Footer";
import { AppContainer, Main } from "../PageContainer";
function Post(){
    return(
        <>
            <AppContainer>
                <Main>
                    <div><h1>This is the Post page</h1></div>
                </Main>
                <Footer />
            </AppContainer>
        </>
    );
}

export default Post