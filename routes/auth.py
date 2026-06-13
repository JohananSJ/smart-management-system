from flask import Blueprint, request, jsonify, session
from database import get_db
import re
import logging
import secrets

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

from app import limiter, bcrypt

# Helper: validate email format 
def is_valid_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email)

# Helper: validate password strength
def is_valid_password(password):
    return len(password) >= 6

# Helper: sanitize input
def sanitize_input(value):
    if not isinstance(value, str):
        return ''
    return value.strip()

# POST /register
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    data = request.get_json()

    # Sanitize inputs
    name     = sanitize_input(data.get('name', ''))
    email    = sanitize_input(data.get('email', '')).lower()
    password = data.get('password', '')
    confirm  = data.get('confirm_password', '')

    if not name or not email or not password or not confirm:
        return jsonify({'message': 'All fields are required'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if not is_valid_password(password):
        return jsonify({'message': 'Password must be at least 6 characters'}), 400

    if password != confirm:
        return jsonify({'message': 'Passwords do not match'}), 400

    db = get_db()
    try:
        existing = db.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()

        if existing:
            logger.warning(f'Registration attempt with existing email: {email}')
            return jsonify({'message': 'Email already registered'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        db.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, hashed_password, 'user')
        )
        db.commit()

        logger.info(f'New user registered: {email}')
        return jsonify({'message': 'Registration successful'}), 201

    except Exception as e:
        logger.error(f'Registration error: {e}')
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# POST /login
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()

    email    = sanitize_input(data.get('email', '')).lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    db = get_db()
    try:
        user = db.execute(
            'SELECT id, name, email, password, role FROM users WHERE email = ?', (email,)
        ).fetchone()

        if not user or not bcrypt.check_password_hash(user['password'], password):
            logger.warning(f'Failed login attempt for email: {email}')
            return jsonify({'message': 'Invalid email or password'}), 401

        session.clear()
        session['user_id']    = user['id']
        session['user_name']  = user['name']
        session['user_email'] = user['email']
        session['user_role']  = user['role']
        session.sid = secrets.token_hex(32)

        logger.info(f'Successful login: {email}')
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id':   user['id'],
                'name': user['name'],
                'role': user['role']
            }
        }), 200

    except Exception as e:
        logger.error(f'Login error: {e}')
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# POST /logout 
@auth_bp.route('/logout', methods=['POST'])
def logout():
    email = session.get('user_email', 'unknown')
    session.clear()
    logger.info(f'User logged out: {email}')
    return jsonify({'message': 'Logged out successfully'}), 200