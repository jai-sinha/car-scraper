import { Card } from "react-bootstrap";
import '../index.css'
import 'bootstrap/dist/css/bootstrap.min.css';


export default function CarSummary(props) {

	return <Card>
		<Card.Img className="rounded-1" variant="top" src={props.image} />
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