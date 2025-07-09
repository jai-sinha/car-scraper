import { createContext, useContext, useState, useEffect } from "react";
import { useLoginStatus } from "./LoginStatusContext";

const SavedListingsContext = createContext();

export function useSavedListings() {
	return useContext(SavedListingsContext);
}

export function SavedListingsProvider({ children }) {
	const [saved, setSaved] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const { loginStatus, setShowLoginModal } = useLoginStatus();

	const API_URL = import.meta.env.VITE_API_URL;

	// Fetch saved listings when loginStatus changes
	useEffect(() => {
		if (loginStatus) {
			setLoading(true);
			setError(null);
			fetch(`${API_URL}/garage`, {
				method: "GET",
				headers: { "Content-Type": "application/json" },
				credentials: "include"
			})
			.then(res => {
				if (!res.ok) throw new Error("Failed to fetch saved listings");
				return res.json();
			})
			.then(data => {
				const savedArr = Object.values(data);
				setSaved(savedArr);
			})
			.catch(err => setError(err.message))
			.finally(() => setLoading(false));
		} else {
			setSaved([]);
		}
	}, [loginStatus, API_URL]);

	const isSaved = (url) => saved.some(car => car.url === url);

	const addSaved = async (url) => {
		if (!loginStatus) {
			setShowLoginModal(true);
			return;
		}
		try {
			setLoading(true);
			const res = await fetch(`${API_URL}/save`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify({ "url": url })
			});
			if (!res.ok) throw new Error("Failed to save listing");
			const newCar = await res.json();
			setSaved(prev => prev.some(car => car.url === url) ? prev : [...prev, newCar.car]);
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	const removeSaved = async (url) => {
		if (!loginStatus) return;
		try {
			setLoading(true);
			const res = await fetch(`${API_URL}/delete_saved_listing`, {
				method: "DELETE",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify({ "url": url })
			});
			if (!res.ok) throw new Error("Failed to remove saved listing");
			setSaved(prev => prev.filter(car => car.url !== url));
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	return (
		<SavedListingsContext.Provider value={{
			saved,
			isSaved,
			addSaved,
			removeSaved,
			loading,
			error
		}}>
			{children}
		</SavedListingsContext.Provider>
	);
}