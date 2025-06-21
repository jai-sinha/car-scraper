import listing
from run_all import run_scrapers
from quart import Quart, request, jsonify
from quart_cors import cors
from quart_sqlalchemy import QuartSQLAlchemy
import bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone

app = Quart(__name__)
app = cors(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = QuartSQLAlchemy(app)

# User model
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password_hash = db.Column(db.String(100), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

	def check_password(self, password):
		return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

	def set_password(self, password):
		self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# JWT decorator for protected routes
def token_required(f):
	@wraps(f)
	async def decorated(*args, **kwargs):
		token = request.headers.get('Authorization')
		if not token:
			return jsonify({'error': 'Token is missing'}), 401
		
		try:
			# Remove 'Bearer ' prefix if present
			if token.startswith('Bearer '):
					token = token[7:]
			
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
			current_user_id = data['user_id']
			current_user = User.query.get(current_user_id)
			if not current_user:
					return jsonify({'error': 'Invalid token'}), 401
		except jwt.ExpiredSignatureError:
			return jsonify({'error': 'Token has expired'}), 401
		except jwt.InvalidTokenError:
			return jsonify({'error': 'Invalid token'}), 401
		
		return await f(current_user, *args, **kwargs)
	return decorated

# Auth routes
@app.route("/auth/register", methods=["POST"])
async def register():
	data = await request.get_json()
	email = data.get('email')
	password = data.get('password')
	
	if not email or not password:
		return jsonify({'error': 'Email and password required'}), 400
	
	# Check if user exists
	if User.query.filter_by(email=email).first():
		return jsonify({'error': 'User already exists'}), 400
	
	# Create new user
	user = User(email=email)
	user.set_password(password)
	db.session.add(user)
	db.session.commit()
	
	return jsonify({'message': 'User created successfully'}), 201

@app.route("/auth/login", methods=["POST"])
async def login():
	data = await request.get_json()
	email = data.get('email')
	password = data.get('password')
	
	if not email or not password:
		return jsonify({'error': 'Email and password required'}), 400
	
	user = User.query.filter_by(email=email).first()
	
	if user and user.check_password(password):
		# Create JWT token
		token_data = {
			'user_id': user.id,
			'exp': datetime.now(timezone.utc) + timedelta(days=30)  # Token expires in 30 days
		}
		token = jwt.encode(token_data, app.config['SECRET_KEY'], algorithm='HS256')
		
		return jsonify({
			'token': token,
			'user': {
					'id': user.id,
					'email': user.email
			}
		})
	
	return jsonify({'error': 'Invalid credentials'}), 401

@app.route("/auth/me", methods=["GET"])
@token_required
async def get_current_user(current_user):
	return jsonify({
		'user': {
			'id': current_user.id,
			'email': current_user.email,
			'created_at': current_user.created_at.isoformat()
		}
	})


@app.route("/search", methods=["GET"])
async def get_search():
	make = request.args.get("make")
	model = request.args.get("model")
	generation = request.args.get("generation")
	car = listing.Car(make, model, generation)
	
	# Make sure at least these parameters exist
	if not make or not model:
		return jsonify({"error": "Missing parameters"}), 400
	
	try:
		results = await run_scrapers(car)
		
		# Convert to serializable format for Car objects
		serializable_results = {}
		for key, value in results.items():
			if hasattr(value, '__dict__'):
				serializable_results[key] = value.__dict__
			else:
				serializable_results[key] = value
		
		return jsonify(serializable_results)
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500

# Create tables before first request
@app.before_serving
async def create_tables():
	db.create_all()

if __name__ == "__main__":
	app.run(debug=True, port=5000)
	