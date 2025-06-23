import React, { useState, useContext } from 'react';
import { Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LoginStatusContext from "../contexts/LoginStatusContext";

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

	// 	fetch(
	// 		"https://cs571api.cs.wisc.edu/rest/s25/hw6/register",
	// 		{
	// 			method: "POST",
	// 			headers: {
	// 			"Content-Type": "application/json",
	// 			"X-CS571-ID": CS571.getBadgerId(),
	// 			},
	// 			credentials: "include",
	// 			body: JSON.stringify({ username, pin }),
	// 		}
	// 	).then(res => {
	// 		if (res.status === 200) {
	// 			alert("Registration successful!");
	// 			setLoginStatus({ username }); // Store login info
	// 			sessionStorage.setItem("loginStatus", JSON.stringify({ username }));
	// 			navigate("/");
	// 		} else if (res.status === 409) {
	// 			alert("That username has already been taken!");
	// 		} else {
	// 			alert("An unexpected error occurred. Please try again.");
	// 		}
	// 	}).catch(error => {
	// 		alert(`Failed to register. Please check your internet connection. Error: ${error}`);
	// 	})
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