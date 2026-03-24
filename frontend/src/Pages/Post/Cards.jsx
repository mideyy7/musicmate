import {
    Box,
    Container,
    Row,
    Column,
    Link,
    Heading,
    Img,
} from "./CardsStyles";

const Cards = () => {

    return (
        <Box>
            <h1 
            style={{
                        color: "#FFFFFF",
                        textAlign: "left",
                        marginTop: "10px",
                        marginLeft: "10px",
                        marginBottom: "5px",
                    }}>
                        See what others like
            </h1>
            <Container>
                <Row>
                    <Column column={1}>
                        <Heading>UserName1</Heading>
                        <Link href="#">
                            <Img src="https://placehold.co/350x250" alt="Other Posts"></Img>
                        </Link>
                    </Column>
                    <Column column={2}>
                        <Heading>UserName2</Heading>
                        <Link href="#">
                            <Img src="https://placehold.co/350x250" alt="Other Posts"></Img>
                        </Link>
                    </Column>
                </Row>
                <Row>
                    <Column column={1}>
                        <Heading>UserName1</Heading>
                        <Link href="#">
                            <Img src="https://placehold.co/350x250" alt="Other Posts"></Img>
                        </Link>
                    </Column>
                    <Column column={2}>
                        <Heading>UserName2</Heading>
                        <Link href="#">
                            <Img src="https://placehold.co/350x250" alt="Other Posts"></Img>
                        </Link>
                    </Column>
                </Row>
            </Container>
        </Box>
    );
};
export default Cards;