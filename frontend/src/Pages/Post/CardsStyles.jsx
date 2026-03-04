import styled from "styled-components";

export const Box = styled.div`
    padding: 5% 2.5%;
    background: #ffffff34;
    // position: absolute;
    bottom: 0;
    width: 95%;

    @media (max-width: 1000px) {
        // padding: 70px 30px;
    }
`;

export const Container = styled.div`
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
    margin-left: 0px;
    grid-column: ${({ column }) => column || 'auto'};
`;

export const Row = styled.div`
    display: grid;
    grid-template-columns: repeat(
        2,
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

export const Link = styled.a`
    color: #fff;
    margin-bottom: 20px;
    font-size: 15px;
    text-decoration: none;
    display: flex;
    justify-content: center;

    &:hover {
        color: #735ac4;
        transition: 200ms ease-in;
    }
`;

export const Heading = styled.p`
    font-size: 18px;
    color: #fff;
    margin-bottom: 5px;
    font-weight: bold;
`;

export const Img = styled.img`
    height: 250px;
    width: 350px;    
    display: inline;
`;

export const LogoContainer = styled.div`
    display: flex;
    align-items: center;
`;