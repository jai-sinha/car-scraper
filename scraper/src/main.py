from run_all import run_scrapers
from quart_cors import cors
from quart import Quart, request, jsonify, session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy.orm
from sqlalchemy.exc import IntegrityError
import redis
import json
import bcrypt
import re
from functools import wraps
from datetime import datetime, timezone

app = Quart(__name__)
app.secret_key = "secret key"
REDIS_HOST = "redis" # Docker service name for Redis

# Enable CORS for the app
app = cors(app, allow_origin="http://localhost:5173", allow_credentials=True)
# Database setup
DATABASE_URL = 'sqlite:///users.db'
engine = create_engine(DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))
Base = sqlalchemy.orm.declarative_base()

# User Model
class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	email = Column(String(120), unique=True, nullable=False, index=True)
	username = Column(String(50), unique=True, nullable=False, index=True)
	password_hash = Column(String(128), nullable=False)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	is_active = Column(Boolean, default=True)
	
	def __init__(self, email, username, password):
		self.email = email.strip().lower()
		self.username = username.strip()
		self.set_password(password)
	
	def set_password(self, password):
		"""Hash and set password"""
		salt = bcrypt.gensalt()
		self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
	
	def check_password(self, password):
		"""Check password against hash"""
		return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
	
	def to_dict(self, include_sensitive=False):
		"""Convert user to dictionary"""
		data = {
			'id': self.id,
			'email': self.email,
			'username': self.username,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'is_active': self.is_active
		}
		if include_sensitive:
			data['password_hash'] = self.password_hash
		return data
	
	@classmethod
	def find_by_email_or_username(cls, email_or_username):
		"""Find user by email or username"""
		session = Session()
		try:
			return session.query(cls).filter(
					(cls.email == email_or_username.lower()) | 
					(cls.username == email_or_username)
			).first()
		finally:
			session.close()
	
	@classmethod
	def create_user(cls, email, username, password):
		"""Create new user with validation - simpler approach"""
		session = Session()
		try:
			# Validate input first
			if not cls.validate_email(email):
				raise ValueError("Invalid email format")
			
			is_valid, msg = cls.validate_password(password)
			if not is_valid:
				raise ValueError(msg)
			
			if len(username.strip()) < 3 or len(username.strip()) > 50:
				raise ValueError("Username must be between 3 and 50 characters")
			
			# Begin explicit transaction
			session.begin()
			
			# Create user
			user = cls(email, username, password)
			session.add(user)
			session.flush()  # This assigns the ID but doesn't commit yet
			
			# Get the ID while still in transaction
			user_id = user.id
			
			# Commit the transaction
			session.commit()
			
			# Return a fresh instance from database
			return session.query(cls).filter(cls.id == user_id).first()
			
		except IntegrityError:
			session.rollback()
			# Check what specifically failed
			existing_user = session.query(cls).filter(
				(cls.email == email.strip().lower()) | 
				(cls.username == username.strip())
			).first()
			
			if existing_user:
				if existing_user.email == email.strip().lower():
					raise ValueError("Email already exists")
				else:
					raise ValueError("Username already exists")
			else:
				raise ValueError("Email or username already exists")
		except Exception as e:
			session.rollback()
			raise
		finally:
			session.close()
	
	@staticmethod
	def validate_email(email):
		"""Validate email format"""
		pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		return re.match(pattern, email) is not None
	
	@staticmethod
	def validate_password(password):
		"""Validate password strength"""
		if len(password) < 8:
			return False, "Password must be at least 8 characters long"
		if not re.search(r'[A-Za-z]', password):
			return False, "Password must contain at least one letter"
		if not re.search(r'\d', password):
			return False, "Password must contain at least one number"
		return True, "Valid password"

def get_user_by_id(user_id):
	"""Get user by ID"""
	session = Session()
	try:
		return session.query(User).filter(User.id == user_id).first()
	finally:
		session.close()

def login_required(f):
	"""Decorator to require login for protected routes"""
	@wraps(f)
	async def decorated_function(*args, **kwargs):  # Make this async
		if 'user_id' not in session:
			return jsonify({'error': 'Authentication required'}), 401
		return await f(*args, **kwargs)  # Add await here
	return decorated_function

