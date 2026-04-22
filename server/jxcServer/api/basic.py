from flask import Blueprint, request, jsonify
import db

basic_bp = Blueprint('basic', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ══════════════════════════════════════════════════════════
# 计量单位  /api/unit/
# ══════════════════════════════════════════════════════════

@basic_bp.route('/unit/list', methods=['GET'])
def unit_list():
    name = request.args.get('name', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if name:
                cur.execute(
                    'SELECT id, name FROM biz_unit WHERE name ILIKE %s ORDER BY id',
                    (f'%{name}%',)
                )
            else:
                cur.execute('SELECT id, name FROM biz_unit ORDER BY id')
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@basic_bp.route('/unit/add', methods=['POST'])
def unit_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return _err('计量单位名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_unit (name) VALUES (%s) RETURNING id',
                (name,)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('计量单位名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


@basic_bp.route('/unit/update', methods=['PUT'])
def unit_update():
    data = request.get_json(silent=True) or {}
    uid = data.get('id')
    name = (data.get('name') or '').strip()
    if not uid:
        return _err('缺少 id')
    if not name:
        return _err('计量单位名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE biz_unit SET name=%s WHERE id=%s',
                (name, uid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('计量单位名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


@basic_bp.route('/unit/delete', methods=['DELETE'])
def unit_delete():
    data = request.get_json(silent=True) or {}
    uid = data.get('id')
    if not uid:
        return _err('缺少 id')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_unit WHERE id=%s', (uid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'foreign' in str(e).lower():
            return _err('该计量单位已被商品引用，无法删除')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')


# ══════════════════════════════════════════════════════════
# 厂家信息  /api/manufacturer/
# ══════════════════════════════════════════════════════════

@basic_bp.route('/manufacturer/list', methods=['GET'])
def manufacturer_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    'SELECT id, name, phone, address, license, bank_account FROM biz_manufacturer'
                    ' WHERE name ILIKE %s OR phone ILIKE %s ORDER BY id',
                    (f'%{keyword}%', f'%{keyword}%')
                )
            else:
                cur.execute(
                    'SELECT id, name, phone, address, license, bank_account FROM biz_manufacturer'
                    ' ORDER BY id'
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@basic_bp.route('/manufacturer/add', methods=['POST'])
def manufacturer_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return _err('厂家名称不能为空')
    phone        = (data.get('phone') or '').strip()
    address      = (data.get('address') or '').strip()
    license_no   = (data.get('license') or '').strip()
    bank_account = (data.get('bank_account') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_manufacturer (name, phone, address, license, bank_account)'
                ' VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (name, phone, address, license_no, bank_account)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('厂家名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


@basic_bp.route('/manufacturer/update', methods=['PUT'])
def manufacturer_update():
    data = request.get_json(silent=True) or {}
    mid = data.get('id')
    name = (data.get('name') or '').strip()
    if not mid:
        return _err('缺少 id')
    if not name:
        return _err('厂家名称不能为空')
    phone        = (data.get('phone') or '').strip()
    address      = (data.get('address') or '').strip()
    license_no   = (data.get('license') or '').strip()
    bank_account = (data.get('bank_account') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE biz_manufacturer SET name=%s, phone=%s, address=%s, license=%s, bank_account=%s'
                ' WHERE id=%s',
                (name, phone, address, license_no, bank_account, mid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('厂家名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


@basic_bp.route('/manufacturer/delete', methods=['DELETE'])
def manufacturer_delete():
    data = request.get_json(silent=True) or {}
    mid = data.get('id')
    if not mid:
        return _err('缺少 id')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_manufacturer WHERE id=%s', (mid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'foreign' in str(e).lower():
            return _err('该厂家已被单据引用，无法删除')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')


# ══════════════════════════════════════════════════════════
# 车辆信息  /api/vehicle/
# ══════════════════════════════════════════════════════════

@basic_bp.route('/vehicle/list', methods=['GET'])
def vehicle_list():
    keyword = request.args.get('keyword', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    'SELECT id, plate, owner, owner_phone, remark FROM biz_vehicle'
                    ' WHERE plate ILIKE %s OR owner ILIKE %s OR owner_phone ILIKE %s ORDER BY id',
                    (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
                )
            else:
                cur.execute(
                    'SELECT id, plate, owner, owner_phone, remark FROM biz_vehicle ORDER BY id'
                )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@basic_bp.route('/vehicle/add', methods=['POST'])
def vehicle_add():
    data = request.get_json(silent=True) or {}
    plate = (data.get('plate') or '').strip()
    if not plate:
        return _err('车牌号不能为空')
    owner       = (data.get('owner') or '').strip()
    owner_phone = (data.get('owner_phone') or '').strip()
    remark      = (data.get('remark') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_vehicle (plate, owner, owner_phone, remark)'
                ' VALUES (%s, %s, %s, %s) RETURNING id',
                (plate, owner, owner_phone, remark)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('车牌号已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


@basic_bp.route('/vehicle/update', methods=['PUT'])
def vehicle_update():
    data = request.get_json(silent=True) or {}
    vid = data.get('id')
    plate = (data.get('plate') or '').strip()
    if not vid:
        return _err('缺少 id')
    if not plate:
        return _err('车牌号不能为空')
    owner       = (data.get('owner') or '').strip()
    owner_phone = (data.get('owner_phone') or '').strip()
    remark      = (data.get('remark') or '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE biz_vehicle SET plate=%s, owner=%s, owner_phone=%s, remark=%s WHERE id=%s',
                (plate, owner, owner_phone, remark, vid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('车牌号已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


@basic_bp.route('/vehicle/delete', methods=['DELETE'])
def vehicle_delete():
    data = request.get_json(silent=True) or {}
    vid = data.get('id')
    if not vid:
        return _err('缺少 id')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_vehicle WHERE id=%s', (vid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'foreign' in str(e).lower():
            return _err('该车辆已被单据引用，无法删除')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')


# ══════════════════════════════════════════════════════════
# 付款方式  /api/payment/
# ══════════════════════════════════════════════════════════

@basic_bp.route('/payment/list', methods=['GET'])
def payment_list():
    name = request.args.get('name', '').strip()
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if name:
                cur.execute(
                    'SELECT id, name FROM biz_payment WHERE name ILIKE %s ORDER BY id',
                    (f'%{name}%',)
                )
            else:
                cur.execute('SELECT id, name FROM biz_payment ORDER BY id')
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=rows)


@basic_bp.route('/payment/add', methods=['POST'])
def payment_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return _err('付款方式名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO biz_payment (name) VALUES (%s) RETURNING id',
                (name,)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('付款方式名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


@basic_bp.route('/payment/update', methods=['PUT'])
def payment_update():
    data = request.get_json(silent=True) or {}
    pid = data.get('id')
    name = (data.get('name') or '').strip()
    if not pid:
        return _err('缺少 id')
    if not name:
        return _err('付款方式名称不能为空')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE biz_payment SET name=%s WHERE id=%s', (name, pid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'unique' in str(e).lower():
            return _err('付款方式名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


@basic_bp.route('/payment/delete', methods=['DELETE'])
def payment_delete():
    data = request.get_json(silent=True) or {}
    pid = data.get('id')
    if not pid:
        return _err('缺少 id')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM biz_payment WHERE id=%s', (pid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'foreign' in str(e).lower():
            return _err('该付款方式已被单据引用，无法删除')
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')
