from flask import Blueprint, request, jsonify
import db
from datetime import date

customer_bp = Blueprint('customer', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


def _generate_code(cur):
    """自动生成客户编号，格式 C{年}{序号4位}"""
    year = date.today().year
    cur.execute(
        "SELECT code FROM biz_customer WHERE code LIKE %s ORDER BY code DESC LIMIT 1",
        (f'C{year}%',)
    )
    row = cur.fetchone()
    if row:
        seq = int(row['code'][5:]) + 1
    else:
        seq = 1
    return f'C{year}{seq:04d}'


def _generate_member_no(cur):
    """自动生成会员号，格式 M{年}{序号4位}"""
    year = date.today().year
    cur.execute(
        "SELECT member_no FROM biz_customer WHERE member_no LIKE %s ORDER BY member_no DESC LIMIT 1",
        (f'M{year}%',)
    )
    row = cur.fetchone()
    if row:
        seq = int(row['member_no'][5:]) + 1
    else:
        seq = 1
    return f'M{year}{seq:04d}'


# ──────────────────────────────────────────────────────────
# GET /api/customer/list  客户列表（支持 keyword / area_id / page / page_size）
# ──────────────────────────────────────────────────────────
@customer_bp.route('/customer/list', methods=['GET'])
def customer_list():
    keyword   = request.args.get('keyword', '').strip()
    area_id   = request.args.get('area_id', type=int, default=0)
    page      = request.args.get('page', type=int, default=1)
    page_size = request.args.get('page_size', type=int, default=10)
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    offset = (page - 1) * page_size

    where_clauses = []
    params = []

    if keyword:
        where_clauses.append(
            "(c.name ILIKE %s OR c.contact ILIKE %s OR c.phone ILIKE %s OR c.member_no ILIKE %s)"
        )
        like = f'%{keyword}%'
        params.extend([like, like, like, like])

    if area_id and area_id > 0:
        where_clauses.append("c.area_id = %s")
        params.append(area_id)

    where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''

    base_sql = (
        "FROM biz_customer c "
        "LEFT JOIN biz_area a ON c.area_id = a.id "
        "LEFT JOIN biz_member_type mt ON c.member_type_id = mt.id "
        "LEFT JOIN sys_user u ON c.salesman = u.id "
        f"{where_sql}"
    )

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total {base_sql}", params)
            total = cur.fetchone()['total']

            cur.execute(
                f"SELECT c.id, c.code, c.name, c.contact, c.phone, c.address, "
                f"c.area_id, a.name AS area_name, c.salesman, u.real_name AS salesman_name, "
                f"c.member_type_id, mt.name AS member_type_name, "
                f"c.member_no, c.birthday, c.points, c.balance, c.status, c.created_at "
                f"{base_sql} ORDER BY c.id LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()

    # 格式化日期
    for r in rows:
        if r.get('birthday'):
            r['birthday'] = r['birthday'].isoformat()
        if r.get('created_at'):
            r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if r.get('balance') is not None:
            r['balance'] = float(r['balance'])

    return _ok(data={'list': rows, 'total': total})


# ──────────────────────────────────────────────────────────
# POST /api/customer/add  新建客户
# ──────────────────────────────────────────────────────────
@customer_bp.route('/customer/add', methods=['POST'])
def customer_add():
    data = request.get_json(silent=True) or {}
    name    = (data.get('name') or '').strip()
    contact = (data.get('contact') or '').strip()
    phone   = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    area_id         = data.get('area_id') or None
    salesman        = data.get('salesman') or None
    member_type_id  = data.get('member_type_id') or None
    birthday        = data.get('birthday') or None
    status          = data.get('status', 1)

    if not name:
        return _err('客户名称不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            code      = (data.get('code') or '').strip() or _generate_code(cur)
            member_no = (data.get('member_no') or '').strip() or _generate_member_no(cur)

            cur.execute(
                "INSERT INTO biz_customer "
                "(code, name, contact, phone, address, area_id, salesman, "
                " member_type_id, member_no, birthday, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (code, name, contact, phone, address, area_id, salesman,
                 member_type_id, member_no, birthday or None, status)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        msg = str(e)
        if 'unique' in msg.lower():
            if 'code' in msg.lower():
                return _err('客户编号已存在')
            if 'member_no' in msg.lower():
                return _err('会员号已存在')
            return _err('数据重复')
        return _err(msg, 500)
    finally:
        conn.close()
    return _ok(data={'id': new_id}, msg='新建成功')


# ──────────────────────────────────────────────────────────
# PUT /api/customer/update  修改客户
# ──────────────────────────────────────────────────────────
@customer_bp.route('/customer/update', methods=['PUT'])
def customer_update():
    data = request.get_json(silent=True) or {}
    cid  = data.get('id')
    if not cid:
        return _err('缺少客户 id')

    name    = (data.get('name') or '').strip()
    contact = (data.get('contact') or '').strip()
    phone   = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()
    area_id         = data.get('area_id') or None
    salesman        = data.get('salesman') or None
    member_type_id  = data.get('member_type_id') or None
    member_no       = (data.get('member_no') or '').strip()
    birthday        = data.get('birthday') or None
    status          = data.get('status', 1)

    if not name:
        return _err('客户名称不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_customer WHERE id = %s', (cid,))
            if not cur.fetchone():
                return _err('客户不存在', 404)

            if not member_no:
                member_no = _generate_member_no(cur)

            cur.execute(
                "UPDATE biz_customer SET name=%s, contact=%s, phone=%s, address=%s, "
                "area_id=%s, salesman=%s, member_type_id=%s, member_no=%s, "
                "birthday=%s, status=%s WHERE id=%s",
                (name, contact, phone, address, area_id, salesman,
                 member_type_id, member_no, birthday or None, status, cid)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        msg = str(e)
        if 'unique' in msg.lower():
            if 'member_no' in msg.lower():
                return _err('会员号已存在')
            return _err('数据重复')
        return _err(msg, 500)
    finally:
        conn.close()
    return _ok(msg='更新成功')


# ──────────────────────────────────────────────────────────
# PUT /api/customer/recharge  充值
# Body: { id, amount }
# ──────────────────────────────────────────────────────────
@customer_bp.route('/customer/recharge', methods=['PUT'])
def customer_recharge():
    data   = request.get_json(silent=True) or {}
    cid    = data.get('id')
    amount = data.get('amount')
    if not cid:
        return _err('缺少客户 id')
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return _err('充值金额无效')
    if amount <= 0:
        return _err('充值金额必须大于 0')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, balance FROM biz_customer WHERE id = %s', (cid,))
            row = cur.fetchone()
            if not row:
                return _err('客户不存在', 404)
            cur.execute(
                'UPDATE biz_customer SET balance = balance + %s WHERE id = %s',
                (amount, cid)
            )
        conn.commit()
        new_balance = float(row['balance']) + amount
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data={'balance': round(new_balance, 2)}, msg='充值成功')


# ──────────────────────────────────────────────────────────
# DELETE /api/customer/delete  删除客户
# Body: { id }
# ──────────────────────────────────────────────────────────
@customer_bp.route('/customer/delete', methods=['DELETE'])
def customer_delete():
    data = request.get_json(silent=True) or {}
    cid  = data.get('id')
    if not cid:
        return _err('缺少客户 id')
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_customer WHERE id = %s', (cid,))
            if not cur.fetchone():
                return _err('客户不存在', 404)
            cur.execute('DELETE FROM biz_customer WHERE id = %s', (cid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='删除成功')
