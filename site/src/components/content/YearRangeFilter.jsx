import { Button, Dropdown, Form } from "react-bootstrap";

const YearRangeFilter = ({ yearFrom, yearTo, setYearFrom, setYearTo, onFilter, onClear }) => {
	return (
		<Dropdown>
			<Dropdown.Toggle variant="outline-secondary" id="dropdown-years">
				Year Range
			</Dropdown.Toggle>
			<Dropdown.Menu>
				<div style={{ padding: '10px', minWidth: '200px' }}>
					<Form.Control
						size="sm" 
						id="yearFrom"
						value={yearFrom}
						placeholder="1800"
						onChange={(e) => setYearFrom(e.target.value)}
						style={{ marginBottom: '10px' }}
					/>
					<Form.Control
						size="sm" 
						id="yearTo"
						value={yearTo}
						placeholder="2025"
						onChange={(e) => setYearTo(e.target.value)}
					/>
					<Button size="md" className="mt-2 me-2" onClick={onFilter}>Filter</Button>
					<Button size="md" variant="secondary" className="mt-2" onClick={onClear}>
						Undo Filter
					</Button>
				</div>
			</Dropdown.Menu>
		</Dropdown>
	);
};

export default YearRangeFilter;