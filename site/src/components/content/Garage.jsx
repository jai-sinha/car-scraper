import { useLoginStatus } from "../contexts/LoginStatusContext";
import { useSavedListings } from "../contexts/SavedContext";
import { Row, Col, Container, Spinner, Alert } from "react-bootstrap";
import CarSummary from "../helpers/CarSummary";

function Garage() {
	const { loginStatus } = useLoginStatus();
	const { saved, loading, error } = useSavedListings();

	if (!loginStatus) {
		return (
			<Container className="mt-5">
				<Alert variant="info" className="text-center">
					<h4>Login Required</h4>
					<p className="mb-0">You need to log in to view your saved listings.</p>
				</Alert>
			</Container>
		);
	}

	if (loading) {
		return (
			<Container className="mt-5 text-center">
				<Spinner animation="border" variant="primary" size="lg" />
				<p className="mt-3">Loading your saved listings...</p>
			</Container>
		);
	}

	if (error) {
		return (
			<Container className="mt-5">
				<Alert variant="danger" className="text-center">
					<h4>Error</h4>
					<p className="mb-0">{error}</p>
				</Alert>
			</Container>
		);
	}

	if (!saved || saved.length === 0) {
		return (
			<Container className="mt-5">
				<Alert variant="secondary" className="text-center">
					<h4>No Saved Listings</h4>
					<p className="mb-0">You haven't saved any cars yet. Start browsing to find your favorites!</p>
				</Alert>
			</Container>
		);
	}

	return (
		<Container className="mt-4">
			<div className="mb-4">
				<h2 className="text-center mb-3">
					Your Garage
				</h2>
				<p className="text-center text-muted">
					{saved.length} saved listing{saved.length !== 1 ? 's' : ''}
				</p>
			</div>
			
			<Row className="g-4">
				{saved.map(car => (
					<Col xs={12} sm={6} lg={4} xl={3} key={car.url}>
						<CarSummary {...car} />
					</Col>
				))}
			</Row>
		</Container>
	);
}

export default Garage;