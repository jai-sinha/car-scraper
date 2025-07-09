import { useState, useEffect } from "react";
import { Row, Col, Button } from "react-bootstrap";
import CarSummary from "./CarSummary";

const API_URL = import.meta.env.VITE_API_URL;
const PAGE_SIZE = 40;

function AllListings() {
	const [listings, setListings] = useState(null);
	const [minutesAgo, setMinutesAgo] = useState(null);
	const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

	const fetchListings = async () => {
		try {
			const response = await fetch(`${API_URL}/listings`);
			console.log("Fetching live listings from:", `${API_URL}/listings`);
			if (!response.ok) {
				throw new Error(`HTTP error: ${response.status}`);
			}
			const data = await response.json();
			console.log("Fetched live listings:", Object.values(data)[0]);
			setListings(data);
			const timestamp = Object.values(data)[0].scraped_at;
			calculateMins(timestamp);
		} catch (err) {
			console.error(err);
		}
	};

	useEffect(() => {
		fetchListings();
	}, []);

	const refreshListings = async () => {
		setListings(null); // Reset listings to show loading state
		setMinutesAgo(null); // Reset minutes ago to show loading state
		setVisibleCount(PAGE_SIZE);
		await fetchListings();
	};

	const calculateMins = (timestamp) => {
		// Ensure the timestamp is in a format the Date constructor can parse
		// Remove microseconds if present (".203765") for Safari compatibility
		const cleanedTimestamp = timestamp.replace(/\.\d{6}/, "");
    	const timestampDate = new Date(cleanedTimestamp);
		const now = new Date();
		const diffMins = Math.floor((now - timestampDate) / 60000);
		setMinutesAgo(diffMins);
	}

	if (!listings) {
		return <div className="text-center">Loading live listings...</div>;
	}

	const cars = Object.values(listings);
	const visibleCars = cars.slice(0, visibleCount);

	return (
		<div className="text-center">
			<h1>{cars.length} Live* Auction Listings</h1>
			<h6 style={{ cursor: "pointer", display: "inline-block" }} onClick={refreshListings}>*as of {minutesAgo} minutes ago (click me to refresh)</h6>
			<Row>
				{visibleCars.map(car => (
					<Col xs={12} sm={6} lg={4} xl={3} key={car.url}>
						<CarSummary {...car} />
					</Col>
				))}
			</Row>
			{visibleCount < cars.length && (
				<Button
					variant="primary"
					className="mt-3"
					size="lg"
					onClick={() => setVisibleCount(visibleCount + PAGE_SIZE)}
				>
					Show More
				</Button>
			)}
		</div>
	);
}

export default AllListings;