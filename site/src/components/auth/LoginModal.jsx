import { useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

function LoginModal({ show, onHide, onLogin }) {
	const [email_or_username, setEmailOrUsername] = useState('');
	const [password, setPassword] = useState('');
	const navigate = useNavigate();

	const handleSubmit = (e) => {
		e.preventDefault();
		onLogin({ email_or_username, password });
		resetForm();
		navigate('/');
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
		<Modal show={show} onHide={handleClose} centered>
			<Modal.Header closeButton>
					<Modal.Title>Log In</Modal.Title>
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
									required
							/>
						</Form.Group>
					</Form>
			</Modal.Body>

			<Modal.Footer className="d-flex justify-content-center gap-2">
					<Button variant="secondary" onClick={handleClose}>
						Cancel
					</Button>
					<Button variant="primary" onClick={handleSubmit}>
						Log In
					</Button>
			</Modal.Footer>
		</Modal>
	);
}

export default LoginModal;