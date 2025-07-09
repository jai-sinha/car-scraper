import { Form, Button } from "react-bootstrap";
import { useSearch } from "../contexts/SearchContext";
import KeywordFilter from "./KeywordFilter";
import YearRangeFilter from "./YearRangeFilter";

const Search = () => {
	const { query, setQuery, useDB, setUseDB, fetchCarData, loading, setData, setFilteredData, setResetKey } = useSearch();

	return (
		<Form className="mx-auto w-50 p-2">
			<Form.Label htmlFor="query"></Form.Label>
			<Form.Control
				className="mb-2"
				size="lg"
				id="query"
				value={query}
				placeholder="Search (e.g. '991 911', 'Alfa 105 Series', 'Mercedes W113 SL')"
				onChange={(e) => setQuery(e.target.value)}
				onKeyDown={(e) => {
					if (e.key === 'Enter') {
						e.preventDefault();
						fetchCarData();
					}
				}}
			/>
			<div className="d-flex align-items-center mb-2 flex-wrap gap-2">
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
				<Form.Check
					style={{ transform: "scale(1.25)"}}			
					type="checkbox"
					id="use-db-search"
					label="Use DB search"
					checked={useDB}
					onChange={e => setUseDB(e.target.checked)}
					className="m-2 ms-4"
				/>
			</div>
			<div className="d-flex align-items-center mt-2 gap-2">
				<KeywordFilter />
				<YearRangeFilter />
			</div>
		</Form>
	);
};

export default Search;