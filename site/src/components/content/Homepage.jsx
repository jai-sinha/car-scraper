import { SearchProvider, useSearch } from "../contexts/SearchContext";
import Search from "./Search";
import AllListings from "./AllListings";
import { Container, Row, Col } from "react-bootstrap";
import CarSummary from "./CarSummary";

function ListingsWrapper() {
	const { data, filteredData } = useSearch();
	// Show AllListings only if both data and filteredData are null
	if (data || filteredData) {
		const display = filteredData || data; 
		return (
			<Row>
				{Object.values(display).map(car => (
					<Col xs={12} md={6} lg={3} key={car.url}>
						<CarSummary {...car} />
					</Col>
				))}
			</Row>
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