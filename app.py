from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# App configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10485760))

# Initialize extensions
bcrypt = Bcrypt(app)
Session(app)

# Rate Limiter 
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Error handlers
@app.errorhandler(429)
def rate_limit_exceeded(e):
    logger.warning(f'Rate limit exceeded: {e}')
    return jsonify({'message': 'Too many attempts. Please try again later.'}), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f'Server error: {e}')
    return jsonify({'message': 'Internal server error'}), 500

# Import routes
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.progress import progress_bp
from routes.resources import resources_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(resources_bp)

if __name__ == '__main__':
    app.run(debug=True)