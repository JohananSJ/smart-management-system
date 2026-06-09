from flask import Flask, jsonify, session
from database import get_db
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

from flask import render_template, session, redirect, url_for

# ── Page Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login')
def login_page():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('auth/login.html')

@app.route('/register')
def register_page():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('auth/register.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('dashboard/dashboard.html', active_page='dashboard')

@app.route('/tasks-board')
def tasks_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('tasks/tasks.html', active_page='tasks')

@app.route('/learning')
def learning_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('learning/learning.html', active_page='learning')

@app.route('/resources')
def resources_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('resources/resources.html', active_page='resources')

@app.route('/profile')
def profile_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('dashboard/profile.html', active_page='profile')

@app.route('/admin')
def admin_page():
    if not session.get('user_id'):
        return redirect('/login')
    if session.get('user_role') != 'admin':
        return redirect('/dashboard')
    return render_template('admin/admin.html', active_page='admin')

@app.route('/api/profile')
def api_profile():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    user = db.execute('SELECT name, email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user:
        return jsonify({'name': user['name'], 'email': user['email']})
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)