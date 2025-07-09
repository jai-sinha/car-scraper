import { useState, useRef } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

function LoginModal({ show, onHide, onLogin }) {
	const [email_or_username, setEmailOrUsername] = useState('');
	const [password, setPassword] = useState('');
	const passwordRef = useRef();
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		await onLogin({ email_or_username, password });
		// Fix scrolling issue on submit by blurring the password input
		if (passwordRef.current) passwordRef.current.blur();
		if (window.location.pathname === '/register') {
			navigate('/');
		}
		resetForm();
	};

	const handleClose = () => {
		resetForm();
		onHide();
	};

	const resetForm = () => {
		setEmailOrUsername('');
		setPassword('');
	};

	return (
		<Modal 
			show={show} 
			onHide={handleClose} 
			enforceFocus={false}
			restoreFocus={false}
			centered>
			<Modal.Header closeButton>
				<div className="w-100 text-center">
					<Modal.Title>Log In</Modal.Title>
				</div>
			</Modal.Header>
			
			<Modal.Body>
				<div className="text-center mb-3">
					<span>Don't have an account? </span>
					<Link to="/register" onClick={handleClose} className="text-decoration-none">
						Sign up here
					</Link>
				</div>

				<Form onSubmit={handleSubmit}>
					<Form.Group className="mb-3">
						<Form.Label>Username or Email</Form.Label>
						<Form.Control
							type="text"
							value={email_or_username}
							onChange={(e) => setEmailOrUsername(e.target.value)}
							required
						/>
					</Form.Group>

					<Form.Group className="mb-3">
						<Form.Label>Password</Form.Label>
						<Form.Control
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							ref={passwordRef}
							required
						/>
					</Form.Group>
					<div className="d-flex justify-content-center gap-2">
						<Button variant="secondary" onClick={handleClose} type="button">
							Cancel
						</Button>
						<Button variant="primary" type="submit">
							Log In
						</Button>
					</div>
				</Form>
			</Modal.Body>
		</Modal>
	);
}

export default LoginModal;