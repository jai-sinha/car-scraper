import { useState } from "react";
import { Nav, Button, Form } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

function LoginModal({ show, onHide, onLogin }) {
	const [email_or_username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const navigate = useNavigate();

	const handleLogin = (e) => {
		e.preventDefault();
		// Call the onLogin function passed from parent
		onLogin({ email_or_username, password });
		// Reset form
		setUsername('');
		setPassword('');
		navigate('/');
	};

	const handleClose = () => {
		setUsername('');
		setPassword('');
		onHide();
	};

	if (!show) return null;

	return (
		<div 
			className="position-fixed top-0 start-0 end-0 bottom-0 d-flex align-items-center justify-content-center"
			style={{ zIndex: 1050 }}
		>
			<div 
				className="bg-white rounded w-100 mx-3" 
				style={{
					boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
					maxWidth: '500px'
				}}
			>
				<div className="py-3">
					<h4 className="text-center fw-semibold">
						Log In
					</h4>
					<div className="text-center small">
						<span>Don't have an account? </span>
						<Nav.Link 
							as={Link} 
							to="register" 
							onClick={handleClose} 
							style={{ color: '#007bff' }}
						>
							Sign up here
						</Nav.Link>
					</div>

					<Form onSubmit={handleLogin}>
						<Form.Label htmlFor="username">Username or Email</Form.Label>
						<Form.Control
							value={email_or_username}
							onChange={(e) => setUsername(e.target.value)}
							size="sm"
							required
						/>

						<Form.Label htmlFor="password">Password</Form.Label>
						<Form.Control
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							size="sm"
							required
							type="password"
							className="mb-3"
						/>
						{/* <div style={{
							marginBottom: '1.5rem',
							fontSize: '14px'
							}}>
							<span style={{ color: '#333' }}>(Forgot your password? </span>
							<a 
								href="#" 
								style={{
									color: '#007bff',
									textDecoration: 'none'
								}}
							>
								Click Here
							</a>
							<span style={{ color: '#333' }}>)</span>
						</div> */}
						<div className="d-flex gap-1 justify-content-center align-items-center">
							<Button
								onClick={handleLogin}
							>
								Log In
							</Button>
							<Button
								variant='secondary'
								onClick={handleClose}
							>
								Cancel
							</Button>
						</div>
					</Form>
				</div>
			</div>
		</div>
	);
}

export default LoginModal;