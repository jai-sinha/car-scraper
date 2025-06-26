import { Card } from "react-bootstrap";
import '../../index.css'
import 'bootstrap/dist/css/bootstrap.min.css';


export default function CarSummary(props) {

	return <Card>
		<Card.Img className="rounded-1" variant="top" src={props.image} />
		<Card.Body>
			<Card.Title>
				<a href={props.url} rel="noopener noreferrer" target="_blank">{props.title}</a>
			</Card.Title>
			<Card.Text>
				Current Bid: <strong>{props.price ? props.price : "No Bids"}</strong>
				<br />
				Time left: <strong>{props.time}</strong>
			</Card.Text>
		</Card.Body>
	</Card>
}