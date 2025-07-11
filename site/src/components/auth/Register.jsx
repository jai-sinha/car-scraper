import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Card } from 'react-bootstrap';
import { useLoginStatus } from "../contexts/LoginStatusContext";

function Register() {
	const [email, setEmail] = useState('');
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const { setShowLoginModal, handleRegister } = useLoginStatus();

	const handleSubmit = async (e) => {
		e.preventDefault();
		await handleRegister(email, username, password, confirmPassword);
	};

	return (
		<Container className="mt-5">
			<Row className="justify-content-center">
				<Col md={8} lg={6}>
					<Card>
						<Card.Body>
							<Card.Title className="text-center mb-4">
								<h2>Create Your Account</h2>
								<p className="text-muted">Join Car Scraper today</p>
							</Card.Title>

							<div className="text-center mb-3">
								<span>Already have an account? </span>
								<Button
									variant="link"
									className="p-0 align-baseline text-decoration-none"
									onClick={() => setShowLoginModal(true)}
								>
									Sign in here
								</Button>
							</div>

							<Form onSubmit={handleSubmit}>
								<Form.Group className="mb-3">
									<Form.Label htmlFor="emailInput">Email</Form.Label>
									<Form.Control 
										id="emailInput" 
										type="email"
										value={email} 
										onChange={(e) => setEmail(e.target.value)}
										required
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label htmlFor="usernameInput">Username</Form.Label>
									<Form.Control 
										id="usernameInput" 
										value={username} 
										onChange={(e) => setUsername(e.target.value)}
										required
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label htmlFor="passwordInput">Password</Form.Label>
									<Form.Control 
										id="passwordInput" 
										type="password" 
										value={password} 
										onChange={(e) => setPassword(e.target.value)}
										required
									/>
								</Form.Group>

								<Form.Group className="mb-4">
									<Form.Label htmlFor="confirmPasswordInput">Confirm Password</Form.Label>
									<Form.Control 
										id="confirmPasswordInput" 
										type="password" 
										value={confirmPassword} 
										onChange={(e) => setConfirmPassword(e.target.value)}
										required
									/>
								</Form.Group>

								<div className="d-grid">
									<Button variant="primary" type="submit" size="lg">
										Create Account
									</Button>
								</div>
							</Form>
						</Card.Body>
					</Card>
				</Col>
			</Row>

			<Row className="justify-content-center mt-4">
				<Col md={8} lg={6}>
					<Card className="bg-light">
						<Card.Body className="text-center">
							<Card.Title>Why Join Car Scraper?</Card.Title>
							<ul className="list-unstyled mt-3">
								<li className="mb-2">🚗 Save your favorite cars</li>
								<li className="mb-2">📊 Track price changes</li>
								<li className="mb-2">⭐ Be awesome!!</li>
							</ul>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
}

export default Register;