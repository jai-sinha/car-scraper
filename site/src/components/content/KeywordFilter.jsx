import { Button, Dropdown, Form } from "react-bootstrap";

const KeywordFilter = ({ includeKeywords, excludeKeywords, setIncludeKeywords, setExcludeKeywords, onFilter, onClear }) => {
	return (
		<Dropdown>
			<Dropdown.Toggle variant="outline-secondary" id="dropdown-keywords">
				Keywords
			</Dropdown.Toggle>
			<Dropdown.Menu>
				<div style={{ padding: '10px', minWidth: '275px' }}>
					<Form.Control
						size="sm" 
						id="includeKeywords"
						value={includeKeywords}
						placeholder="Include (e.g. 'carrera s, 6-speed')"
						onChange={(e) => setIncludeKeywords(e.target.value)}
						style={{ marginBottom: '10px' }}
					/>
					<Form.Control
						size="sm" 
						id="excludeKeywords"
						value={excludeKeywords}
						placeholder="Exclude (e.g. 'convertible, gt3')"
						onChange={(e) => setExcludeKeywords(e.target.value)}
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

export default KeywordFilter;