import { useLoginStatus } from "../contexts/LoginStatusContext";
import { useState, useEffect } from "react";
import { Row, Col } from "react-bootstrap";
import CarSummary from "../helpers/CarSummary";

const API_URL = import.meta.env.VITE_API_URL;

function Garage() {
	const { loginStatus } = useLoginStatus();
	const [savedListings, setSavedListings] = useState([]);

	const fetchSavedListings = async () => {
		try {
			const response = await fetch(`${API_URL}/garage`, {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to fetch saved listings');
			const data = await response.json();
			setSavedListings(data);
		} catch (error) {
			console.error('Error fetching saved listings:', error);
			setSavedListings([]);
		}
	};

	useEffect(() => {
		if (loginStatus) {
			fetchSavedListings();
		}
	}, [loginStatus]);

	if (!loginStatus) {
		return <h2>You need to log in to use this feature.</h2>;
	}

	if (!savedListings || Object.keys(savedListings).length === 0) {
		return <h2 className="text-center">You have no saved listings in your Garage. Go search for some cars to save!</h2>;
	}

	return (
		<div>
			<h2 className="text-center">Your Saved Listings:</h2>
				<Row>
					{Object.values(savedListings).map(car => (
						<Col xs={12} md={6} lg={3} key={car.url}>
							<CarSummary
								{...car}
								initialSaved={true}
								onUnsave={ fetchSavedListings }
							/>
						</Col>
					))}
				</Row>
		</div>
	);
}

export default Garage;