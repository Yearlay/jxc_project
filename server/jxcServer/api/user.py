from flask import Blueprint, jsonify
import db

user_bp = Blueprint('user', __name__)


# ──────────────────────────────────────────────────────────
# GET /api/user/list  用户列表（用于权限组添加成员）
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/list', methods=['GET'])
def user_list():
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT id, username, real_name, status
                FROM sys_user
                ORDER BY id
            ''')
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify(code=200, msg='success', data=[dict(r) for r in rows])
