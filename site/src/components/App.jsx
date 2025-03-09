import { Button, Container, Form, Row, Col } from "react-bootstrap";
import { useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import CarSummary from "./CarSummary"

const App = () => {
	const [make, setMake] = useState("");
	const [model, setModel] = useState("");
	const [generation, setGeneration] = useState("");

	const [data, setData] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	// Fetch data from API
	const fetchCarData = async () => {
		setLoading(true);
		setError(null);
		setData(null);

		try {
			const url = `http://127.0.0.1:5000/GET?make=${encodeURIComponent(make)}&model=${encodeURIComponent(model)}&generation=${encodeURIComponent(generation)}`;
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

	return <Container fluid>
		<div style={{ margin: "1rem" }}>
			<h1>Car Search</h1>
			<Form>
				<Form.Label htmlFor="make"></Form.Label>
				<Form.Control 
					id="make"
					value={make}
					placeholder="Make"
					onChange={(e) => setMake(e.target.value)}
				/>
				<Form.Label htmlFor="model"></Form.Label>
				<Form.Control 
					id="model"
					value={model}
					placeholder="Model"
					onChange={(e) => setModel(e.target.value)}
				/>
				<Form.Label htmlFor="generation"></Form.Label>
				<Form.Control 
					id="generation"
					value={generation}
					placeholder="Generation"
					onChange={(e) => setGeneration(e.target.value)}
				/>
				<br />
				<Button variant="primary" onClick={fetchCarData} disabled={loading}>
						{loading ? "Loading..." : "Submit"}
				</Button>
				<Button variant="secondary" onClick={() => {
						setMake('');
						setModel('');
						setGeneration('');
					}}> Reset Search
				</Button>
			</Form>
			<br></br>
			{error && <p style={{ color: "red" }}>Error: {error}</p>}

			{data && (
				<Row>
					{data.length === 0 ? (
						<p>No cars match this search!</p>
					) : (
						Object.values(data).map(car => (
							<Col xs={12} md={6} lg={3} key={car.url}>
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

export default App;