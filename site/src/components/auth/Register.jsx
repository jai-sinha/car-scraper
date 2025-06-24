import React, { useState, useContext } from 'react';
import { Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LoginStatusContext from "../contexts/LoginStatusContext";

const API_URL = import.meta.env.VITE_API_URL;

function Register() {

	const [email, setEmail] = useState('');
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const navigate = useNavigate();
	const [loginStatus, setLoginStatus] = useContext(LoginStatusContext);

	const handleRegister = async (e) => {
		e.preventDefault();

		if (!username || !password || !email) {
			alert("You must provide an email, username and password!");
			return;
		}

		if (password !== confirmPassword) {
			alert("Your passwords do not match!");
			return;
		}

		const credentials = JSON.stringify({ email, username, password });
		console.log('Registration attempted with:', credentials);

		try {
			const response = await fetch(`${API_URL}/register`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: credentials
			});
			const userData = await response.json();
			console.log(userData);
			if (response.ok) {
				setLoginStatus(userData.user);
				navigate("/")
			} else {
				alert('Registration failed: ' + userData.error);
			}
			} catch (error) {
			alert('Registration error: ' + error.message);
		}

	};


	return (
	<>
		<h1>Register for My Cool App</h1>
		<Form onSubmit={handleRegister}>
			<Form.Group>
				<Form.Label htmlFor="emailInput">Email</Form.Label>
				<Form.Control id="emailInput" value={email} onChange={(e) => setEmail(e.target.value)} />
			</Form.Group>

			<Form.Group>
				<Form.Label htmlFor="usernameInput">Username</Form.Label>
				<Form.Control id="usernameInput" value={username} onChange={(e) => setUsername(e.target.value)} />
			</Form.Group>

			<Form.Group>
				<Form.Label htmlFor="passwordInput">Password</Form.Label>
				<Form.Control id="passwordInput" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
			</Form.Group>

			<Form.Group>
				<Form.Label htmlFor="confirmPasswordInput">Confirm Password</Form.Label>
				<Form.Control id="confirmPasswordInput" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
			</Form.Group>

			<br />
			<Button variant="primary" type="submit">
				Register
			</Button>
		</Form>

		<div>
			<h1>Account Benefits</h1>
			<p 		
			style={{				
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center',
			}}>
				You are goated.
			</p>
		</div>
	</>
	);
}

export default Register;