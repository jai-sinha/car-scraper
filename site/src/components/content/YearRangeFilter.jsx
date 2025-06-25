import { Button, Dropdown, Form } from "react-bootstrap";
import React, { useState } from "react";

const YearRangeFilter = ({ onFilter, onClear }) => {
	const [yearFrom, setYearFrom] = useState('');
	const [yearTo, setYearTo] = useState('');

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
					<Button size="md" className="mt-2 me-2" 
						onClick={() => onFilter(yearFrom, yearTo)}>
						Filter
					</Button>
					<Button size="md" variant="secondary" className="mt-2" 
						onClick={() => {
							onClear();
							setYearFrom('');
							setYearTo('');
						}}>
						Undo Filter
					</Button>
				</div>
			</Dropdown.Menu>
		</Dropdown>
	);
};

export default YearRangeFilter;