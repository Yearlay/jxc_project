from flask import Blueprint, request, jsonify
import db

staff_bp = Blueprint('staff', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ══════════════════════════════════════════════════════════
# 采购业务员  /api/purchase-staff/
# ══════════════════════════════════════════════════════════

@staff_bp.route('/purchase-staff/list', methods=['GET'])
def purchase_staff_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    '''SELECT id, name, phone, address, is_default, purchase_limit
                       FROM biz_purchase_staff
                       WHERE name ILIKE %s OR phone ILIKE %s
                       ORDER BY id''',
                    (f'%{keyword}%', f'%{keyword}%')
                )
            else:
                cur.execute(
                    '''SELECT id, name, phone, address, is_default, purchase_limit
                       FROM biz_purchase_staff ORDER BY id'''
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@staff_bp.route('/purchase-staff/add', methods=['POST'])
def purchase_staff_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return _err('姓名不能为空')
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    is_default = 1 if data.get('is_default') == 1 else 0
    purchase_limit = float(data.get('purchase_limit') or 0)
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_purchase_staff SET is_default = 0')
            cur.execute(
                '''INSERT INTO biz_purchase_staff (name, phone, address, is_default, purchase_limit)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id''',
                (name, phone, address, is_default, purchase_limit)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id})


@staff_bp.route('/purchase-staff/update', methods=['PUT'])
def purchase_staff_update():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    name = (data.get('name') or '').strip()
    if not rid:
        return _err('id 不能为空')
    if not name:
        return _err('姓名不能为空')
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    is_default = 1 if data.get('is_default') == 1 else 0
    purchase_limit = float(data.get('purchase_limit') or 0)
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_purchase_staff SET is_default = 0 WHERE id != %s', (rid,))
            cur.execute(
                '''UPDATE biz_purchase_staff
                   SET name=%s, phone=%s, address=%s, is_default=%s, purchase_limit=%s
                   WHERE id=%s''',
                (name, phone, address, is_default, purchase_limit, rid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()


@staff_bp.route('/purchase-staff/delete', methods=['DELETE'])
def purchase_staff_delete():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    if not rid:
        return _err('id 不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_purchase_staff WHERE id = %s', (rid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()


# ══════════════════════════════════════════════════════════
# 销售业务员  /api/sales-staff/
# ══════════════════════════════════════════════════════════

@staff_bp.route('/sales-staff/list', methods=['GET'])
def sales_staff_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    '''SELECT id, name, phone, address, is_default, commission_rate
                       FROM biz_sales_staff
                       WHERE name ILIKE %s OR phone ILIKE %s
                       ORDER BY id''',
                    (f'%{keyword}%', f'%{keyword}%')
                )
            else:
                cur.execute(
                    '''SELECT id, name, phone, address, is_default, commission_rate
                       FROM biz_sales_staff ORDER BY id'''
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@staff_bp.route('/sales-staff/add', methods=['POST'])
def sales_staff_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return _err('姓名不能为空')
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    is_default = 1 if data.get('is_default') == 1 else 0
    commission_rate = float(data.get('commission_rate') or 0)
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_sales_staff SET is_default = 0')
            cur.execute(
                '''INSERT INTO biz_sales_staff (name, phone, address, is_default, commission_rate)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id''',
                (name, phone, address, is_default, commission_rate)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id})


@staff_bp.route('/sales-staff/update', methods=['PUT'])
def sales_staff_update():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    name = (data.get('name') or '').strip()
    if not rid:
        return _err('id 不能为空')
    if not name:
        return _err('姓名不能为空')
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    is_default = 1 if data.get('is_default') == 1 else 0
    commission_rate = float(data.get('commission_rate') or 0)
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_sales_staff SET is_default = 0 WHERE id != %s', (rid,))
            cur.execute(
                '''UPDATE biz_sales_staff
                   SET name=%s, phone=%s, address=%s, is_default=%s, commission_rate=%s
                   WHERE id=%s''',
                (name, phone, address, is_default, commission_rate, rid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()


@staff_bp.route('/sales-staff/delete', methods=['DELETE'])
def sales_staff_delete():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    if not rid:
        return _err('id 不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_sales_staff WHERE id = %s', (rid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()


# ══════════════════════════════════════════════════════════
# 销售终端  /api/terminal/
# ══════════════════════════════════════════════════════════

@staff_bp.route('/terminal/list', methods=['GET'])
def terminal_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    '''SELECT id, name, code, is_default, db_no
                       FROM biz_terminal
                       WHERE name ILIKE %s OR code ILIKE %s
                       ORDER BY id''',
                    (f'%{keyword}%', f'%{keyword}%')
                )
            else:
                cur.execute(
                    '''SELECT id, name, code, is_default, db_no
                       FROM biz_terminal ORDER BY id'''
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@staff_bp.route('/terminal/add', methods=['POST'])
def terminal_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip()
    if not name:
        return _err('终端名称不能为空')
    if not code:
        return _err('终端编号不能为空')
    is_default = 1 if data.get('is_default') == 1 else 0
    db_no = (data.get('db_no') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_terminal SET is_default = 0')
            cur.execute(
                '''INSERT INTO biz_terminal (name, code, is_default, db_no)
                   VALUES (%s, %s, %s, %s) RETURNING id''',
                (name, code, is_default, db_no)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('终端编号已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id})


@staff_bp.route('/terminal/update', methods=['PUT'])
def terminal_update():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip()
    if not rid:
        return _err('id 不能为空')
    if not name:
        return _err('终端名称不能为空')
    if not code:
        return _err('终端编号不能为空')
    is_default = 1 if data.get('is_default') == 1 else 0
    db_no = (data.get('db_no') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if is_default == 1:
                cur.execute('UPDATE biz_terminal SET is_default = 0 WHERE id != %s', (rid,))
            cur.execute(
                '''UPDATE biz_terminal
                   SET name=%s, code=%s, is_default=%s, db_no=%s
                   WHERE id=%s''',
                (name, code, is_default, db_no, rid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('终端编号已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()


@staff_bp.route('/terminal/delete', methods=['DELETE'])
def terminal_delete():
    data = request.get_json(silent=True) or {}
    rid = data.get('id')
    if not rid:
        return _err('id 不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_terminal WHERE id = %s', (rid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok()
