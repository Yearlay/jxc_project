from flask import Blueprint, jsonify, request

import db

pos_sales_bp = Blueprint('pos_sales', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


def _to_float(value):
    return float(value or 0)


def _normalize_order_row(row):
    result = dict(row)
    for key in ['total_amount', 'discount_amount', 'payable_amount', 'paid_amount', 'change_amount']:
        result[key] = _to_float(result.get(key))
    created_at = result.get('created_at')
    updated_at = result.get('updated_at')
    result['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
    result['updated_at'] = updated_at.strftime('%Y-%m-%d %H:%M:%S') if updated_at else ''
    result['customer_name'] = result.get('customer_name') or '散客'
    return result


def _normalize_item_row(row):
    result = dict(row)
    for key in ['sale_price', 'discount_rate', 'final_price', 'final_amount']:
        result[key] = _to_float(result.get(key))
    created_at = result.get('created_at')
    result['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
    return result


def _build_goods_summary(items):
    if not items:
        return ''
    preview = [f"{item['goods_name_snapshot']}×{int(item['quantity'] or 0)}" for item in items[:3]]
    if len(items) > 3:
        preview.append(f'等{len(items)}项')
    return '，'.join(preview)


@pos_sales_bp.route('/pos-sales/list', methods=['GET'])
def pos_sales_list():
    sale_no = request.args.get('sale_no', '').strip()
    customer_name = request.args.get('customer_name', '').strip()
    warehouse_id = request.args.get('warehouse_id', type=int, default=0)
    sales_staff_id = request.args.get('sales_staff_id', type=int, default=0)
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', type=int, default=1)
    page_size = request.args.get('page_size', type=int, default=10)

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    offset = (page - 1) * page_size

    where_clauses = ['o.status = 1']
    params = []

    if sale_no:
        where_clauses.append('o.sale_no ILIKE %s')
        params.append(f'%{sale_no}%')
    if customer_name:
        where_clauses.append("COALESCE(c.name, '散客') ILIKE %s")
        params.append(f'%{customer_name}%')
    if warehouse_id > 0:
        where_clauses.append('o.warehouse_id = %s')
        params.append(warehouse_id)
    if sales_staff_id > 0:
        where_clauses.append('o.sales_staff_id = %s')
        params.append(sales_staff_id)
    if start_date:
        where_clauses.append('o.created_at >= %s::date')
        params.append(start_date)
    if end_date:
        where_clauses.append("o.created_at < (%s::date + INTERVAL '1 day')")
        params.append(end_date)

    where_sql = 'WHERE ' + ' AND '.join(where_clauses)
    base_sql = f'''
        FROM biz_pos_order o
        LEFT JOIN biz_warehouse w ON o.warehouse_id = w.id
        LEFT JOIN biz_sales_staff ss ON o.sales_staff_id = ss.id
        LEFT JOIN sys_user su ON o.operator_id = su.id
        LEFT JOIN biz_terminal t ON o.terminal_id = t.id
        LEFT JOIN biz_customer c ON o.customer_id = c.id
        {where_sql}
    '''

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f'SELECT COUNT(*) AS total {base_sql}', params)
            total = cur.fetchone()['total']

            cur.execute(
                f'''
                SELECT
                    o.id,
                    o.sale_no,
                    o.warehouse_id,
                    COALESCE(w.name, '') AS warehouse_name,
                    o.sales_staff_id,
                    COALESCE(ss.name, '') AS sales_staff_name,
                    o.operator_id,
                    COALESCE(NULLIF(su.real_name, ''), su.username, '') AS operator_name,
                    o.terminal_id,
                    COALESCE(t.name, '') AS terminal_name,
                    o.customer_id,
                    COALESCE(c.name, '散客') AS customer_name,
                    o.goods_count,
                    o.total_amount,
                    o.discount_amount,
                    o.payable_amount,
                    o.payment_method,
                    o.paid_amount,
                    o.change_amount,
                    o.status,
                    o.remark,
                    o.created_at,
                    o.updated_at
                {base_sql}
                ORDER BY o.id DESC
                LIMIT %s OFFSET %s
                ''',
                params + [page_size, offset]
            )
            rows = cur.fetchall()

            order_ids = [row['id'] for row in rows]
            items_by_order = {}
            if order_ids:
                cur.execute(
                    '''SELECT order_id, goods_name_snapshot, quantity
                       FROM biz_pos_order_item
                       WHERE order_id = ANY(%s)
                       ORDER BY id ASC''',
                    (order_ids,)
                )
                for item in cur.fetchall():
                    items_by_order.setdefault(item['order_id'], []).append(item)
    except Exception as exc:
        return _err(str(exc), 500)
    finally:
        conn.close()

    result = []
    for row in rows:
        order = _normalize_order_row(row)
        order['goods_summary'] = _build_goods_summary(items_by_order.get(order['id'], []))
        result.append(order)

    return _ok(data={'list': result, 'total': total})


@pos_sales_bp.route('/pos-sales/detail', methods=['GET'])
def pos_sales_detail():
    order_id = request.args.get('id', type=int)
    if not order_id:
        return _err('缺少销售单 id')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT
                       o.id,
                       o.sale_no,
                       o.warehouse_id,
                       COALESCE(w.name, '') AS warehouse_name,
                       o.sales_staff_id,
                       COALESCE(ss.name, '') AS sales_staff_name,
                       o.operator_id,
                       COALESCE(NULLIF(su.real_name, ''), su.username, '') AS operator_name,
                       o.terminal_id,
                       COALESCE(t.name, '') AS terminal_name,
                       o.customer_id,
                       COALESCE(c.name, '散客') AS customer_name,
                       COALESCE(c.contact, '') AS customer_contact,
                       COALESCE(c.phone, '') AS customer_phone,
                       o.goods_count,
                       o.total_amount,
                       o.discount_amount,
                       o.payable_amount,
                       o.payment_method,
                       o.paid_amount,
                       o.change_amount,
                       o.status,
                       o.remark,
                       o.created_at,
                       o.updated_at
                   FROM biz_pos_order o
                   LEFT JOIN biz_warehouse w ON o.warehouse_id = w.id
                   LEFT JOIN biz_sales_staff ss ON o.sales_staff_id = ss.id
                   LEFT JOIN sys_user su ON o.operator_id = su.id
                   LEFT JOIN biz_terminal t ON o.terminal_id = t.id
                   LEFT JOIN biz_customer c ON o.customer_id = c.id
                   WHERE o.id = %s AND o.status = 1''',
                (order_id,)
            )
            order = cur.fetchone()
            if not order:
                return _err('销售单不存在', 404)

            cur.execute(
                '''SELECT
                       i.id,
                       i.order_id,
                       i.goods_id,
                       i.goods_name_snapshot,
                       i.unit_name_snapshot,
                       i.quantity,
                       i.sale_price,
                       i.discount_rate,
                       i.final_price,
                       i.final_amount,
                       i.warehouse_id,
                       COALESCE(w.name, '') AS warehouse_name,
                       i.enable_points,
                       i.enable_discount,
                       i.created_at
                   FROM biz_pos_order_item i
                   LEFT JOIN biz_warehouse w ON i.warehouse_id = w.id
                   WHERE i.order_id = %s
                   ORDER BY i.id ASC''',
                (order_id,)
            )
            items = cur.fetchall()
    except Exception as exc:
        return _err(str(exc), 500)
    finally:
        conn.close()

    order_data = _normalize_order_row(order)
    item_list = [_normalize_item_row(item) for item in items]
    order_data['goods_summary'] = _build_goods_summary(item_list)
    order_data['items'] = item_list
    return _ok(data=order_data)