"""
Simple token-based auth utilities using itsdangerous for the Flask backend.
"""
from datetime import timedelta
from typing import Optional, Tuple
from flask import request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import config


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = getattr(config, 'SECRET_KEY', 'dev-secret-key')
    return URLSafeTimedSerializer(secret_key, salt='intellilearn-auth')


def hash_password(plain: str) -> str:
    return generate_password_hash(plain)


def verify_password(hash_value: str, plain: str) -> bool:
    return check_password_hash(hash_value, plain)


def create_token(user_id: int, email: str, role: str, lifetime: timedelta = timedelta(days=7)) -> str:
    s = _get_serializer()
    return s.dumps({'uid': user_id, 'email': email, 'role': role, 'exp': lifetime.total_seconds()})


def verify_token(token: str, max_age_seconds: Optional[int] = None) -> Optional[dict]:
    s = _get_serializer()
    try:
        data = s.loads(token, max_age=max_age_seconds or 7 * 24 * 3600)
        return data
    except (SignatureExpired, BadSignature):
        return None


def extract_bearer_token() -> Optional[str]:
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return None


