import jwt
from functools import wraps
from flask import request, jsonify, current_app
from .extensions import db
from .models.user import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, current_app.config['JWT_SECRET'], algorithms=['HS256']
            )
            user = db.session.get(User, payload['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired — please log in again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(user, *args, **kwargs)
    return decorated
