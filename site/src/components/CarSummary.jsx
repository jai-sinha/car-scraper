import { Card } from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css';


export default function CarSummary(props) {

	return <Card style={{margin: "0.25rem"}}>
		<Card.Img variant="top" src={props.image} />
		<Card.Body>
			<Card.Title>
				<a href={props.url} rel="noopener noreferrer" target="_blank">{props.title}</a>
			</Card.Title>
			<Card.Text>
				<p>
					{props.title.includes("DT") ? "DT Price: " : "Current Bid: "} 
					<strong>{props.price ? props.price : "No Bids"}</strong>
					<br></br> 
					{props.title.includes("DT") ? "In DT" : "Time left: "} <strong>{props.time == "DT" || props.time}</strong>
				</p>
			</Card.Text>
		</Card.Body>
	</Card>
}