import { Card } from "react-bootstrap";
import { FaStar } from "react-icons/fa";
import { useSavedListings } from "../contexts/SavedContext";
import '../../index.css';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function CarSummary(props) {
	const { isSaved, addSaved, removeSaved } = useSavedListings();
	const saved = isSaved(props.url);

	function formatTimeLeft(endTime) {
		if (endTime == "N/A") return "N/A";
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

	async function handleSave(e) {
		e.preventDefault();
		if (saved) {
			await removeSaved(props.url);
		} else {
			console.log(`Removed ${props.title} from garage`);
			await addSaved(props.url);
		}
	}

	return (
	  <a
			href={props.url}
			target="_blank"
			rel="noopener noreferrer"
			className="text-decoration-none text-dark"
			style={{ display: "block" }}
		>
			<Card className="position-relative">
				<div style={{ position: "relative" }}>
					<Card.Img
						className="rounded-1"
						variant="top"
						src={props.image}
						style={{ width: "100%", height: "auto", display: "block" }}
					/>
					<FaStar
						onClick={handleSave}
						style={{
						position: "absolute",
						top: "8%",
						right: "8%",
						cursor: "pointer",
						fontSize: "clamp(1.25em, 2vw, 1.75em)",
						color: saved ? "gold" : "#fff",
						stroke: "black",
						strokeWidth: 35,
						zIndex: 2,
						transition: "color 0.2s, filter 0.2s"
						}}
						title={saved ? "Remove from Garage" : "Save to Garage"}
					/>
				</div>
				<Card.Body>
					<Card.Title>
						<h4 className="fw-semibold">
							{props.title}
						</h4>
					</Card.Title>
					<Card.Text>
						Current Bid: <strong>{props.price ? props.price : "No Bids"}</strong>
						<br />
						Time left: <strong>{formatTimeLeft(props.time)}</strong>
					</Card.Text>
				</Card.Body>
			</Card>
		</a>
	);
}