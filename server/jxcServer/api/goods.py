from flask import Blueprint, request, jsonify
from datetime import timedelta
import db

goods_bp = Blueprint('goods', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# 商品接口
# ──────────────────────────────────────────────────────────

@goods_bp.route('/goods/list', methods=['GET'])
def goods_list():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    keyword = request.args.get('keyword', '').strip()
    category_id = int(request.args.get('category_id', 0))

    offset = (page - 1) * page_size
    conditions = []
    params = []

    if keyword:
        conditions.append("(g.name ILIKE %s OR g.code ILIKE %s)")
        params += [f'%{keyword}%', f'%{keyword}%']
    if category_id:
        conditions.append("g.category_id = %s")
        params.append(category_id)

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    sql_count = f'''
        SELECT COUNT(*) as cnt
        FROM biz_goods g
        {where}
    '''
    sql_list = f'''
        SELECT
            g.id, g.code, g.other_code, g.name,
            g.category_id,
            COALESCE(gc.name, '') AS category_name,
            g.purchase_price, g.sale_price, g.member_price, g.wholesale_price,
            g.unit_id,
            COALESCE(u.name, '') AS unit_name,
            g.manufacturer_id,
            COALESCE(m.name, '') AS manufacturer_name,
            g.stock_min, g.shelf_life,
            g.enable_points, g.enable_discount,
            g.created_at,
            COALESCE((
                SELECT SUM(s.quantity)
                FROM biz_goods_stock s
                WHERE s.goods_id = g.id
            ), 0) AS stock_total
        FROM biz_goods g
        LEFT JOIN goods_category gc ON g.category_id = gc.id
        LEFT JOIN biz_unit u ON g.unit_id = u.id
        LEFT JOIN biz_manufacturer m ON g.manufacturer_id = m.id
        {where}
        ORDER BY g.id DESC
        LIMIT %s OFFSET %s
    '''

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_count, params)
            total = cur.fetchone()['cnt']
            cur.execute(sql_list, params + [page_size, offset])
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()

    result = []
    for row in rows:
        d = dict(row)
        d['stock_total'] = int(d['stock_total'])
        d['purchase_price'] = float(d['purchase_price'])
        d['sale_price'] = float(d['sale_price'])
        d['member_price'] = float(d['member_price'])
        d['wholesale_price'] = float(d['wholesale_price'])
        d['created_at'] = str(d['created_at'])
        result.append(d)

    return _ok(data={'total': total, 'list': result})


