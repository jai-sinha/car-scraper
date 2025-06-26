import "../../App.css"
import { Button, Container, Form, Dropdown, Row, Col } from "react-bootstrap";
import { useState } from "react";
import CarSummary from "./CarSummary"
import YearRangeFilter from "./YearRangeFilter";
import KeywordFilter from "./KeywordFilter";

const API_URL = import.meta.env.VITE_API_URL;

const Search = () => {
	const [query, setQuery] = useState('');

	const [data, setData] = useState(null);
	const [filteredData, setFilteredData] = useState(null);
	const [resetKey, setResetKey] = useState(0);
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
			const sortedData = Object.entries(result)
				.sort(([, a], [, b]) => parseTimeToHours(a.time) - parseTimeToHours(b.time))
				.reduce((obj, [key, value]) => ({ 
					...obj, 
					[key]: value
				}), {});
			setData(sortedData);
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	const handleYearFilter = (yearFrom, yearTo) => {
		yearFrom = yearFrom ? yearFrom : '1800'; // Default to 1800 if not set
		yearTo = yearTo ? yearTo : '2025'; // Default to 2025 if not set

		const from = parseInt(yearFrom);
		const to = parseInt(yearTo);
		if (from > to) {
			alert("Year 'From' cannot be greater than 'To'.");
			return;
		}

		if (!data) {
			alert("No data to filter. Please search first.");
			return;
		}

		const filtered = Object.fromEntries(
			Object.entries(data).filter(([key, car]) => {
				const year = parseInt(car.year);
				return year >= from && year <= to;
			})
		);

		if (Object.keys(filtered).length === 0) { 
			alert("No cars found in the specified year range.");
			return;
		}
		setFilteredData(filtered);
 	}

	const handleKeywordFilter = (include, exclude) => {
		// Implement keyword filtering logic here
		// filter data based on include/exclude keywords
	};

	const parseTimeToHours = (timeString) => {	
		const number = parseInt(timeString);
		if (timeString.includes('N/A')) {
			return Infinity; // In MarketPlace, so no time limit.
		} else if (timeString.includes('day')) {
			return number * 24; // Convert days to hours
		} else { // Handle hours + minutes
			const hourMatch = timeString.match(/(\d+)h/);
			const minuteMatch = timeString.match(/(\d+)m/);
			const hours = hourMatch ? parseInt(hourMatch[1]) : 0;
			const minutes = minuteMatch ? parseInt(minuteMatch[1]) : 0;
			return hours + (minutes / 60);
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
					onKeyDown={(e) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							fetchCarData();
						}
					}}
				/>
				<div className="d-flex gap-2 mt-2 mb-3">
					<YearRangeFilter
						key={`year-${resetKey}`}
						onFilter={handleYearFilter}
						onClear={() => {setFilteredData(null)}}
					/>
					<KeywordFilter
						key={`keyword-${resetKey}`}
						onFilter={handleKeywordFilter}
						onClear={() => {setFilteredData(null)}}
					/>
				</div>
				<Button className="me-1" size="lg" variant="primary" onClick={fetchCarData} disabled={loading}>
					{loading ? "Loading..." : "Search"}
				</Button>
				<Button size="lg" variant="secondary" onClick={() => {
					setQuery('');
					setData(null);
					setFilteredData(null);
					setResetKey(prev => prev + 1);
				}}> Reset Search
				</Button>
			</Form>
			<br></br>
			{error && <p style={{ color: "red" }}>Error: {error}</p>}

			{(filteredData && Object.keys(filteredData).length > 0) ? (
				<Row>
					{Object.values(filteredData).map(car => (
						<Col xs={12} md={6} lg={4} key={car.url}>
							<CarSummary {...car} />
						</Col>
					))}
				</Row>
			) : data && (
				<Row>
					{Object.keys(data).length === 0 ? (
						<p className='text-center'>No live listings match this search!</p>
					) : (
						Object.values(data).map(car => (
							<Col xs={12} md={6} lg={4} key={car.url}>
								<CarSummary {...car} />
							</Col>
						))
					)}
				</Row>
			)}
		</div>
	</Container>
};

export default Search;