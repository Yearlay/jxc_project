from datetime import datetime
import json

from flask import Blueprint, g, jsonify, request

import db

pos_bp = Blueprint('pos', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


def _to_float(value):
    return float(value or 0)


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _current_user_id():
    return _to_int((getattr(g, 'current_user', {}) or {}).get('user_id'))


def _generate_sale_no():
    now = datetime.now()
    return f"P-{now.strftime('%y%m%d')}{int(now.timestamp() * 1000)}"


def _normalize_hold_row(row):
    result = dict(row)
    result['total_amount'] = _to_float(result.get('total_amount'))
    result['payable_amount'] = _to_float(result.get('payable_amount'))
    result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    snapshot = json.loads(result.get('cart_json') or '{}')
    if isinstance(snapshot, list):
        snapshot = {'cart': snapshot}
    result['snapshot'] = snapshot
    result['cart'] = snapshot.get('cart') or []
    return result


@pos_bp.route('/pos/bootstrap', methods=['GET'])
def pos_bootstrap():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT id, name, address, is_default
                   FROM biz_warehouse
                   ORDER BY is_default DESC, id ASC
                   LIMIT 1'''
            )
            warehouse = cur.fetchone()

            cur.execute(
                '''SELECT id, name, phone, address, is_default, commission_rate
                   FROM biz_sales_staff
                   ORDER BY is_default DESC, id ASC
                   LIMIT 1'''
            )
            sales_staff = cur.fetchone()

            cur.execute(
                '''SELECT id, name, code, is_default, db_no
                   FROM biz_terminal
                   ORDER BY is_default DESC, id ASC
                   LIMIT 1'''
            )
            terminal = cur.fetchone()

            cur.execute(
                'SELECT id, username, real_name FROM sys_user WHERE id = %s',
                (operator_id,)
            )
            operator = cur.fetchone()
    except Exception as exc:
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(data={
        'sale_no': _generate_sale_no(),
        'warehouse': warehouse,
        'sales_staff': sales_staff,
        'terminal': terminal,
        'operator': operator,
    })


@pos_bp.route('/pos/goods/search', methods=['GET'])
def pos_goods_search():
    keyword = request.args.get('keyword', '').strip()
    warehouse_id = _to_int(request.args.get('warehouse_id'))
    if not keyword:
        return _ok(data=[])

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT
                       g.id,
                       g.code,
                       g.other_code,
                       g.name,
                       g.sale_price,
                       g.member_price,
                       g.enable_points,
                       g.enable_discount,
                       COALESCE(u.name, '') AS unit_name,
                       COALESCE((
                           SELECT SUM(s.quantity)
                           FROM biz_goods_stock s
                           WHERE s.goods_id = g.id
                             AND (%s = 0 OR s.warehouse_id = %s)
                       ), 0) AS stock_total
                   FROM biz_goods g
                   LEFT JOIN biz_unit u ON g.unit_id = u.id
                   WHERE g.name ILIKE %s OR g.code ILIKE %s OR g.other_code ILIKE %s
                   ORDER BY g.id DESC
                   LIMIT 20''',
                (warehouse_id, warehouse_id, f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
            )
            rows = cur.fetchall()
    except Exception as exc:
        return _err(str(exc), 500)
    finally:
        conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item['sale_price'] = _to_float(item['sale_price'])
        item['member_price'] = _to_float(item['member_price'])
        item['stock_total'] = _to_int(item['stock_total'])
        result.append(item)
    return _ok(data=result)


@pos_bp.route('/pos/hold', methods=['POST'])
def pos_hold_save():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    data = request.get_json(silent=True) or {}
    cart = data.get('cart')
    if not isinstance(cart, list) or not cart:
        return _err('挂单商品不能为空')

    hold_no = (data.get('hold_no') or data.get('sale_no') or _generate_sale_no()).strip()
    warehouse_id = data.get('warehouse_id') or None
    sales_staff_id = data.get('sales_staff_id') or None
    terminal_id = data.get('terminal_id') or None
    customer_id = data.get('customer_id') or None
    goods_count = sum(max(_to_int(item.get('quantity'), 0), 0) for item in cart)
    total_amount = sum(_to_float(item.get('subtotal') or item.get('line_total') or item.get('raw_amount')) for item in cart)
    payable_amount = sum(_to_float(item.get('final_amount') or item.get('line_payable') or item.get('payable_amount')) for item in cart)
    remark = (data.get('remark') or '').strip()
    snapshot = data.get('snapshot') or {}
    if not isinstance(snapshot, dict):
        snapshot = {}
    snapshot.setdefault('cart', cart)
    snapshot.setdefault('sale_no', hold_no)

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''INSERT INTO biz_pos_hold_order
                   (hold_no, operator_id, warehouse_id, sales_staff_id, terminal_id,
                    customer_id, goods_count, total_amount, payable_amount, cart_json, remark)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id''',
                (
                    hold_no,
                    operator_id,
                    warehouse_id,
                    sales_staff_id,
                    terminal_id,
                    customer_id,
                    goods_count,
                    total_amount,
                    payable_amount,
                    json.dumps(snapshot, ensure_ascii=False),
                    remark,
                )
            )
            hold_id = cur.fetchone()['id']
        conn.commit()
    except Exception as exc:
        conn.rollback()
        if 'unique' in str(exc).lower():
            return _err('挂单号重复，请重试')
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(data={'id': hold_id, 'hold_no': hold_no}, msg='挂单成功')


@pos_bp.route('/pos/hold/list', methods=['GET'])
def pos_hold_list():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT
                       h.id, h.hold_no, h.operator_id, h.warehouse_id, h.sales_staff_id,
                       h.terminal_id, h.customer_id, h.goods_count, h.total_amount,
                       h.payable_amount, h.cart_json, h.remark, h.created_at,
                       COALESCE(c.name, '散客') AS customer_name
                   FROM biz_pos_hold_order h
                   LEFT JOIN biz_customer c ON h.customer_id = c.id
                   WHERE h.operator_id = %s
                   ORDER BY h.created_at DESC, h.id DESC''',
                (operator_id,)
            )
            rows = cur.fetchall()
    except Exception as exc:
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(data=[_normalize_hold_row(row) for row in rows])