@app.route('/register', methods=['POST'])
async def register():
	"""Register a new user"""
	try:
		data = await request.get_json()
		
		if not data:
			return jsonify({'error': 'No data provided'}), 400
		
		email = data.get('email', '')
		username = data.get('username', '')
		password = data.get('password', '')
		
		if not email or not username or not password:
			return jsonify({'error': 'Email, username, and password are required'}), 400
		
		# Create user (includes validation)
		user = User.create_user(email, username, password)
		
		# Log the user in
		session['user_id'] = user.id
		session['username'] = user.username
		
		return jsonify({
			'message': 'User registered successfully',
			'user': user.to_dict()
		}), 201
		
	except ValueError as e:
		print(f"Validation error: {e}")
		return jsonify({'error': str(e)}), 400
	except Exception as e:
		print(f"Registration error: {e}")
		import traceback
		traceback.print_exc()
		return jsonify({'error': 'Registration failed'}), 500
	
@app.route('/login', methods=['POST'])
async def login():
	"""Login user"""
	try:
		data = await request.get_json()
		
		if not data:
			return jsonify({'error': 'No data provided'}), 400
		
		email_or_username = data.get('email_or_username', '').strip()
		password = data.get('password', '')
		
		if not email_or_username or not password:
			return jsonify({'error': 'Email/username and password are required'}), 400
		
		# Find and authenticate user
		user = User.find_by_email_or_username(email_or_username)
		
		if not user or not user.check_password(password) or not user.is_active:
			return jsonify({'error': 'Invalid credentials'}), 401
		
		# Create session
		session['user_id'] = user.id
		session['username'] = user.username
		
		return jsonify({
			'message': 'Login successful',
			'user': user.to_dict()
		}), 200
		
	except Exception as e:
		return jsonify({'error': 'Login failed'}), 500

@app.route('/me', methods=['GET'])
@login_required
async def get_current_user():
	"""Get current user information"""
	try:
		user_id = session['user_id']
		user = get_user_by_id(user_id)
		
		if not user:
			return jsonify({'error': 'User not found'}), 404
		
		return jsonify({
			'user': user.to_dict()
		}), 200
		
	except Exception as e:
		return jsonify({'error': 'Failed to get user information'}), 500

@app.route('/delete_user', methods=['DELETE'])
@login_required
async def delete_user():
	"""Delete current user account"""
	try:
		data = await request.get_json()
		password = data.get('password', '') if data else ''
		
		if not password:
			return jsonify({'error': 'Password confirmation required'}), 400
		
		user_id = session['user_id']
		user = get_user_by_id(user_id)
		
		if not user or not user.check_password(password):
			return jsonify({'error': 'Invalid password'}), 401
		
		# Delete user
		db_session = Session()
		try:
			db_session.delete(user)
			db_session.commit()
		finally:
			db_session.close()
		
		# Clear session
		session.clear()
		return jsonify({'message': 'User account deleted successfully'}), 200
		
	except Exception as e:
		return jsonify({'error': 'Failed to delete user account'}), 500

@app.route('/logout', methods=['POST'])
@login_required
async def logout():
	"""Logout user"""
	session.clear()
	return jsonify({'message': 'Logged out successfully'}), 200

# Initialize database
@app.before_serving
async def startup():
	"""Create database tables"""
	Base.metadata.create_all(engine)

@app.route("/search", methods=["GET"])
async def get_search():
	query = request.args.get("query")
	
	try:
		results = await run_scrapers(query)
		# Convert to serializable format for Listing objects
		serializable_results = {}
		for key, value in results.items():
			if hasattr(value, '__dict__'):
				serializable_results[key] = value.__dict__
			else:
				serializable_results[key] = value
		
		return jsonify(serializable_results), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500
	
@app.route("/listings", methods=["GET"])
async def get_all_listings():
	"""Get all live listings from Redis"""
	try:
		r = redis.Redis(host="redis", port=6379, db=0)
		data = r.get("bat_listings")
		
		if not data:
			return jsonify({"error": "No listings found"}), 404
		
		dict_data = json.loads(data.decode("utf-8"))
		return jsonify(dict_data), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500
	
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)
