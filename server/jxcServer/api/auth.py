from flask import Blueprint, request, jsonify, g
from typing import Optional
import hashlib
import jwt
import config
import db

auth_bp = Blueprint('auth', __name__)


def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def _make_token(user_id: int, username: str, role: str) -> str:
    """生成长期有效的 JWT token"""
    payload = {
        'user_id':  user_id,
        'username': username,
        'role':     role,
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm='HS256')


def verify_token(token: str) -> Optional[dict]:
    """校验 token，返回 payload 或 None"""
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None


# ──────────────────────────────────────────────────────────
# POST /api/login
# ──────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify(code=400, msg='用户名和密码不能为空'), 400

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, username, role, real_name FROM sys_user '
                'WHERE username = %s AND password = %s AND status = 1',
                (username, _md5(password)),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user:
        return jsonify(code=401, msg='用户名或密码错误'), 401

    token = _make_token(user['id'], user['username'], user['role'])
    return jsonify(
        code=200,
        msg='登录成功',
        data={
            'token':     token,
            'username':  user['username'],
            'real_name': user['real_name'],
            'role':      user['role'],
        },
    )
