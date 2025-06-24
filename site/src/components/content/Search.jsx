import "../../App.css"
import { Button, Container, Form, Row, Col } from "react-bootstrap";
import { useState } from "react";
import CarSummary from "./CarSummary"

const Search = () => {
	const [make, setMake] = useState("");
	const [model, setModel] = useState("");
	const [generation, setGeneration] = useState("");

	const [data, setData] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	// Fetch data from API-- not using useEffect because we don't want this to run on component mount, only when triggered by pressing "search"
	const fetchCarData = async () => {
		setLoading(true);
		setError(null);
		setData(null);

		try {
			const url = `http://127.0.0.1:5000/search?make=${encodeURIComponent(make)}&model=${encodeURIComponent(model)}&generation=${encodeURIComponent(generation)}`;
			const response = await fetch(url);

			if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const result = await response.json();
			setData(result);
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	return <Container style={{ maxWidth: "1200px" }}>
		<div style={{ margin: ".25rem" }}>
			<h1>Search Bring a Trailer, Cars & Bids, and PCARMARKET</h1>
			<Form>
				<Form.Label htmlFor="make"></Form.Label>
				<Form.Control
					size="lg" 
					id="make"
					value={make}
					placeholder="Make"
					onChange={(e) => setMake(e.target.value)}
				/>
				<Form.Label htmlFor="model"></Form.Label>
				<Form.Control
					size="lg" 
					id="model"
					value={model}
					placeholder="Model"
					onChange={(e) => setModel(e.target.value)}
				/>
				<Form.Label htmlFor="generation"></Form.Label>
				<Form.Control
					size="lg" 
					id="generation"
					value={generation}
					placeholder="Generation"
					onChange={(e) => setGeneration(e.target.value)}
				/>
				<br />
				<Button className="me-1" size="lg" variant="primary" onClick={fetchCarData} disabled={loading}>
					{loading ? "Loading..." : "Search"}
				</Button>
				<Button size="lg" variant="secondary" onClick={() => {
					setMake('');
					setModel('');
					setGeneration('');
					setData(null);
				}}> Reset Search
				</Button>
			</Form>
			<br></br>
			{error && <p style={{ color: "red" }}>Error: {error}</p>}

			{data && (
				<Row>
					{data.length === 0 ? (
						<p>No live listings match this search!</p>
					) : (
						Object.values(data).map(car => (
							<Col xs={12} md={6} lg={4} key={car.url}>
								<CarSummary 
									{...car}
								/>
							</Col>
						))
					)}
				</Row>
			)}
		</div>
	</Container>
};

export default Search;