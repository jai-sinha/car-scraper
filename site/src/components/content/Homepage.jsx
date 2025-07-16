import { SearchProvider, useSearch } from "../contexts/SearchContext";
import Search from "../search/Search";
import AllListings from "../helpers/AllListings";
import { Container, Row, Col } from "react-bootstrap";
import CarSummary from "../helpers/CarSummary";

function ResultsWrapper() {
	const { data, filteredData, searchedQuery, loading } = useSearch();
	const display = filteredData || data;
	console.log({ query, searchedQuery, loading });

	if (loading) {
		return <div className="text-center">Loading search results for '{searchedQuery}'... </div>;
	}

	// Show "no results found" if a search was performed and there are no results
	if (searchedQuery && (!display || Object.values(display).length === 0)) {
		return <div className="text-center">No results found for '{searchedQuery}'.</div>;
	}

	// Show results if available
	if (display && Object.values(display).length > 0) {
		return (
			<>
				<h1 className="text-center">
					{Object.values(display).length} Result {Object.values(display).length !== 1 ? 's' : ''} for '{searchedQuery}'
				</h1>
				<Row>
					{Object.values(display).map(car => (
						<Col xs={12} sm={6} lg={4} xl={3} key={car.url}>
							<CarSummary {...car} />
						</Col>
					))}
				</Row>
			</>
		);
	}

	// Default: show all listings
	return <AllListings />;
}

export default function Homepage() {
	return (
		<SearchProvider>
			<Container fluid>
				<div>
					<Search />
					<ResultsWrapper />
				</div>
			</Container>
		</SearchProvider>
	);
}