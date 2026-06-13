import re
from flask import Blueprint, request, jsonify, session
from database import get_db

tasks_bp = Blueprint('tasks', __name__)

from extensions import limiter

# ── Helper: check if user is logged in ─────────────────────────────────────────
def login_required():
    return session.get('user_id')

# ── GET /tasks ─────────────────────────────────────────────────────────────────
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        tasks = db.execute(
            'SELECT id, title, description, priority, due_date, status, created_at FROM tasks WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()

        return jsonify({
            'tasks': [dict(task) for task in tasks]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# ── POST /tasks ────────────────────────────────────────────────────────────────
@tasks_bp.route('/tasks', methods=['POST'])
@limiter.limit("30 per minute")
def create_task():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()

    title       = data.get('title', '').strip()
    description = data.get('description', '').strip()
    priority    = data.get('priority', 'medium').strip()
    due_date    = data.get('due_date', '').strip()
    status      = data.get('status', 'todo').strip()

    if not title:
        return jsonify({'message': 'Title is required'}), 400

    if len(title) > 200:
        return jsonify({'message': 'Title must be 200 characters or less'}), 400

    if len(description) > 2000:
        return jsonify({'message': 'Description must be 2000 characters or less'}), 400

    if priority not in ['low', 'medium', 'high']:
        return jsonify({'message': 'Invalid priority'}), 400

    if status not in ['todo', 'in_progress', 'done']:
        return jsonify({'message': 'Invalid status'}), 400

    if due_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
        return jsonify({'message': 'due_date must be in YYYY-MM-DD format'}), 400

    db = get_db()
    try:
        db.execute(
            '''INSERT INTO tasks
               (user_id, title, description, priority, due_date, status)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, title, description, priority, due_date, status)
        )
        db.commit()

        return jsonify({'message': 'Task created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# ── PUT /tasks/<id> ────────────────────────────────────────────────────────────
@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@limiter.limit("30 per minute")
def update_task(task_id):
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        # Ownership check — IDOR prevention
        task = db.execute(
            'SELECT id, title, description, priority, due_date, status FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id)
        ).fetchone()

        if not task:
            return jsonify({'message': 'Task not found'}), 404

        data = request.get_json()

        title       = data.get('title', task['title']).strip()
        description = data.get('description', task['description'])
        priority    = data.get('priority', task['priority'])
        due_date    = data.get('due_date', task['due_date'])
        status      = data.get('status', task['status'])

        if not title:
            return jsonify({'message': 'Title is required'}), 400

        if len(title) > 200:
            return jsonify({'message': 'Title must be 200 characters or less'}), 400

        if description and len(description) > 2000:
            return jsonify({'message': 'Description must be 2000 characters or less'}), 400

        if priority not in ['low', 'medium', 'high']:
            return jsonify({'message': 'Invalid priority'}), 400

        if status not in ['todo', 'in_progress', 'done']:
            return jsonify({'message': 'Invalid status'}), 400

        if due_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
            return jsonify({'message': 'due_date must be in YYYY-MM-DD format'}), 400

        db.execute(
            '''UPDATE tasks
               SET title=?, description=?, priority=?, due_date=?, status=?
               WHERE id=? AND user_id=?''',
            (title, description, priority, due_date, status, task_id, user_id)
        )
        db.commit()

        return jsonify({'message': 'Task updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# ── DELETE /tasks/<id> ─────────────────────────────────────────────────────────
@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@limiter.limit("30 per minute")
def delete_task(task_id):
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        # Ownership check — IDOR prevention
        task = db.execute(
            'SELECT id FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id)
        ).fetchone()

        if not task:
            return jsonify({'message': 'Task not found'}), 404

        db.execute(
            'DELETE FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id)
        )
        db.commit()

        return jsonify({'message': 'Task deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()