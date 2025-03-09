import { Card, Container } from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css';


export default function CarSummary(props) {
	return <Card>
		<a href={props.url}><img aspect-ratio="1/1" alt={props.title}src={props.image}/></a>

		<Container>
			<a href={props.url}><h5>{props.title}</h5></a>
			<h6>{props.subtitle}</h6>
			<h6>{props.price}</h6>
			<p>{props.time}</p>
		</Container>
	</Card>
}