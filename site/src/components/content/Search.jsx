import { Form, Button } from "react-bootstrap";
import { useSearch } from "../contexts/SearchContext";
import KeywordFilter from "./KeywordFilter";
import YearRangeFilter from "./YearRangeFilter";

const Search = () => {
	const { query, setQuery, fetchCarData, loading, setData, setFilteredData, setResetKey } = useSearch();

	return (
		<Form className="mx-auto w-50 p-2">
			<Form.Label htmlFor="query"></Form.Label>
			<Form.Control
				className="mb-2"
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
			<div className="d-flex align-items-center mt-2 gap-2">
				<KeywordFilter />
				<YearRangeFilter />
			</div>
		</Form>
	);
};

export default Search;