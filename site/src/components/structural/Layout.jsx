import { useLoginStatus } from "../contexts/LoginStatusContext";
import { Container, Nav, Navbar } from "react-bootstrap";
import { Link, Outlet } from "react-router-dom";
import LoginModal from "../auth/LoginModal"
import LogoutModal from "../auth/LogoutModal"

function Layout(props) {
	const { loginStatus, showLoginModal, setShowLoginModal, showLogoutModal, setShowLogoutModal, handleLogin, handleLogout } = useLoginStatus();

	const handleLoginClick = (e) => {
		e.preventDefault();
		setShowLoginModal(true);
	};

	const handleLogoutClick = (e) => {
		e.preventDefault();
		setShowLogoutModal(true);
	};

  return (
	 <div>
		<Navbar bg="dark" variant="dark">
		  	<Container>
			 	<Navbar.Brand as={Link} to="/">Car Scraper</Navbar.Brand>
			 	<Nav className="me-auto">
					<Nav.Link as={Link} to="/garage">Garage</Nav.Link>
					{!loginStatus ? (
						<Nav.Link as={Link} onClick={handleLoginClick}>Login</Nav.Link>
						) : (
						<Nav.Link as={Link} onClick={handleLogoutClick}>Logout</Nav.Link>
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
			<Outlet />
		</div>

		<LoginModal 
			show={showLoginModal}
			onHide={() => setShowLoginModal(false)}
			onLogin={handleLogin}
		/>
		<LogoutModal 
			show={showLogoutModal}
			onHide={() => setShowLogoutModal(false)}
			onLogout={handleLogout}
		/>
	 </div>
  );
}

export default Layout;