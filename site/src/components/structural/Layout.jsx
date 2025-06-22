import React, { useState, useEffect } from "react";
import { Container, Nav, Navbar, Button, Form } from "react-bootstrap";
import { Link, Outlet } from "react-router-dom";
import LoginStatusContext from "../contexts/LoginStatusContext";
import LoginModal from "../auth/LoginModal"

function Layout(props) {
  const storedLoginStatus = JSON.parse(sessionStorage.getItem("loginStatus"));
  const [loginStatus, setLoginStatus] = useState(storedLoginStatus || null);
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

  const handleLogin = (credentials) => {
	 console.log('Login attempted with:', credentials);
	 
	 // Here you would typically make an API call to authenticate
	 // For now, we'll simulate a successful login
	 const mockUser = {
		username: credentials.username,
		email: credentials.username.includes('@') ? credentials.username : `${credentials.username}@example.com`,
		loginTime: new Date().toISOString()
	 };
	 
	 setLoginStatus(mockUser);
	 setShowLoginModal(false);
	 
	 // You can add actual authentication logic here
	 // Example:
	 // try {
	 //   const response = await fetch('/api/login', {
	 //     method: 'POST',
	 //     headers: { 'Content-Type': 'application/json' },
	 //     body: JSON.stringify(credentials)
	 //   });
	 //   const userData = await response.json();
	 //   if (response.ok) {
	 //     setLoginStatus(userData);
	 //     setShowLoginModal(false);
	 //   } else {
	 //     alert('Login failed: ' + userData.message);
	 //   }
	 // } catch (error) {
	 //   alert('Login error: ' + error.message);
	 // }
  };

  const handleLogout = () => {
	 setLoginStatus(null);
  };

  return (
	 <div>
		<Navbar bg="dark" variant="dark">
		  <Container>
			 <Navbar.Brand as={Link} to="/">
				Car Scraper
			 </Navbar.Brand>
			 <Nav className="me-auto">
				<Nav.Link as={Link} to="/">Home</Nav.Link>
				{!loginStatus ? (
				  <>
					 <Nav.Link href="#" onClick={handleLoginClick}>Login</Nav.Link>
				  </>
				) : (
				  <Nav.Link href="#" onClick={handleLogout}>Logout</Nav.Link>
				)}
			 </Nav>
			 {loginStatus && (
				<Navbar.Text className="text-light">
				  Welcome, {loginStatus.username}!
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