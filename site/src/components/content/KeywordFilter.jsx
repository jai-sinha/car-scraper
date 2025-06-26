import { Button, Dropdown, Form } from "react-bootstrap";
import React, { useState } from "react";

const KeywordFilter = ({ onFilter, onClear }) => {
	const [includeKeywords, setIncludeKeywords] = useState('');
	const [excludeKeywords, setExcludeKeywords] = useState('');
	const [show, setShow] = useState(false);

	return (
		<Dropdown show={show} onToggle={(isOpen) => setShow(isOpen)}>
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
					<Button size="md" className="mt-2 me-2" 
						onClick={() => {onFilter(includeKeywords, excludeKeywords); setShow(false);}}>
						Filter
					</Button>
					<Button size="md" variant="secondary" className="mt-2" 
						onClick={() => {
							onClear()
							setExcludeKeywords('');
							setIncludeKeywords('');
							setShow(false);
						}}>
						Undo Filter
					</Button>
				</div>
			</Dropdown.Menu>
		</Dropdown>
	);
};

export default KeywordFilter;