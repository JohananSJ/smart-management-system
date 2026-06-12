from flask import Blueprint, request, jsonify, session
from database import get_db

progress_bp = Blueprint('progress', __name__)

# Helper: check if user is logged in 
def login_required():
    return session.get('user_id')

# GET /progress 
@progress_bp.route('/progress', methods=['GET'])
def get_progress():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        progress = db.execute(
            'SELECT * FROM learning_progress WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()

        return jsonify({
            'progress': [dict(p) for p in progress]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# POST /progress 
@progress_bp.route('/progress', methods=['POST'])
def create_progress():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()

    topic_name            = data.get('topic_name', '').strip()
    status                = data.get('status', 'in_progress').strip()
    notes                 = data.get('notes', '').strip()
    completion_percentage = data.get('completion_percentage', 0)

    if not topic_name:
        return jsonify({'message': 'Topic name is required'}), 400

    if len(topic_name) > 200:
        return jsonify({'message': 'Topic name must be 200 characters or less'}), 400

    if len(notes) > 2000:
        return jsonify({'message': 'Notes must be 2000 characters or less'}), 400

    if status not in ['in_progress', 'completed']:
        return jsonify({'message': 'Invalid status'}), 400

    if not isinstance(completion_percentage, (int, float)) or not 0 <= completion_percentage <= 100:
        return jsonify({'message': 'Completion percentage must be between 0 and 100'}), 400

    completion_percentage = int(completion_percentage)

    db = get_db()
    try:
        db.execute(
            '''INSERT INTO learning_progress
               (user_id, topic_name, status, notes, completion_percentage)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, topic_name, status, notes, completion_percentage)
        )
        db.commit()

        return jsonify({'message': 'Progress created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# PUT /progress/<id> 
@progress_bp.route('/progress/<int:progress_id>', methods=['PUT'])
def update_progress(progress_id):
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        # Ownership check — IDOR prevention
        progress = db.execute(
            'SELECT * FROM learning_progress WHERE id = ? AND user_id = ?',
            (progress_id, user_id)
        ).fetchone()

        if not progress:
            return jsonify({'message': 'Progress not found'}), 404

        data = request.get_json()

        topic_name            = data.get('topic_name', progress['topic_name']).strip()
        status                = data.get('status', progress['status'])
        notes                 = data.get('notes', progress['notes'])
        completion_percentage = data.get('completion_percentage', progress['completion_percentage'])

        if not topic_name:
            return jsonify({'message': 'Topic name is required'}), 400

        if len(topic_name) > 200:
            return jsonify({'message': 'Topic name must be 200 characters or less'}), 400

        if notes and len(notes) > 2000:
            return jsonify({'message': 'Notes must be 2000 characters or less'}), 400

        if status not in ['in_progress', 'completed']:
            return jsonify({'message': 'Invalid status'}), 400

        if not isinstance(completion_percentage, (int, float)) or not 0 <= completion_percentage <= 100:
            return jsonify({'message': 'Completion percentage must be between 0 and 100'}), 400

        completion_percentage = int(completion_percentage)

        db.execute(
            '''UPDATE learning_progress
               SET topic_name=?, status=?, notes=?, completion_percentage=?
               WHERE id=? AND user_id=?''',
            (topic_name, status, notes, completion_percentage, progress_id, user_id)
        )
        db.commit()

        return jsonify({'message': 'Progress updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()
# DELETE /progress/<id>
@progress_bp.route('/progress/<int:progress_id>', methods=['DELETE'])
def delete_progress(progress_id):
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        # Ownership check — IDOR prevention
        progress = db.execute(
            'SELECT * FROM learning_progress WHERE id = ? AND user_id = ?',
            (progress_id, user_id)
        ).fetchone()

        if not progress:
            return jsonify({'message': 'Progress not found'}), 404

        db.execute(
            'DELETE FROM learning_progress WHERE id = ? AND user_id = ?',
            (progress_id, user_id)
        )
        db.commit()

        return jsonify({'message': 'Progress deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()        