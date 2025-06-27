import { useState, useEffect } from "react";
import { Row, Col } from "react-bootstrap";
import CarSummary from "./CarSummary";

const API_URL = import.meta.env.VITE_API_URL;

function AllListings() {
  const [listings, setListings] = useState(null);
  const [minutesAgo, setMinutesAgo] = useState(null);

	useEffect(() => {
		const fetchListings = async () => {
			try {
				const response = await fetch(`${API_URL}/listings`);
				console.log("Fetching live listings from:", `${API_URL}/listings`);
				if (!response.ok) {
					throw new Error(`HTTP error: ${response.status}`);
				}
				const data = await response.json();
				const timestamp = Object.keys(data)[0];
				const listingsObj = data[timestamp];
				setListings(listingsObj);
				calculateMins(timestamp);
				console.log("Live listings data:", listingsObj);
				console.log("Timestamp of listings:", timestamp);

			} catch (err) {
				console.error(err);
			}
		};
		fetchListings();
	}, []);

	const refreshListings = async () => {
		setListings(null); // Reset listings to show loading state
		setMinutesAgo(null); // Reset minutes ago to show loading state
		try {
			const response = await fetch(`${API_URL}/listings`);
			console.log("Fetching live listings from:", `${API_URL}/listings`);
			if (!response.ok) {
				throw new Error(`HTTP error: ${response.status}`);
			}
			const data = await response.json();
			const timestamp = Object.keys(data)[0];
			const listingsObj = data[timestamp];
			setListings(listingsObj);
			calculateMins(timestamp);
			console.log("Live listings data:", listingsObj);
			console.log("Timestamp of listings:", timestamp);

		} catch (err) {
			console.error(err);
		}
	};

	const calculateMins = (timestamp) => {
		const timestampDate = new Date(timestamp.replace(" ", "T") + "Z");
      const now = new Date();
      const diffMins = Math.floor((now - timestampDate) / 60000);
      setMinutesAgo(diffMins);
	}


	if (!listings) {
		return <div className="text-center">Loading live listings...</div>;
	}

	return (
		<div className="text-center">
			<h1>All Live* Auction Listings</h1>
			<h6 style={{ cursor: "pointer", display: "inline-block" }} onClick={refreshListings}>*as of {minutesAgo} minutes ago (click me to refresh)</h6>
			<Row>
				{Object.values(listings).map(car => (
					<Col xs={12} md={6} lg={4} key={car.url}>
						<CarSummary {...car} />
					</Col>
				))}
			</Row>
		</div>
	);
}

export default AllListings;