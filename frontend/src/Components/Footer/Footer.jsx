import React from "react";
import {
    Box,
    FooterContainer,
    Row,
    Column,
    FooterLink,
    Heading,
    Img,
    LogoContainer
} from "./FooterStyles";
import logo from "../../assets/Logo.png"

const Footer = () => {
    return (
        <Box>
            <LogoContainer>
               <Img src={logo} alt="MusicMate_logo" />
                <h1
                    style={{
                        color: "#8a6fe8",
                        textAlign: "left",
                        marginTop: "10px",
                        marginLeft: "10px",
                        marginBottom: "5px",
                    }}
                >
                    MusicMate <sup>&copy;</sup>
                </h1> 
            </LogoContainer>
            
            <p>Find your University Buddies</p>
            
            <FooterContainer>
                <Row>
                    <Column column={5}>
                        <Heading>About Us</Heading>
                        <FooterLink href="#">
                            Blog
                        </FooterLink>
                        <FooterLink href="#">
                            Case Studies
                        </FooterLink>
                        <FooterLink href="#">
                            Customer Stories
                        </FooterLink>
                    </Column>
                    <Column column={6}>
                        <Heading>Contact Us</Heading>
                        <FooterLink href="#">
                            Email
                        </FooterLink>
                        <FooterLink href="#">
                            Instagram
                        </FooterLink>
                        <FooterLink href="#">
                            Linkedin
                        </FooterLink>
                        <FooterLink href="#">
                            Facebook
                        </FooterLink>
                    </Column>
                </Row>
            </FooterContainer>
        </Box>
    );
};
export default Footer;