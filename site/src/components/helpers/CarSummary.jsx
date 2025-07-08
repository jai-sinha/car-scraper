import { Card } from "react-bootstrap";
import { useState } from "react";
import { FaStar } from "react-icons/fa";
import '../../index.css'
import 'bootstrap/dist/css/bootstrap.min.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function CarSummary(props) {

	const [saved, setSaved] = useState(props.initialSaved || false);

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
			try {
				const response = await fetch(`${API_URL}/delete_saved_listing`, {
					method: 'DELETE',
					headers: { 'Content-Type': 'application/json' },
					credentials: 'include',
					body: JSON.stringify({ url: props.url })
				});
				if (!response.ok) throw new Error('Failed to delete saved listing');
				setSaved(false);
				if (props.onUnsave) props.onUnsave();

			} catch (error) {
				console.error('Error deleting saved listing:', error);
				setSavedListings(true);
			}
		} else {
			try {
				const response = await fetch(`${API_URL}/save`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					credentials: 'include',
					body: JSON.stringify({
						url: props.url
					})
				});
				if (!response.ok) throw new Error('Failed to save listing');
				setSaved(true);
			} catch (error) {
				console.error('Error saving listing:', error);
				setSaved(false);
			}
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
			<Card>
				<Card.Img className="rounded-1" variant="top" src={props.image} />
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
					<FaStar
						onClick={handleSave}
						style={{
							position: "absolute",
							bottom: "10px",
							right: "10px",
							cursor: "pointer",
							fontSize: "1.7rem",
							color: saved ? "gold" : "#ccc",
							transition: "color 0.2s"
						}}
						title={saved ? "Remove from Garage" : "Save to Garage"}
					/>
				</Card.Body>
			</Card>
		</a>
	);
}