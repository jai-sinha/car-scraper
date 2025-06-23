import { useState } from "react";
import { Nav, Button, Form } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

function LoginModal({ show, onHide, onLogin }) {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const navigate = useNavigate();

	const handleLogin = (e) => {
		e.preventDefault();
		// Call the onLogin function passed from parent
		onLogin({ username, password });
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
		<div style={{
		position: 'fixed',
		top: 0,
		left: 0,
		right: 0,
		bottom: 0,
		display: 'flex',
		alignItems: 'center',
		justifyContent: 'center',
		zIndex: 1050
		}}>
			<div style={{
			backgroundColor: 'white',
			borderRadius: '8px',
			boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
			width: '100%',
			maxWidth: '500px',
			margin: '0 1rem'
			}}>
				{/* Modal Body */}
				<div style={{
					paddingBottom: '1rem',
					paddingTop: "1rem"
				}}>
					<h2 style={{
						fontSize: '1.25rem',
						fontWeight: '600',
						textAlign: 'center',
					}}>
						Log In
					</h2>
					
					<div style={{
						textAlign: 'center',
						fontSize: '14px'
					}}>
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
						<Form.Label htmlFor="username">Username</Form.Label>
						<Form.Control
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							size="sm"
							placeholder=""
							required
						/>

						<div style={{ marginBottom: '1rem' }}>
						<Form.Label htmlFor="password">Password</Form.Label>
						<Form.Control
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							size="sm"
							placeholder=""
							required
						/>
						</div>
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
						<div style={{
						display: 'flex',
						gap: '.25rem',
						alignItems:'center',
						justifyContent: 'center',
						}}>
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