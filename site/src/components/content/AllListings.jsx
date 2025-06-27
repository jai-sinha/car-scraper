import { useState, useEffect } from "react";
import { Row, Col } from "react-bootstrap";
import CarSummary from "./CarSummary";

const API_URL = import.meta.env.VITE_API_URL;

function AllListings( data ) {
  const [listings, setListings] = useState(null);

	useEffect(() => {
		const fetchListings = async () => {
			try {
				const response = await fetch(`${API_URL}/listings`);
				console.log("Fetching live listings from:", `${API_URL}/listings`);
				if (!response.ok) {
					throw new Error(`HTTP error: ${response.status}`);
				}
				const data = await response.json();
				setListings(data || null);
				console.log("Live listings data:", data);
			} catch (err) {
			console.error(err);
			}
		};
		fetchListings();
	}, []);

	if (!listings) {
		return <div className="text-center">Loading live listings...</div>;
	}

	return (
		<div>
			<h1>Live BaT Listings</h1>
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