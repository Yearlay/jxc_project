from flask import Blueprint, request, jsonify
import db

area_bp = Blueprint('area', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# GET /api/area/list  片区列表（支持 name 关键词搜索）
# Query: name（可选）
# ──────────────────────────────────────────────────────────
@area_bp.route('/area/list', methods=['GET'])
def area_list():
    name = request.args.get('name', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if name:
                cur.execute(
                    'SELECT id, name, remark, is_default, status FROM biz_area'
                    ' WHERE name ILIKE %s ORDER BY is_default DESC, id',
                    (f'%{name}%',)
                )
            else:
                cur.execute(
                    'SELECT id, name, remark, is_default, status FROM biz_area'
                    ' ORDER BY is_default DESC, id'
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


# ──────────────────────────────────────────────────────────
# POST /api/area/add  新建片区
# Body: { name, remark }
# ──────────────────────────────────────────────────────────
@area_bp.route('/area/add', methods=['POST'])
def area_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    remark = (data.get('remark') or '').strip()
    if not name:
        return _err('片区名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_area (name, remark) VALUES (%s, %s) RETURNING id',
                (name, remark)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('片区名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


# ──────────────────────────────────────────────────────────
# PUT /api/area/update  编辑片区
# Body: { id, name, remark, status }
# ──────────────────────────────────────────────────────────
@area_bp.route('/area/update', methods=['PUT'])
def area_update():
    data = request.get_json(silent=True) or {}
    area_id = data.get('id')
    name = (data.get('name') or '').strip()
    remark = (data.get('remark') or '').strip()
    status = data.get('status')
    if not area_id or not name:
        return _err('参数缺失')
    if status is not None and status not in (0, 1):
        return _err('状态值无效')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            # 不允许编辑默认片区名称
            cur.execute('SELECT is_default FROM biz_area WHERE id = %s', (area_id,))
            row = cur.fetchone()
            if not row:
                return _err('片区不存在', 404)
            if row['is_default'] == 1:
                return _err('默认片区【未划分】不允许编辑')
            if status is not None:
                cur.execute(
                    'UPDATE biz_area SET name = %s, remark = %s, status = %s WHERE id = %s',
                    (name, remark, status, area_id)
                )
            else:
                cur.execute(
                    'UPDATE biz_area SET name = %s, remark = %s WHERE id = %s',
                    (name, remark, area_id)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('片区名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/area/delete  删除片区
# Body: { id }
# ──────────────────────────────────────────────────────────
@area_bp.route('/area/delete', methods=['DELETE'])
def area_delete():
    data = request.get_json(silent=True) or {}
    area_id = data.get('id')
    if not area_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT is_default FROM biz_area WHERE id = %s', (area_id,))
            row = cur.fetchone()
            if not row:
                return _err('片区不存在', 404)
            if row['is_default'] == 1:
                return _err('默认片区【未划分】不允许删除')
            cur.execute('DELETE FROM biz_area WHERE id = %s', (area_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')
