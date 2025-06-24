import React, { useState, useEffect } from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { Link, Outlet } from "react-router-dom";
import LoginStatusContext from "../contexts/LoginStatusContext";
import LoginModal from "../auth/LoginModal"

const API_URL = import.meta.env.VITE_API_URL;

function Layout(props) {
	const storedLoginStatus = sessionStorage.getItem("loginStatus");
	const [loginStatus, setLoginStatus] = useState(
		storedLoginStatus ? JSON.parse(storedLoginStatus) : null
	);
	const [showLoginModal, setShowLoginModal] = useState(false);

	// Update sessionStorage whenever loginStatus changes
	useEffect(() => {
		if (loginStatus) {
			sessionStorage.setItem("loginStatus", JSON.stringify(loginStatus));
		} else {
			sessionStorage.removeItem("loginStatus");
		}
	}, [loginStatus]);

	const handleLoginClick = (e) => {
		e.preventDefault();
		setShowLoginModal(true);
	};

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
	 <div>
		<Navbar bg="dark" variant="dark">
		  	<Container>
			 	<Navbar.Brand as={Link} to="/">Car Scraper</Navbar.Brand>
			 	<Nav className="me-auto">
					{!loginStatus ? (
						<Nav.Link as={Link} href="#" onClick={handleLoginClick}>Login</Nav.Link>
						) : (
						<Nav.Link as={Link} href="#" onClick={handleLogout}>Logout</Nav.Link>
						)
					}
			 	</Nav>
				{loginStatus && (
					<Navbar.Text className="text-light">
						Hi, {loginStatus.username}!
					</Navbar.Text>
				)}
		  	</Container>
		</Navbar>
		
		<div style={{ margin: "1rem" }}>
			<LoginStatusContext.Provider value={[loginStatus, setLoginStatus]}>
				<Outlet />
			</LoginStatusContext.Provider>
		</div>

		<LoginModal 
			show={showLoginModal}
			onHide={() => setShowLoginModal(false)}
			onLogin={handleLogin}
		/>
	 </div>
  );
}

export default Layout;