@pos_bp.route('/pos/hold/delete', methods=['DELETE'])
def pos_hold_delete():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    data = request.get_json(silent=True) or {}
    hold_id = data.get('id')
    if not hold_id:
        return _err('缺少挂单 id')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM biz_pos_hold_order WHERE id = %s AND operator_id = %s',
                (hold_id, operator_id)
            )
            if cur.rowcount == 0:
                return _err('挂单不存在', 404)
        conn.commit()
    except Exception as exc:
        conn.rollback()
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(msg='删除成功')


@pos_bp.route('/pos/hold/take', methods=['POST'])
def pos_hold_take():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    data = request.get_json(silent=True) or {}
    hold_id = data.get('id')
    if not hold_id:
        return _err('缺少挂单 id')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT id, hold_no, operator_id, warehouse_id, sales_staff_id,
                          terminal_id, customer_id, goods_count, total_amount,
                          payable_amount, cart_json, remark, created_at
                   FROM biz_pos_hold_order
                   WHERE id = %s AND operator_id = %s''',
                (hold_id, operator_id)
            )
            row = cur.fetchone()
            if not row:
                return _err('挂单不存在', 404)

            cur.execute('DELETE FROM biz_pos_hold_order WHERE id = %s', (hold_id,))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(data=_normalize_hold_row(row), msg='取单成功')


@pos_bp.route('/pos/checkout', methods=['POST'])
def pos_checkout():
    operator_id = _current_user_id()
    if not operator_id:
        return _err('未获取到当前登录用户', 401)

    data = request.get_json(silent=True) or {}
    items = data.get('items') or []
    if not isinstance(items, list) or not items:
        return _err('商品明细不能为空')

    sale_no = (data.get('sale_no') or _generate_sale_no()).strip()
    warehouse_id = data.get('warehouse_id')
    sales_staff_id = data.get('sales_staff_id') or None
    terminal_id = data.get('terminal_id') or None
    customer_id = data.get('customer_id') or None
    payment_method = (data.get('payment_method') or '现金').strip() or '现金'
    remark = (data.get('remark') or '').strip()
    paid_amount = _to_float(data.get('paid_amount'))

    if not warehouse_id:
        return _err('仓库不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            customer = None
            member_discount = 1.0
            if customer_id:
                cur.execute(
                    '''SELECT c.id, c.balance, c.points, mt.discount
                       FROM biz_customer c
                       LEFT JOIN biz_member_type mt ON c.member_type_id = mt.id
                       WHERE c.id = %s''',
                    (customer_id,)
                )
                customer = cur.fetchone()
                if not customer:
                    return _err('顾客不存在', 404)
                member_discount = _to_float(customer.get('discount') or 1)

            computed_items = []
            total_amount = 0.0
            payable_amount = 0.0
            points_total = 0
            goods_count = 0

            for raw_item in items:
                goods_id = raw_item.get('goods_id')
                quantity = _to_int(raw_item.get('quantity'))
                item_warehouse_id = raw_item.get('warehouse_id') or warehouse_id
                if not goods_id or quantity <= 0:
                    return _err('商品明细存在无效数量')

                cur.execute(
                    '''SELECT g.id, g.name, g.sale_price, g.enable_points, g.enable_discount,
                              COALESCE(u.name, '') AS unit_name
                       FROM biz_goods g
                       LEFT JOIN biz_unit u ON g.unit_id = u.id
                       WHERE g.id = %s''',
                    (goods_id,)
                )
                goods = cur.fetchone()
                if not goods:
                    return _err(f'商品不存在: {goods_id}', 404)

                cur.execute(
                    '''SELECT COALESCE(SUM(quantity), 0) AS stock_total
                       FROM biz_goods_stock
                       WHERE goods_id = %s AND warehouse_id = %s''',
                    (goods_id, item_warehouse_id)
                )
                stock_total = _to_int(cur.fetchone()['stock_total'])
                if stock_total < quantity:
                    return _err(f"商品 {goods['name']} 库存不足，当前库存 {stock_total}")

                sale_price = _to_float(goods['sale_price'])
                discount_rate = member_discount if _to_int(goods['enable_discount']) == 1 else 1.0
                final_price = round(sale_price * discount_rate, 2)
                raw_amount = round(sale_price * quantity, 2)
                final_amount = round(final_price * quantity, 2)

                total_amount += raw_amount
                payable_amount += final_amount
                goods_count += quantity
                if customer and _to_int(goods['enable_points']) == 1:
                    points_total += int(final_amount)

                computed_items.append({
                    'goods_id': goods_id,
                    'goods_name_snapshot': goods['name'],
                    'unit_name_snapshot': goods['unit_name'],
                    'quantity': quantity,
                    'sale_price': sale_price,
                    'discount_rate': round(discount_rate, 4),
                    'final_price': final_price,
                    'final_amount': final_amount,
                    'warehouse_id': item_warehouse_id,
                    'enable_points': _to_int(goods['enable_points']),
                    'enable_discount': _to_int(goods['enable_discount']),
                })

            total_amount = round(total_amount, 2)
            payable_amount = round(payable_amount, 2)
            discount_amount = round(total_amount - payable_amount, 2)
            change_amount = round(paid_amount - payable_amount, 2)

            if paid_amount < payable_amount:
                return _err('支付金额不足')

            if payment_method == '余额':
                if not customer:
                    return _err('余额支付必须选择顾客')
                if _to_float(customer['balance']) < payable_amount:
                    return _err('顾客余额不足')

            cur.execute(
                '''INSERT INTO biz_pos_order
                   (sale_no, warehouse_id, sales_staff_id, operator_id, terminal_id, customer_id,
                    goods_count, total_amount, discount_amount, payable_amount,
                    payment_method, paid_amount, change_amount, status, remark)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id''',
                (
                    sale_no,
                    warehouse_id,
                    sales_staff_id,
                    operator_id,
                    terminal_id,
                    customer_id,
                    goods_count,
                    total_amount,
                    discount_amount,
                    payable_amount,
                    payment_method,
                    paid_amount,
                    change_amount,
                    1,
                    remark,
                )
            )
            order_id = cur.fetchone()['id']

            for item in computed_items:
                cur.execute(
                    '''INSERT INTO biz_pos_order_item
                       (order_id, goods_id, goods_name_snapshot, unit_name_snapshot,
                        quantity, sale_price, discount_rate, final_price, final_amount,
                        warehouse_id, enable_points, enable_discount)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (
                        order_id,
                        item['goods_id'],
                        item['goods_name_snapshot'],
                        item['unit_name_snapshot'],
                        item['quantity'],
                        item['sale_price'],
                        item['discount_rate'],
                        item['final_price'],
                        item['final_amount'],
                        item['warehouse_id'],
                        item['enable_points'],
                        item['enable_discount'],
                    )
                )

                remaining = item['quantity']
                cur.execute(
                    '''SELECT id, quantity
                       FROM biz_goods_stock
                       WHERE goods_id = %s AND warehouse_id = %s AND quantity > 0
                       ORDER BY id
                       FOR UPDATE''',
                    (item['goods_id'], item['warehouse_id'])
                )
                stock_rows = cur.fetchall()
                for stock_row in stock_rows:
                    if remaining <= 0:
                        break
                    consume = min(remaining, _to_int(stock_row['quantity']))
                    cur.execute(
                        'UPDATE biz_goods_stock SET quantity = quantity - %s WHERE id = %s',
                        (consume, stock_row['id'])
                    )
                    remaining -= consume
                if remaining > 0:
                    raise ValueError(f"商品 {item['goods_name_snapshot']} 扣减库存失败")

            if customer:
                if points_total > 0:
                    cur.execute(
                        'UPDATE biz_customer SET points = points + %s WHERE id = %s',
                        (points_total, customer_id)
                    )
                if payment_method == '余额':
                    cur.execute(
                        'UPDATE biz_customer SET balance = balance - %s WHERE id = %s',
                        (payable_amount, customer_id)
                    )

        conn.commit()
    except Exception as exc:
        conn.rollback()
        if 'unique' in str(exc).lower():
            return _err('销售单号重复，请重试')
        return _err(str(exc), 500)
    finally:
        conn.close()

    return _ok(data={
        'id': order_id,
        'sale_no': sale_no,
        'goods_count': goods_count,
        'total_amount': total_amount,
        'payable_amount': payable_amount,
        'change_amount': change_amount,
        'next_sale_no': _generate_sale_no(),
    }, msg='结算成功')