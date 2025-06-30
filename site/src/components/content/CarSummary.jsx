import { Card } from "react-bootstrap";
import '../../index.css'
import 'bootstrap/dist/css/bootstrap.min.css';


export default function CarSummary(props) {

	function formatTimeLeft(endTime) {
		const end = new Date(endTime);
		const now = new Date();
		let diff = Math.max(0, Math.floor((end - now) / 1000)); // in seconds

		const days = Math.floor(diff / (24 * 3600));
		diff %= 24 * 3600;
		const hours = Math.floor(diff / 3600);
		diff %= 3600;
		const minutes = Math.floor(diff / 60);

		if (days > 0) return `${days} day${days > 1 ? 's' : ''}`;
		else if (hours > 0) return `${hours.toString()}h ${minutes.toString()}m`;
		else return `${minutes.toString()}m`;
	}

	return <Card>
		<Card.Img className="rounded-1" variant="top" src={props.image} />
		<Card.Body>
			<Card.Title>
				<a href={props.url} rel="noopener noreferrer" target="_blank">{props.title}</a>
			</Card.Title>
			<Card.Text>
				Current Bid: <strong>{props.price ? props.price : "No Bids"}</strong>
				<br />
				Time left: <strong>{formatTimeLeft(props.time)}</strong>
			</Card.Text>
		</Card.Body>
	</Card>
}