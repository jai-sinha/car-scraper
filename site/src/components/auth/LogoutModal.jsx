import { Button, Modal } from "react-bootstrap";

function LogoutModal({ show, onHide, onLogout }) {
	const handleClose = () => {
		onHide();
	};

	const handleLogout = (e) => {
		e.preventDefault();
		onLogout();
		onHide();
	};

	return (
		<Modal show={show} onHide={handleClose} centered>
			<Modal.Header closeButton>
				<div className="w-100 text-center">
					<Modal.Title>Log Out</Modal.Title>
				</div>
			</Modal.Header>

			<Modal.Body>
				<div className="text-center mb-3">
					<span>Are you sure you want to log out?</span>
				</div>
			</Modal.Body>

			<Modal.Footer className="d-flex justify-content-center gap-2">
				<Button variant="secondary" onClick={handleClose}>
					Cancel
				</Button>
				<Button variant="danger" onClick={handleLogout}>
					Log Out
				</Button>
			</Modal.Footer>
		</Modal>
	);
}

export default LogoutModal;