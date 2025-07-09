import { createContext, useContext, useState, useEffect } from "react";

const LoginStatusContext = createContext();
const API_URL = import.meta.env.VITE_API_URL;

export function useLoginStatus() {
	return useContext(LoginStatusContext);
}

export function LoginStatusProvider({ children }) {
	const storedLoginStatus = sessionStorage.getItem("loginStatus");
	const [loginStatus, setLoginStatus] = useState(
		storedLoginStatus ? JSON.parse(storedLoginStatus) : null
	);
	const [showLoginModal, setShowLoginModal] = useState(false);
	const [showLogoutModal, setShowLogoutModal] = useState(false);

	useEffect(() => {
		if (loginStatus) {
			sessionStorage.setItem("loginStatus", JSON.stringify(loginStatus));
		} else {
			sessionStorage.removeItem("loginStatus");
		}
	}, [loginStatus]);

	async function handleLogin(credentials) {
		console.log('Login attempted with:', credentials);

		try {
			const response = await fetch(`${API_URL}/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(credentials)
			});
			const userData = await response.json();
			console.log(userData);
			if (response.ok) {
				setLoginStatus(userData.user);
				setShowLoginModal(false);
			} else {
				alert('Login failed: ' + userData.error);
			}
			} catch (error) {
			alert('Login error: ' + error.message);
		}
	};

	async function handleLogout() {
		try {
			const response = await fetch(`${API_URL}/logout`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: "include"
			});
			const userData = await response.json();
			console.log(userData);
			if (response.ok) {
				setLoginStatus(null);
			} else {
				alert('Logout failed: ' + userData.error);
			}
			} catch (error) {
			alert('Logout error: ' + error.message);
		}
	};

	return (
		<LoginStatusContext.Provider value={{
			loginStatus, setLoginStatus,
			showLoginModal, setShowLoginModal,
			showLogoutModal, setShowLogoutModal,
			handleLogin, handleLogout
		}}>
			{children}
		</LoginStatusContext.Provider>
	);
}

export default LoginStatusContext;