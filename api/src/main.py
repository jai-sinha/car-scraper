from run_all import run_search_scrapers
from scheduler import run_scrapers
from quart_cors import cors
from quart import Quart, request, jsonify, session
import asyncpg
import bcrypt
import re
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, timezone

load_dotenv()

app = Quart(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

PG_CONN = {
	"host": os.environ.get("PG_HOST"),
	"database": os.environ.get("PG_DATABASE"),
	"user": os.environ.get("PG_USER"),
	"password": os.environ.get("PG_PASSWORD")
}

app = cors(app, allow_origin="http://localhost:5173", allow_credentials=True)

# User helper functions
async def validate_email(email):
	"""Validate email format"""
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return re.match(pattern, email) is not None

async def validate_password(password):
	"""Validate password strength"""
	if len(password) < 8:
		return False, "Password must be at least 8 characters long"
	if not re.search(r'[A-Za-z]', password):
		return False, "Password must contain at least one letter"
	if not re.search(r'\d', password):
		return False, "Password must contain at least one number"
	return True, "Valid password"

async def hash_password(password):
	"""Hash password"""
	salt = bcrypt.gensalt()
	hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
	return hashed.decode('utf-8')  # Convert bytes to string

async def check_password(password, password_hash):
	"""Check password against hash"""
	try:
		# Convert string back to bytes for bcrypt
		if isinstance(password_hash, str):
			password_hash = password_hash.encode('utf-8')
		
		return bcrypt.checkpw(password.encode('utf-8'), password_hash)
	except Exception as e:
		print(f"Password check error: {e}")
		return False

async def find_user_by_email_or_username(email_or_username):
	"""Find user by email or username"""
	conn = await asyncpg.connect(**PG_CONN)
	try:
		user = await conn.fetchrow("""
			SELECT id, email, username, password_hash, created_at, is_active
			FROM users 
			WHERE email = $1 OR username = $2
		""", email_or_username.lower(), email_or_username)
		return user
	finally:
		await conn.close()

async def get_user_by_id(user_id):
	"""Get user by ID"""
	conn = await asyncpg.connect(**PG_CONN)
	try:
		user = await conn.fetchrow("""
			SELECT id, email, username, password_hash, created_at, is_active
			FROM users 
			WHERE id = $1
		""", user_id)
		return user
	finally:
		await conn.close()

async def create_user(email, username, password):
	"""Create new user with validation"""
	# Validate input
	if not await validate_email(email):
		raise ValueError("Invalid email format")
	
	is_valid, msg = await validate_password(password)
	if not is_valid:
		raise ValueError(msg)
	
	if len(username.strip()) < 3 or len(username.strip()) > 50:
		raise ValueError("Username must be between 3 and 50 characters")
	
	conn = await asyncpg.connect(**PG_CONN)
	try:
		# Check if user already exists
		existing = await conn.fetchrow("""
			SELECT id FROM users WHERE email = $1 OR username = $2
		""", email.strip().lower(), username.strip())
		
		if existing:
			# Check which field conflicts
			email_exists = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email.strip().lower())
			if email_exists:
					raise ValueError("Email already exists")
			else:
					raise ValueError("Username already exists")
		
		# Hash password and create user
		password_hash = await hash_password(password)
		user_id = await conn.fetchval("""
			INSERT INTO users (email, username, password_hash, created_at, is_active)
			VALUES ($1, $2, $3, $4, $5)
			RETURNING id
		""", email.strip().lower(), username.strip(), password_hash, datetime.now(timezone.utc), True)
		
		# Return the created user
		user = await conn.fetchrow("""
			SELECT id, email, username, password_hash, created_at, is_active
			FROM users WHERE id = $1
		""", user_id)
		return user
		
	finally:
		await conn.close()

def login_required(f):
	"""Decorator to require login for protected routes"""
	@wraps(f)
	async def decorated_function(*args, **kwargs):
		if 'user_id' not in session:
			return jsonify({'error': 'Authentication required'}), 401
		return await f(*args, **kwargs)
	return decorated_function