@goods_bp.route('/goods/add', methods=['POST'])
def goods_add():
    data = request.get_json(force=True) or {}
    code = data.get('code', '').strip()
    name = data.get('name', '').strip()
    if not code:
        return _err('商品编码不能为空')
    if not name:
        return _err('商品名称不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_goods WHERE code = %s', (code,))
            if cur.fetchone():
                return _err(f'商品编码 "{code}" 已存在')
            cur.execute(
                '''INSERT INTO biz_goods
                   (code, other_code, name, category_id,
                    purchase_price, sale_price, member_price, wholesale_price,
                    unit_id, manufacturer_id, stock_min, shelf_life,
                    enable_points, enable_discount)
                   VALUES (%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s)
                   RETURNING id''',
                (
                    code,
                    data.get('other_code', ''),
                    name,
                    int(data.get('category_id', 0)),
                    float(data.get('purchase_price', 0)),
                    float(data.get('sale_price', 0)),
                    float(data.get('member_price', 0)),
                    float(data.get('wholesale_price', 0)),
                    int(data.get('unit_id', 0)),
                    int(data.get('manufacturer_id', 0)),
                    int(data.get('stock_min', 0)),
                    int(data.get('shelf_life', 0)),
                    int(data.get('enable_points', 0)),
                    int(data.get('enable_discount', 0)),
                )
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(data={'id': new_id}, msg='新增成功')


@goods_bp.route('/goods/update', methods=['PUT'])
def goods_update():
    data = request.get_json(force=True) or {}
    gid = data.get('id')
    if not gid:
        return _err('id 不能为空')
    code = data.get('code', '').strip()
    name = data.get('name', '').strip()
    if not code:
        return _err('商品编码不能为空')
    if not name:
        return _err('商品名称不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_goods WHERE code = %s AND id != %s', (code, gid))
            if cur.fetchone():
                return _err(f'商品编码 "{code}" 已被其他商品使用')
            cur.execute(
                '''UPDATE biz_goods SET
                   code=%s, other_code=%s, name=%s, category_id=%s,
                   purchase_price=%s, sale_price=%s, member_price=%s, wholesale_price=%s,
                   unit_id=%s, manufacturer_id=%s, stock_min=%s, shelf_life=%s,
                   enable_points=%s, enable_discount=%s
                   WHERE id=%s''',
                (
                    code,
                    data.get('other_code', ''),
                    name,
                    int(data.get('category_id', 0)),
                    float(data.get('purchase_price', 0)),
                    float(data.get('sale_price', 0)),
                    float(data.get('member_price', 0)),
                    float(data.get('wholesale_price', 0)),
                    int(data.get('unit_id', 0)),
                    int(data.get('manufacturer_id', 0)),
                    int(data.get('stock_min', 0)),
                    int(data.get('shelf_life', 0)),
                    int(data.get('enable_points', 0)),
                    int(data.get('enable_discount', 0)),
                    gid,
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='修改成功')


@goods_bp.route('/goods/delete', methods=['DELETE'])
def goods_delete():
    data = request.get_json(force=True) or {}
    gid = data.get('id')
    if not gid:
        return _err('id 不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT COALESCE(SUM(quantity),0) AS total FROM biz_goods_stock WHERE goods_id=%s',
                (gid,)
            )
            total = int(cur.fetchone()['total'])
            if total > 0:
                return _err(f'该商品当前库存为 {total}，不允许删除')
            cur.execute('SELECT name FROM biz_goods WHERE id=%s', (gid,))
            row = cur.fetchone()
            if not row:
                return _err('商品不存在')
            cur.execute('DELETE FROM biz_goods_stock WHERE goods_id=%s', (gid,))
            cur.execute('DELETE FROM biz_goods WHERE id=%s', (gid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='删除成功')


# ──────────────────────────────────────────────────────────
# 商品库存接口
# ──────────────────────────────────────────────────────────

@goods_bp.route('/goods/stock/list', methods=['GET'])
def stock_list():
    goods_id = request.args.get('goods_id')
    if not goods_id:
        return _err('goods_id 不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT
                       s.id, s.goods_id, s.warehouse_id,
                       COALESCE(w.name,'') AS warehouse_name,
                       s.spec, s.batch_no, s.size, s.color,
                       s.produce_date, s.quantity, s.created_at,
                       g.shelf_life
                   FROM biz_goods_stock s
                   LEFT JOIN biz_warehouse w ON s.warehouse_id = w.id
                   LEFT JOIN biz_goods g ON s.goods_id = g.id
                   WHERE s.goods_id = %s
                   ORDER BY s.id''',
                (int(goods_id),)
            )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()

    result = []
    for row in rows:
        d = dict(row)
        d['created_at'] = str(d['created_at'])
        # 计算有效日期
        if d['produce_date'] and d['shelf_life']:
            expire = d['produce_date'] + timedelta(days=d['shelf_life'])
            d['expire_date'] = str(expire)
        else:
            d['expire_date'] = None
        d['produce_date'] = str(d['produce_date']) if d['produce_date'] else None
        del d['shelf_life']
        result.append(d)

    return _ok(data=result)


@goods_bp.route('/goods/stock/add', methods=['POST'])
def stock_add():
    data = request.get_json(force=True) or {}
    goods_id = data.get('goods_id')
    warehouse_id = data.get('warehouse_id')
    quantity = data.get('quantity')
    if not goods_id:
        return _err('goods_id 不能为空')
    if not warehouse_id:
        return _err('warehouse_id 不能为空')
    if quantity is None or int(quantity) <= 0:
        return _err('增加数量必须大于 0')

    produce_date = data.get('produce_date') or None

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''INSERT INTO biz_goods_stock
                   (goods_id, warehouse_id, spec, batch_no, size, color, produce_date, quantity)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                   RETURNING id''',
                (
                    int(goods_id),
                    int(warehouse_id),
                    data.get('spec', ''),
                    data.get('batch_no', ''),
                    data.get('size', ''),
                    data.get('color', ''),
                    produce_date,
                    int(quantity),
                )
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(data={'id': new_id}, msg='库存已增加')


@goods_bp.route('/goods/stock/update', methods=['PUT'])
def stock_update():
    data = request.get_json(force=True) or {}
    sid = data.get('id')
    if not sid:
        return _err('id 不能为空')
    quantity = data.get('quantity')
    if quantity is None or int(quantity) < 0:
        return _err('数量不能为负数')

    produce_date = data.get('produce_date') or None

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM biz_goods_stock WHERE id=%s', (sid,))
            if not cur.fetchone():
                return _err('库存记录不存在')
            cur.execute(
                '''UPDATE biz_goods_stock SET
                   warehouse_id=%s, spec=%s, batch_no=%s, size=%s, color=%s,
                   produce_date=%s, quantity=%s
                   WHERE id=%s''',
                (
                    int(data.get('warehouse_id', 0)),
                    data.get('spec', ''),
                    data.get('batch_no', ''),
                    data.get('size', ''),
                    data.get('color', ''),
                    produce_date,
                    int(quantity),
                    sid,
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='库存盘点成功')


@goods_bp.route('/goods/stock/transfer', methods=['POST'])
def stock_transfer():
    data = request.get_json(force=True) or {}
    goods_id = data.get('goods_id')
    from_wh = data.get('from_warehouse_id')
    to_wh = data.get('to_warehouse_id')
    quantity = data.get('quantity')

    if not goods_id or not from_wh or not to_wh:
        return _err('goods_id、from_warehouse_id、to_warehouse_id 不能为空')
    if not quantity or int(quantity) <= 0:
        return _err('调拨数量必须大于 0')
    if int(from_wh) == int(to_wh):
        return _err('源仓库和目标仓库不能相同')

    quantity = int(quantity)
    goods_id = int(goods_id)
    from_wh = int(from_wh)
    to_wh = int(to_wh)

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            # 查源仓库总库存
            cur.execute(
                '''SELECT COALESCE(SUM(quantity),0) AS total
                   FROM biz_goods_stock
                   WHERE goods_id=%s AND warehouse_id=%s''',
                (goods_id, from_wh)
            )
            src_total = int(cur.fetchone()['total'])
            if src_total < quantity:
                return _err(f'源仓库库存不足（当前 {src_total}，调拨 {quantity}）')

            # 从源仓库逐条扣减，直到扣完
            cur.execute(
                '''SELECT id, quantity FROM biz_goods_stock
                   WHERE goods_id=%s AND warehouse_id=%s AND quantity > 0
                   ORDER BY id''',
                (goods_id, from_wh)
            )
            src_rows = cur.fetchall()
            remaining = quantity
            for row in src_rows:
                if remaining <= 0:
                    break
                deduct = min(row['quantity'], remaining)
                new_qty = row['quantity'] - deduct
                cur.execute('UPDATE biz_goods_stock SET quantity=%s WHERE id=%s', (new_qty, row['id']))
                remaining -= deduct

            # 在目标仓库新增一条记录
            cur.execute(
                '''INSERT INTO biz_goods_stock (goods_id, warehouse_id, quantity)
                   VALUES (%s, %s, %s)''',
                (goods_id, to_wh, quantity)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='调拨成功')
