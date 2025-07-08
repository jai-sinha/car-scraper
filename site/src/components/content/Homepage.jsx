import { SearchProvider, useSearch } from "../contexts/SearchContext";
import Search from "../search/Search";
import AllListings from "../helpers/AllListings";
import { Container, Row, Col } from "react-bootstrap";
import CarSummary from "../helpers/CarSummary";

function ResultsWrapper() {
	const { data, filteredData, searchedQuery, loading } = useSearch();
	// Show AllListings only if both data and filteredData are null
	if ((data || filteredData) || loading === true) {
		const display = filteredData || data;

		if (loading) {
			return <div className="text-center">Loading search results for '{searchedQuery}'... </div>;
		}

		return (
			<>
			<h1 className="text-center">{Object.values(display).length} Results for '{searchedQuery}'</h1>
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