def user_to_dict(user, include_sensitive=False):
	"""Convert user record to dictionary"""
	if not user:
		return None
	
	data = {
		'id': user['id'],
		'email': user['email'],
		'username': user['username'],
		'created_at': user['created_at'].isoformat() if user['created_at'] else None,
		'is_active': user['is_active']
	}
	if include_sensitive:
		data['password_hash'] = user['password_hash']
	return data

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
		user = await create_user(email, username, password)
		
		# Log the user in
		session['user_id'] = user['id']
		session['username'] = user['username']
		
		return jsonify({
			'message': 'User registered successfully',
			'user': user_to_dict(user)
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
		user = await find_user_by_email_or_username(email_or_username)
		
		if not user or not await check_password(password, user['password_hash']) or not user['is_active']:
			return jsonify({'error': 'Invalid credentials'}), 401
		
		# Create session
		session['user_id'] = user['id']
		session['username'] = user['username']
		
		return jsonify({
			'message': 'Login successful',
			'user': user_to_dict(user)
		}), 200
		
	except Exception as e:
		return jsonify({'error': 'Login failed'}), 500

@app.route('/me', methods=['GET'])
@login_required
async def get_current_user():
	"""Get current user information"""
	try:
		user_id = session['user_id']
		user = await get_user_by_id(user_id)
		
		if not user:
			return jsonify({'error': 'User not found'}), 404
		
		return jsonify({
			'user': user_to_dict(user)
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
		user = await get_user_by_id(user_id)
		
		if not user or not await check_password(password, user['password_hash']):
			return jsonify({'error': 'Invalid password'}), 401
		
		# Delete user
		conn = await asyncpg.connect(**PG_CONN)
		try:
			await conn.execute("DELETE FROM users WHERE id = $1", user_id)
		finally:
			await conn.close()
		
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

@app.before_serving
async def startup():
	"""Create user and listing tables"""
	conn = await asyncpg.connect(**PG_CONN)
	try:
		# Users
		await conn.execute("""
			CREATE TABLE IF NOT EXISTS users (
				id SERIAL PRIMARY KEY,
				email VARCHAR(120) UNIQUE NOT NULL,
				username VARCHAR(50) UNIQUE NOT NULL,
				password_hash TEXT NOT NULL,
				created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
				is_active BOOLEAN DEFAULT TRUE
			)
		""")
		await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
		await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")

		# Live listings
		await conn.execute("""
			CREATE TABLE IF NOT EXISTS live_listings (
				url TEXT PRIMARY KEY,
				title TEXT,
				image TEXT,
				time TIMESTAMP WITH TIME ZONE,
				price TEXT,
				year INTEGER,
				scraped_at TIMESTAMP WITH TIME ZONE,
				keywords TSVECTOR
			)
		""")

		# Temp listings
		await conn.execute("""
			CREATE TABLE IF NOT EXISTS temp_listings (
				url TEXT PRIMARY KEY,
				title TEXT,
				image TEXT,
				time TIMESTAMP WITH TIME ZONE,
				price TEXT,
				year INTEGER,
				scraped_at TIMESTAMP WITH TIME ZONE,
				keywords TSVECTOR
			)
		""")

		# Closed listings
		await conn.execute("""
			CREATE TABLE IF NOT EXISTS closed_listings (
				url TEXT PRIMARY KEY,
				title TEXT,
				image TEXT,
				price TEXT,
				year INTEGER,
				closed_at TIMESTAMP WITH TIME ZONE,
				keywords TSVECTOR
			)
		""")

		# Saved listings
		await conn.execute("""
			CREATE TABLE IF NOT EXISTS saved_listings (
				user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
				url TEXT REFERENCES live_listings(url) ON DELETE CASCADE,
				title TEXT,
				image TEXT,
				time TIMESTAMP WITH TIME ZONE,
				price TEXT,
				year INTEGER,
				saved_at TIMESTAMP WITH TIME ZONE,
				PRIMARY KEY (user_id, url)
			)
		""")
	finally:
		await conn.close()

@app.route("/search", methods=["GET"])
async def get_search():
	"""Search for listings using PostgreSQL full-text search"""
	query = str(request.args.get("query")).lower()

	try:
		results = await run_search_scrapers(query)
		return jsonify(results), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@app.route("/db_search", methods=["GET"])
async def get_db_search():
	"""Search for listings using PostgreSQL full-text search"""
	query = str(request.args.get("query")).lower()

	try:
		conn = await asyncpg.connect(**PG_CONN)
		try:
			rows = await conn.fetch("""
				SELECT title, url, image, time, price, year, scraped_at, keywords
				FROM live_listings
				WHERE keywords @@ plainto_tsquery('english', $1)
				ORDER BY time DESC
			""", query)
		finally:
			await conn.close()
		if not rows:
			return jsonify({"error": "No listings found"}), 404
		
		# Convert rows to a dictionary format
		listings = {}
		for row in rows:
			title, url, image, time_rem, price, year, scraped_at, keywords = row
			listings[title] = {
				"title": title,
				"url": url,
				"image": image,
				"time": time_rem,
				"price": price,
				"year": year,
				"keywords": keywords.split() if keywords else [],
				"scraped_at": scraped_at.isoformat() if scraped_at else None
			}

		return jsonify(listings), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500
	
@app.route("/listings", methods=["GET"])
async def get_all_listings():
	"""Get all live listings from PostgreSQL using asyncpg"""
	refresh = request.args.get("refresh")
	if refresh and refresh.lower() == "true":
		try:
			await run_scrapers()  # Run the scraper to refresh data
		except Exception as e:
			return jsonify({"error": str(e)}), 500

	try:
		conn = await asyncpg.connect(**PG_CONN)
		try:
			rows = await conn.fetch("""
				SELECT title, url, image, time, price, year, scraped_at
				FROM live_listings
				ORDER BY time DESC
			""")
		finally:
			await conn.close()

		if not rows:
			return jsonify({"error": "No listings found"}), 404

		# Convert rows to a dictionary format
		listings = {}
		for row in rows:
			title, url, image, time_rem, price, year, scraped_at = row
			listings[title] = {
				"title": title,
				"url": url,
				"image": image,
				"time": time_rem,
				"price": price,
				"year": year,
				"scraped_at": scraped_at.isoformat() if scraped_at else None
			}

		return jsonify(listings), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@app.route("/save", methods=["POST"])
@login_required
async def save_listing():
	"""Save a listing to the current user's garage"""
	data = await request.get_json()
	url = data.get("url", "")
	if not url:
		return jsonify({"error": "URL is required"}), 400
	
	user_id = session['user_id']
	if not user_id:
		return jsonify({'error': 'User not found'}), 401
	
	saved_at = datetime.now(timezone.utc)

	try:
		conn = await asyncpg.connect(**PG_CONN)

		try:
			# Fetch listing data from live_listings
			listing = await conn.fetchrow("""
				SELECT title, url, image, time, price, year, keywords
				FROM live_listings WHERE url = $1
			""", url)
			if not listing:
				return jsonify({"error": "Listing not found"}), 404

			# Insert into saved_listings
			await conn.execute("""
				INSERT INTO saved_listings (user_id, url, title, image, time, price, year, saved_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
				ON CONFLICT (user_id, url) DO NOTHING
			""", user_id, listing['url'], listing['title'], listing['image'], listing['time'],
				listing['price'], listing['year'], saved_at)
		
		finally:
			await conn.close()

		return jsonify({
			'message': 'Login successful',
			'car': dict(listing)
		}), 201

	except Exception as e:
		return jsonify({"error": str(e)}), 500
	
@app.route("/garage", methods=["GET"])
@login_required
async def get_garage():
	"""Get all saved listings for the current user"""
	user_id = session.get('user_id')
	if not user_id:
		return jsonify({'error': 'User not found'}), 401
	
	try:
		conn = await asyncpg.connect(**PG_CONN)
		try:
			rows = await conn.fetch("""
				SELECT title, url, image, time, price, year
				FROM saved_listings WHERE user_id = $1
				ORDER BY saved_at DESC
			""", user_id)
		finally:
			await conn.close()

		if not rows:
			return {}, 200

		# Convert rows to a dictionary format
		listings = {}
		for row in rows:
			title, url, image, time_rem, price, year = row
			listings[title] = {
				"title": title,
				"url": url,
				"image": image,
				"time": time_rem,
				"price": price,
				"year": year,
			}

		return jsonify(listings), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500
	
@app.route("/delete_saved_listing", methods=["DELETE"])
@login_required
async def delete_saved_listing():
	"""Delete a saved listing from the user's garage"""
	data = await request.get_json()
	url = data.get("url", "")
	if not url:
		return jsonify({"error": "URL is required"}), 400
	
	user_id = session.get('user_id')
	if not user_id:
		return jsonify({'error': 'User not found'}), 401
	
	try:
		conn = await asyncpg.connect(**PG_CONN)
		try:
			result = await conn.execute("""
				DELETE FROM saved_listings WHERE user_id = $1 AND url = $2
			""", user_id, url)
			
			if result == "DELETE 0":
				return jsonify({"error": "Listing not found in garage"}), 404
			
		finally:
			await conn.close()

		return jsonify({"message": "Listing deleted successfully"}), 200
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)