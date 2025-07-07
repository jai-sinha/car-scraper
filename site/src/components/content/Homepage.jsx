import { SearchProvider, useSearch } from "../contexts/SearchContext";
import Search from "./Search";
import AllListings from "./AllListings";
import { Container, Row, Col } from "react-bootstrap";
import CarSummary from "./CarSummary";

function ListingsWrapper() {
	const { data, filteredData, queryUsed, loading } = useSearch();
	// Show AllListings only if both data and filteredData are null
	if ((data || filteredData) || loading === true) {
		const display = filteredData || data;

		if (loading) {
			return <div className="text-center">Loading search results for '{queryUsed}'... </div>;
		}

		return (
			<>
				<h1 className="text-center">{Object.values(display).length} Results for '{queryUsed}'</h1>
				<Row>
					{Object.values(display).map(car => (
						<Col xs={12} md={6} lg={3} key={car.url}>
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
					<ListingsWrapper />
				</div>
			</Container>
		</SearchProvider>
	);
}