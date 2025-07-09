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
	const [useDB, setUseDB] = useState(false);
	const [searchedQuery, setSearchedQuery] = useState(false);

	const API_URL = import.meta.env.VITE_API_URL;

	const fetchCarData = async () => {
		setLoading(true);
		setError(null);
		setData(null);

		try {
			let url;
			if (useDB) {
				url = `${API_URL}/db_search?query=${encodeURIComponent(query)}`;
			} else {
				url = `${API_URL}/search?query=${encodeURIComponent(query)}`;
			}
			setSearchedQuery(query);
			const response = await fetch(url);

			if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const result = await response.json();
			console.log("Fetched from endpoint:", url);
			const sortedData = Object.entries(result)
				.sort(([, a], [, b]) => getTimeLeftInSeconds(a.time) - getTimeLeftInSeconds(b.time))
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
				const year = car.year ? parseInt(car.year) : 0; // Default to 0 if year is missing
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

	const getTimeLeftInSeconds = (endTime) => {
		if (endTime === "N/A") return 0;
		const end = new Date(endTime);
		const now = new Date();
		const diffInSeconds = Math.max(0, Math.floor((end - now) / 1000));
		return diffInSeconds;
	}

	return (
		<SearchContext.Provider value={{
			query, setQuery,
			searchedQuery, setSearchedQuery,
			data, setData,
			useDB, setUseDB,
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
			getTimeLeftInSeconds,
		}}>
			{children}
		</SearchContext.Provider>
	);
}