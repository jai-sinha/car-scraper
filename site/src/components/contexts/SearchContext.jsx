import { createContext, useContext, useState } from "react";

const SearchContext = createContext();

export function useSearch() {
    return useContext(SearchContext);
}

export function SearchProvider({ children }) {
    const [query, setQuery] = useState('');
    const [data, setData] = useState(null);
    const [filteredData, setFilteredData] = useState(null);
    const [resetKey, setResetKey] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [yearFilter, setYearFilter] = useState(null);
    const [keywordFilter, setKeywordFilter] = useState(null);

    const API_URL = import.meta.env.VITE_API_URL;

    // ...move fetchCarData, applyFilters, handleYearFilter, handleKeywordFilter, clearYearFilter, clearKeywordFilter, parseTimeToHours here...

	const fetchCarData = async () => {
		setLoading(true);
		setError(null);
		setData(null);

		try {
			const url = `${API_URL}/search?query=${encodeURIComponent(query)}`;
			const response = await fetch(url);

			if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const result = await response.json();
			console.log("Searched URL:", url);
			console.log(result);
			const sortedData = Object.entries(result)
				.sort(([, a], [, b]) => parseTimeToHours(a.time) - parseTimeToHours(b.time))
				.reduce((obj, [key, value]) => ({ 
					...obj, 
					[key]: value
				}), {});
			setData(sortedData);
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	const applyFilters = (sourceData, yearParams = yearFilter, keywordParams = keywordFilter) => {
		let result = sourceData;

		// Apply year filter if active
		if (yearParams) {
			const { from, to } = yearParams;
			result = Object.fromEntries(
				Object.entries(result).filter(([key, car]) => {
					const year = parseInt(car.year);
					return year >= from && year <= to;
				})
			);
		}

		// Apply keyword filter if active
		if (keywordParams) {
			const { includeKeywords, excludeKeywords } = keywordParams;
			result = Object.fromEntries(
				Object.entries(result).filter(([key, car]) => {
					const searchText = `${car.title || ''}`.toLowerCase();
					
					// Check include keywords (ALL must be present)
					let includeMatch = true;
					if (includeKeywords.length > 0) {
						includeMatch = includeKeywords.every(keyword => searchText.includes(keyword));
					}
					
					// Check exclude keywords (NONE should be present)
					let excludeMatch = false;
					if (excludeKeywords.length > 0) {
						excludeMatch = excludeKeywords.some(keyword => searchText.includes(keyword));
					}
					
					return includeMatch && !excludeMatch;
				})
			);
		}
		
		return result;
	};

	const handleYearFilter = (yearFrom, yearTo) => {
		yearFrom = yearFrom ? yearFrom : '1800'; // Default to 1800 if not set
		yearTo = yearTo ? yearTo : '2025'; // Default to 2025 if not set

		const from = parseInt(yearFrom);
		const to = parseInt(yearTo);
		if (from > to) {
			alert("Year 'From' cannot be greater than 'To'.");
			return;
		}

		if (!data) {
			alert("No data to filter. Please search first.");
			return;
		}

		const filtered = Object.fromEntries(
			Object.entries(data).filter(([key, car]) => {
				const year = parseInt(car.year);
				return year >= from && year <= to;
			})
		);

		if (Object.keys(filtered).length === 0) { 
			alert("No cars found in the specified year range.");
			return;
		}
		setFilteredData(filtered);
 	}

	const handleKeywordFilter = (include, exclude) => {
		// Validate inputs
		if (!include?.trim() && !exclude?.trim()) {
			alert("Please provide at least one keyword to filter by");
			return;
		}

		if (!data) {
			alert("No data to filter. Please search first.");
			return;
		}

		// Process keywords
		const includeKeywords = include ? include.toLowerCase().split(',').map(k => k.trim()).filter(k => k) : [];
		const excludeKeywords = exclude ? exclude.toLowerCase().split(',').map(k => k.trim()).filter(k => k) : [];

		// Save keyword filter parameters
		const keywordParams = { includeKeywords, excludeKeywords };
		setKeywordFilter(keywordParams);

		// Apply all filters
		const filtered = applyFilters(data, yearFilter, keywordParams);

		if (Object.keys(filtered).length === 0) {
			alert("No cars found matching the current filters.");
			return;
		}
		setFilteredData(filtered);
	};

	// Clear year filter only
	const clearYearFilter = () => {
		setYearFilter(null);
		if (keywordFilter) {
			// Reapply keyword filter only
			const filtered = applyFilters(data, null, keywordFilter);
			setFilteredData(Object.keys(filtered).length > 0 ? filtered : null);
		} else {
			// No other filters active
			setFilteredData(null);
		}
	};

	// Clear keyword filter only
	const clearKeywordFilter = () => {
		setKeywordFilter(null);
		if (yearFilter) {
			// Reapply year filter only
			const filtered = applyFilters(data, yearFilter, null);
			setFilteredData(Object.keys(filtered).length > 0 ? filtered : null);
		} else {
			// No other filters active
			setFilteredData(null);
		}
	};

	const parseTimeToHours = (timeString) => {	
		const number = parseInt(timeString);
		if (timeString.includes('N/A')) {
			return Infinity; // In MarketPlace, so no time limit.
		} else if (timeString.includes('day')) {
			return number * 24; // Convert days to hours
		} else { // Handle hours + minutes
			const hourMatch = timeString.match(/(\d+)h/);
			const minuteMatch = timeString.match(/(\d+)m/);
			const hours = hourMatch ? parseInt(hourMatch[1]) : 0;
			const minutes = minuteMatch ? parseInt(minuteMatch[1]) : 0;
			return hours + (minutes / 60);
		}
	};

    // (Paste all the logic from Search.jsx here, but remove the JSX return)

    return (
        <SearchContext.Provider value={{
            query, setQuery,
            data, setData,
            filteredData, setFilteredData,
            resetKey, setResetKey,
            loading, setLoading,
            error, setError,
            yearFilter, setYearFilter,
            keywordFilter, setKeywordFilter,
            // expose all handler functions here
            fetchCarData,
            handleYearFilter,
            handleKeywordFilter,
            clearYearFilter,
            clearKeywordFilter,
        }}>
            {children}
        </SearchContext.Provider>
    );
}