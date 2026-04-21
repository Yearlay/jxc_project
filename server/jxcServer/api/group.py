from flask import Blueprint, request, jsonify
import db

group_bp = Blueprint('group', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# GET /api/group/list  权限组列表（含成员数量）
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/list', methods=['GET'])
def group_list():
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT g.id, g.name, g.remark, g.status,
                       COUNT(gu.user_id) AS member_count
                FROM sys_group g
                LEFT JOIN sys_group_user gu ON gu.group_id = g.id
                GROUP BY g.id, g.name, g.remark, g.status
                ORDER BY g.id
            ''')
            rows = cur.fetchall()
    finally:
        conn.close()
    return _ok([dict(r) for r in rows])


# ──────────────────────────────────────────────────────────
# POST /api/group/add  新增权限组
# Body: { name, remark? }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/add', methods=['POST'])
def group_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    remark = (data.get('remark') or '').strip()
    if not name:
        return _err('权限组名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO sys_group (name, remark) VALUES (%s, %s) RETURNING id',
                (name, remark)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('权限组名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok({'id': new_id}, '添加成功')


# ──────────────────────────────────────────────────────────
# PUT /api/group/rename  重命名权限组
# Body: { id, name }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/rename', methods=['PUT'])
def group_rename():
    data = request.get_json(silent=True) or {}
    group_id = data.get('id')
    name = (data.get('name') or '').strip()
    if not group_id or not name:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE sys_group SET name = %s WHERE id = %s',
                (name, group_id)
            )
            if cur.rowcount == 0:
                return _err('权限组不存在', 404)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('权限组名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='重命名成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/group/delete  删除权限组
# Body: { id }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/delete', methods=['DELETE'])
def group_delete():
    data = request.get_json(silent=True) or {}
    group_id = data.get('id')
    if not group_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) AS cnt FROM sys_group_user WHERE group_id = %s', (group_id,))
            cnt = cur.fetchone()['cnt']
            if cnt > 0:
                return _err(f'该权限组下还有 {cnt} 名成员，请先移除成员后再删除')
            cur.execute('DELETE FROM sys_group_menu WHERE group_id = %s', (group_id,))
            cur.execute('DELETE FROM sys_group WHERE id = %s', (group_id,))
            if cur.rowcount == 0:
                return _err('权限组不存在', 404)
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')


# ──────────────────────────────────────────────────────────
# GET /api/group/menus?group_id=  权限组已配置的菜单 ID 列表
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/menus', methods=['GET'])
def group_menus():
    group_id = request.args.get('group_id')
    if not group_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT menu_id FROM sys_group_menu WHERE group_id = %s',
                (group_id,)
            )
            ids = [r['menu_id'] for r in cur.fetchall()]
    finally:
        conn.close()
    return _ok(ids)


# ──────────────────────────────────────────────────────────
# POST /api/group/menus/save  保存权限组菜单配置（全量覆盖）
# Body: { group_id, menu_ids: [1,2,...] }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/menus/save', methods=['POST'])
def group_menus_save():
    data = request.get_json(silent=True) or {}
    group_id = data.get('group_id')
    menu_ids = data.get('menu_ids', [])
    if not group_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM sys_group_menu WHERE group_id = %s', (group_id,))
            if menu_ids:
                values = [(group_id, mid) for mid in menu_ids]
                cur.executemany(
                    'INSERT INTO sys_group_menu (group_id, menu_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                    values
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='保存成功')


# ──────────────────────────────────────────────────────────
# GET /api/group/members?group_id=  权限组成员列表
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/members', methods=['GET'])
def group_members():
    group_id = request.args.get('group_id')
    if not group_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT u.id, u.username, u.real_name, u.status
                FROM sys_group_user gu
                JOIN sys_user u ON u.id = gu.user_id
                WHERE gu.group_id = %s
                ORDER BY u.id
            ''', (group_id,))
            rows = cur.fetchall()
    finally:
        conn.close()
    return _ok([dict(r) for r in rows])


# ──────────────────────────────────────────────────────────
# POST /api/group/members/add  添加成员
# Body: { group_id, user_id }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/members/add', methods=['POST'])
def group_members_add():
    data = request.get_json(silent=True) or {}
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    if not group_id or not user_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO sys_group_user (group_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                (group_id, user_id)
            )
            # 同步更新 sys_user.group_id（主权限组）
            cur.execute(
                'UPDATE sys_user SET group_id = %s WHERE id = %s AND group_id IS NULL',
                (group_id, user_id)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='添加成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/group/members/remove  移除成员
# Body: { group_id, user_id }
# ──────────────────────────────────────────────────────────
@group_bp.route('/group/members/remove', methods=['DELETE'])
def group_members_remove():
    data = request.get_json(silent=True) or {}
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    if not group_id or not user_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM sys_group_user WHERE group_id = %s AND user_id = %s',
                (group_id, user_id)
            )
            if cur.rowcount == 0:
                return _err('该成员不在此权限组中', 404)
            # 若用户主权限组是当前组，清除
            cur.execute(
                'UPDATE sys_user SET group_id = NULL WHERE id = %s AND group_id = %s',
                (user_id, group_id)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='移除成功')
