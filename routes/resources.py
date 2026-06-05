from flask import Blueprint, request, jsonify, session
from database import get_db
import os
from werkzeug.utils import secure_filename

resources_bp = Blueprint('resources', __name__)

# Allowed file types
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def login_required():
    return session.get('user_id')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# POST /upload 
@resources_bp.route('/upload', methods=['POST'])
def upload_file():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file type. Only PDF, DOC, DOCX, TXT allowed'}), 400

    db = get_db()
    try:
        # Secure the filename
        filename  = secure_filename(file.filename)
        file_path = os.path.join('static', 'uploads', filename)

        # Save file
        file.save(file_path)

        # Save to database
        db.execute(
            'INSERT INTO resources (user_id, file_name, file_path) VALUES (?, ?, ?)',
            (user_id, filename, file_path)
        )
        db.commit()

        return jsonify({'message': 'File uploaded successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# GET /resources 
@resources_bp.route('/resources', methods=['GET'])
def get_resources():
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        resources = db.execute(
            'SELECT * FROM resources WHERE user_id = ? ORDER BY uploaded_at DESC',
            (user_id,)
        ).fetchall()

        return jsonify({
            'resources': [dict(r) for r in resources]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()

# DELETE /resources/<id>
@resources_bp.route('/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    user_id = login_required()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    db = get_db()
    try:
        # Ownership check — IDOR prevention
        resource = db.execute(
            'SELECT * FROM resources WHERE id = ? AND user_id = ?',
            (resource_id, user_id)
        ).fetchone()

        if not resource:
            return jsonify({'message': 'Resource not found'}), 404

        # Delete file from storage
        if os.path.exists(resource['file_path']):
            os.remove(resource['file_path'])

        # Delete from database
        db.execute(
            'DELETE FROM resources WHERE id = ? AND user_id = ?',
            (resource_id, user_id)
        )
        db.commit()

        return jsonify({'message': 'Resource deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500
    finally:
        db.close()