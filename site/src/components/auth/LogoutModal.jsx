import { Nav, Button, Form } from "react-bootstrap";
import { Link } from "react-router-dom";

function LogoutModal({ show, onHide }) {

	const handleClose = () => {
		onHide();
	};

	const handleLogout = () => {
		// do something
		console.log("Hey someone logged out") 
	}

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
						Log Out
					</h2>
					
					<div style={{
						textAlign: 'center',
						fontSize: '14px'
					}}>
						<span>Are you sure? </span>
					</div>

					<div style={{
					display: 'flex',
					gap: '.25rem',
					alignItems:'center',
					justifyContent: 'center',
					}}>
					<Button
						onClick={handleLogout}
					>
						Yeah I'm Sure
					</Button>
					<Button
						variant='secondary'
						onClick={handleClose}
					>
						No Wait I Want To Stay
					</Button>
					</div>
				</div>
				</div>
			</div>
  );
}

export default LogoutModal;