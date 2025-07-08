import { Button } from "react-bootstrap";

function LogoutModal({ show, onHide, onLogout }) {

	const handleClose = () => {
		onHide();
	};

	const handleLogout = (e) => {
		e.preventDefault();
		onLogout();
		onHide();
	}

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
				{/* Modal Body */}
				<div className="py-3">
					<h4 className="text-center fw-semibold">
						Log Out
					</h4>
					
					<div className="text-center small mb-3">
						<span>Are you sure?</span>
					</div>

					<div className="d-flex gap-1 justify-content-center align-items-center">
						<Button
							onClick={handleLogout}
						>
							Yeah
						</Button>
						<Button
							variant='secondary'
							onClick={handleClose}
						>
							Nah
						</Button>
					</div>
				</div>
			</div>
		</div>
  );
}

export default LogoutModal;