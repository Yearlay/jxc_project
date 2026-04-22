import hashlib
from flask import Blueprint, jsonify, request
import db

user_bp = Blueprint('user', __name__)


def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


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


# ──────────────────────────────────────────────────────────
# GET /api/user/manage/list  用户管理列表（含仓库/片区信息）
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/manage/list', methods=['GET'])
def manage_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            sql = '''
                SELECT u.id, u.username, u.real_name, u.role, u.status,
                       u.warehouse_ids,
                       ARRAY(SELECT name FROM biz_warehouse WHERE id = ANY(u.warehouse_ids)) AS warehouse_names,
                       u.area_ids,
                       ARRAY(SELECT name FROM biz_area WHERE id = ANY(u.area_ids)) AS area_names
                FROM sys_user u
            '''
            params = []
            if keyword:
                sql += ' WHERE u.username ILIKE %s'
                params.append(f'%{keyword}%')
            sql += ' ORDER BY u.id'
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify(code=200, msg='success', data=[dict(r) for r in rows])


# ──────────────────────────────────────────────────────────
# POST /api/user/manage/add  新建用户
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/manage/add', methods=['POST'])
def manage_add():
    body = request.get_json(silent=True) or {}
    username      = (body.get('username') or '').strip()
    password      = (body.get('password') or '').strip()
    real_name     = (body.get('real_name') or '').strip()
    role          = body.get('role', 'staff')
    status        = body.get('status', 1)
    warehouse_ids = body.get('warehouse_ids') or []
    area_ids      = body.get('area_ids') or []

    if not username:
        return jsonify(code=400, msg='用户名不能为空'), 400
    if not password:
        return jsonify(code=400, msg='密码不能为空'), 400

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM sys_user WHERE username = %s', (username,))
            if cur.fetchone():
                return jsonify(code=400, msg='用户名已存在'), 400
            cur.execute(
                '''INSERT INTO sys_user (username, password, real_name, role, status, warehouse_ids, area_ids)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                (username, _md5(password), real_name, role, status, warehouse_ids, area_ids)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    finally:
        conn.close()
    return jsonify(code=200, msg='创建成功', data={'id': new_id})


# ──────────────────────────────────────────────────────────
# PUT /api/user/manage/update  修改用户（不改密码）
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/manage/update', methods=['PUT'])
def manage_update():
    body = request.get_json(silent=True) or {}
    uid           = body.get('id')
    username      = (body.get('username') or '').strip()
    real_name     = (body.get('real_name') or '').strip()
    role          = body.get('role', 'staff')
    status        = body.get('status', 1)
    warehouse_ids = body.get('warehouse_ids') or []
    area_ids      = body.get('area_ids') or []

    if not uid:
        return jsonify(code=400, msg='缺少 id'), 400
    if not username:
        return jsonify(code=400, msg='用户名不能为空'), 400

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM sys_user WHERE username = %s AND id != %s', (username, uid))
            if cur.fetchone():
                return jsonify(code=400, msg='用户名已被其他用户占用'), 400
            cur.execute(
                '''UPDATE sys_user
                   SET username=%s, real_name=%s, role=%s, status=%s,
                       warehouse_ids=%s, area_ids=%s
                   WHERE id=%s''',
                (username, real_name, role, status, warehouse_ids, area_ids, uid)
            )
        conn.commit()
    finally:
        conn.close()
    return jsonify(code=200, msg='修改成功')


# ──────────────────────────────────────────────────────────
# PUT /api/user/manage/reset-password  重置密码
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/manage/reset-password', methods=['PUT'])
def manage_reset_password():
    body = request.get_json(silent=True) or {}
    uid      = body.get('id')
    password = (body.get('password') or '').strip()

    if not uid:
        return jsonify(code=400, msg='缺少 id'), 400
    if not password:
        return jsonify(code=400, msg='密码不能为空'), 400
    if len(password) < 6:
        return jsonify(code=400, msg='密码长度不能少于6位'), 400

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE sys_user SET password=%s WHERE id=%s', (_md5(password), uid))
        conn.commit()
    finally:
        conn.close()
    return jsonify(code=200, msg='密码重置成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/user/manage/delete  删除用户（禁止删除 id=1 超管）
# ──────────────────────────────────────────────────────────
@user_bp.route('/user/manage/delete', methods=['DELETE'])
def manage_delete():
    body = request.get_json(silent=True) or {}
    uid = body.get('id')

    if not uid:
        return jsonify(code=400, msg='缺少 id'), 400
    if uid == 1:
        return jsonify(code=403, msg='超级管理员不可删除'), 403

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM sys_user WHERE id=%s', (uid,))
        conn.commit()
    finally:
        conn.close()
    return jsonify(code=200, msg='删除成功')
