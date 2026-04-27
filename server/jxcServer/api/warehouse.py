from flask import Blueprint, request, jsonify
import db

warehouse_bp = Blueprint('warehouse', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# GET /api/warehouse/list  仓库列表（支持 name 关键词搜索）
# Query: name（可选）
# ──────────────────────────────────────────────────────────
@warehouse_bp.route('/warehouse/list', methods=['GET'])
def warehouse_list():
    name = request.args.get('name', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if name:
                cur.execute(
                    'SELECT id, name, address, remark, is_default FROM biz_warehouse'
                    ' WHERE name ILIKE %s ORDER BY id',
                    (f'%{name}%',)
                )
            else:
                cur.execute(
                    'SELECT id, name, address, remark, is_default FROM biz_warehouse'
                    ' ORDER BY id'
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


# ──────────────────────────────────────────────────────────
# POST /api/warehouse/add  新建仓库
# Body: { name, address, remark, is_default }
# ──────────────────────────────────────────────────────────
@warehouse_bp.route('/warehouse/add', methods=['POST'])
def warehouse_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    address = (data.get('address') or '').strip()
    remark = (data.get('remark') or '').strip()
    is_default = 1 if int(data.get('is_default', 0) or 0) == 1 else 0
    if not name:
        return _err('仓库名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_warehouse SET is_default = 0 WHERE is_default = 1')
            cur.execute(
                'INSERT INTO biz_warehouse (name, address, remark, is_default) VALUES (%s, %s, %s, %s) RETURNING id',
                (name, address, remark, is_default)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('仓库名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


# ──────────────────────────────────────────────────────────
# PUT /api/warehouse/update  修改仓库
# Body: { id, name, address, remark, is_default }
# ──────────────────────────────────────────────────────────
@warehouse_bp.route('/warehouse/update', methods=['PUT'])
def warehouse_update():
    data = request.get_json(silent=True) or {}
    wh_id = data.get('id')
    name = (data.get('name') or '').strip()
    address = (data.get('address') or '').strip()
    remark = (data.get('remark') or '').strip()
    is_default = 1 if int(data.get('is_default', 0) or 0) == 1 else 0
    if not wh_id or not name:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_warehouse WHERE id = %s', (wh_id,))
            if not cur.fetchone():
                return _err('仓库不存在', 404)
            if is_default == 1:
                cur.execute('UPDATE biz_warehouse SET is_default = 0 WHERE id != %s AND is_default = 1', (wh_id,))
            cur.execute(
                'UPDATE biz_warehouse SET name=%s, address=%s, remark=%s, is_default=%s WHERE id=%s',
                (name, address, remark, is_default, wh_id)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('仓库名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='修改成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/warehouse/delete  删除仓库
# Body: { id }
# ──────────────────────────────────────────────────────────
@warehouse_bp.route('/warehouse/delete', methods=['DELETE'])
def warehouse_delete():
    data = request.get_json(silent=True) or {}
    wh_id = data.get('id')
    if not wh_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_warehouse WHERE id = %s', (wh_id,))
            if not cur.fetchone():
                return _err('仓库不存在', 404)
            cur.execute('DELETE FROM biz_warehouse WHERE id = %s', (wh_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')
