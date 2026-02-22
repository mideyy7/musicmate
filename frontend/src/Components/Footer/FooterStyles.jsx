import styled from "styled-components";

export const Box = styled.div`
    padding: 5% 2.5%;
    background: black;
    // position: absolute;
    bottom: 0;
    width: 95%;

    @media (max-width: 1000px) {
        // padding: 70px 30px;
    }
`;

export const FooterContainer = styled.div`
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-width: 10000px;
    margin: 0 auto;
`;

export const Column = styled.div`
    display: flex;
    flex-direction: column;
    text-align: left;
    margin-left: 60px;
    grid-column: ${({ column }) => column || 'auto'};
`;

export const Row = styled.div`
    display: grid;
    grid-template-columns: repeat(
        6,
        minmax(185px, 1fr)
    );
    grid-gap: 20px;

    @media (max-width: 1000px) {
        grid-template-columns: repeat(
            auto-fill,
            minmax(200px, 1fr)
        );
    }
`;

export const FooterLink = styled.a`
    color: #fff;
    margin-bottom: 20px;
    font-size: 15px;
    text-decoration: none;

    &:hover {
        color: #735ac4;
        transition: 200ms ease-in;
    }
`;

export const Heading = styled.p`
    font-size: 18px;
    color: #fff;
    margin-bottom: 40px;
    font-weight: bold;
`;

export const Img = styled.img`
    height: 60px;
    width: 60px;    
    display: inline;
`;

export const LogoContainer = styled.div`
    display: flex;
    align-items: center;
`;