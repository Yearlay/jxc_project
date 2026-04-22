from flask import Blueprint, request, jsonify
import db

member_type_bp = Blueprint('member_type', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# GET /api/member-type/list  会员类型列表（支持 name 关键词搜索）
# Query: name（可选）
# ──────────────────────────────────────────────────────────
@member_type_bp.route('/member-type/list', methods=['GET'])
def member_type_list():
    name = request.args.get('name', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if name:
                cur.execute(
                    'SELECT id, name, discount, remark, status FROM biz_member_type'
                    ' WHERE name ILIKE %s ORDER BY id',
                    (f'%{name}%',)
                )
            else:
                cur.execute(
                    'SELECT id, name, discount, remark, status FROM biz_member_type'
                    ' ORDER BY id'
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    # discount 转为 float 返回
    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'name': r['name'],
            'discount': float(r['discount']),
            'remark': r['remark'],
            'status': r['status'],
        })
    return _ok(data=result)


# ──────────────────────────────────────────────────────────
# POST /api/member-type/add  新建会员类型
# Body: { name, discount, remark }
# ──────────────────────────────────────────────────────────
@member_type_bp.route('/member-type/add', methods=['POST'])
def member_type_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    discount = data.get('discount')
    remark = (data.get('remark') or '').strip()
    if not name:
        return _err('会员类型名称不能为空')
    if discount is None:
        return _err('折扣率不能为空')
    try:
        discount = float(discount)
        if not (0.01 <= discount <= 1.00):
            raise ValueError()
    except (ValueError, TypeError):
        return _err('折扣率须在 0.01 ~ 1.00 之间')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_member_type (name, discount, remark) VALUES (%s, %s, %s) RETURNING id',
                (name, discount, remark)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('会员类型名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


# ──────────────────────────────────────────────────────────
# PUT /api/member-type/update  编辑会员类型
# Body: { id, name, discount, remark, status }
# ──────────────────────────────────────────────────────────
@member_type_bp.route('/member-type/update', methods=['PUT'])
def member_type_update():
    data = request.get_json(silent=True) or {}
    mt_id = data.get('id')
    name = (data.get('name') or '').strip()
    discount = data.get('discount')
    remark = (data.get('remark') or '').strip()
    status = data.get('status')
    if not mt_id or not name or discount is None:
        return _err('参数缺失')
    try:
        discount = float(discount)
        if not (0.01 <= discount <= 1.00):
            raise ValueError()
    except (ValueError, TypeError):
        return _err('折扣率须在 0.01 ~ 1.00 之间')
    if status is not None and status not in (0, 1):
        return _err('状态值无效')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if status is not None:
                cur.execute(
                    'UPDATE biz_member_type SET name = %s, discount = %s, remark = %s, status = %s WHERE id = %s',
                    (name, discount, remark, status, mt_id)
                )
            else:
                cur.execute(
                    'UPDATE biz_member_type SET name = %s, discount = %s, remark = %s WHERE id = %s',
                    (name, discount, remark, mt_id)
                )
            if cur.rowcount == 0:
                return _err('会员类型不存在', 404)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('会员类型名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/member-type/delete  删除会员类型
# Body: { id }
# ──────────────────────────────────────────────────────────
@member_type_bp.route('/member-type/delete', methods=['DELETE'])
def member_type_delete():
    data = request.get_json(silent=True) or {}
    mt_id = data.get('id')
    if not mt_id:
        return _err('参数缺失')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_member_type WHERE id = %s', (mt_id,))
            if cur.rowcount == 0:
                return _err('会员类型不存在', 404)
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')
