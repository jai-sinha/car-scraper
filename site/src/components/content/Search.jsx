import "../../App.css"
import { Button, Container, Form, Row, Col } from "react-bootstrap";
import { useState } from "react";
import CarSummary from "./CarSummary"

const API_URL = import.meta.env.VITE_API_URL;

const Search = () => {
	const [query, setQuery] = useState('');

	const [data, setData] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	// Fetch data from API-- not using useEffect because we don't want this to run on component mount, only when triggered by pressing "search"
	const fetchCarData = async () => {
		setLoading(true);
		setError(null);
		setData(null);

		try {
			const url = `${API_URL}/search?query=${encodeURIComponent(query)}`;
			const response = await fetch(url);

			if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const result = await response.json();
			console.log("Searched URL:", url);
			console.log(result);
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
				<Form.Label htmlFor="query"></Form.Label>
				<Form.Control
					size="lg" 
					id="query"
					value={query}
					placeholder="Search (e.g. '991 911', 'BMW E9', 'Mercedes W113 SL')"
					onChange={(e) => setQuery(e.target.value)}
				/>
				<br />
				<Button className="me-1" size="lg" variant="primary" onClick={fetchCarData} disabled={loading}>
					{loading ? "Loading..." : "Search"}
				</Button>
				<Button size="lg" variant="secondary" onClick={() => {
					setQuery('');
					setData([]);
				}}> Reset Search
				</Button>
			</Form>
			<br></br>
			{error && <p style={{ color: "red" }}>Error: {error}</p>}

			{data && (
				<Row>
					{data.length === 0 ? (
						<p className='text-center'>No live listings match this search!</p>
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