from flask import Flask, jsonify, session, render_template, redirect, url_for, make_response, request
from database import get_db
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import logging
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.jinja_env.bytecode_cache = None
# App configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10485760))

# Initialize extensions
bcrypt = Bcrypt(app)
Session(app)
csrf = CSRFProtect(app)

# Rate Limiter 
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

@limiter.request_filter
def exempt_page_routes():
    return request.path in ['/my-resources', '/resources-v2', '/dashboard', '/learning', '/tasks-board']

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
    return render_template('dashboard/dashboard.html', active_page='dashboard', role=session.get('user_role'))

@app.route('/tasks-board')
def tasks_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('tasks/tasks.html', active_page='tasks', role=session.get('user_role'))

@app.route('/learning')
def learning_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('learning/learning.html', active_page='learning', role=session.get('user_role'))

@app.route('/resources')
def resources_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('resources/resources.html', active_page='resources', role=session.get('user_role'))

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
    try:
        user = db.execute('SELECT name, email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if user:
            return jsonify({'name': user['name'], 'email': user['email']})
        return jsonify({'error': 'Not found'}), 404
    finally:
        db.close()

@app.route('/api/admin/stats')
def admin_stats():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    try:
        total_users     = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_tasks     = db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        total_resources = db.execute('SELECT COUNT(*) FROM resources').fetchone()[0]
        total_topics    = db.execute('SELECT COUNT(*) FROM learning_progress').fetchone()[0]
        return jsonify({
            'total_users': total_users,
            'total_tasks': total_tasks,
            'total_resources': total_resources,
            'total_topics': total_topics
        })
    finally:
        db.close()

@app.route('/api/admin/users')
def admin_users():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    try:
        users = db.execute(
            'SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC'
        ).fetchall()
        def format_user(u):
            user = dict(u)
            if user.get('created_at'):
                user['created_at'] = user['created_at'].replace(' ', 'T') + 'Z'
            return user

        return jsonify({'users': [format_user(u) for u in users]})
    finally:
        db.close()

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Cannot delete your own account'}), 400
    db = get_db()
    try:
        user = db.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Delete uploaded files from disk
        resources = db.execute('SELECT file_path FROM resources WHERE user_id = ?', (user_id,)).fetchall()
        for r in resources:
            try:
                os.remove(r['file_path'])
            except OSError:
                pass

        # Cascade delete related data
        db.execute('DELETE FROM tasks WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM learning_progress WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM resources WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()

        return jsonify({'message': 'User deleted'})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=False)