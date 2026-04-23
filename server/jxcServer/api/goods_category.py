from flask import Blueprint, request, jsonify
import db

goods_category_bp = Blueprint('goods_category', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


def _fetch_category(cur, category_id):
    cur.execute(
        '''SELECT id, name, parent_id, sort, is_system
           FROM goods_category
           WHERE id = %s''',
        (category_id,)
    )
    return cur.fetchone()


def _get_category_level(cur, category):
    level = 1
    current_parent_id = category['parent_id']
    while current_parent_id and current_parent_id != 0:
        parent = _fetch_category(cur, current_parent_id)
        if not parent:
            break
        level += 1
        current_parent_id = parent['parent_id']
    return level


def _build_tree(rows):
    node_map = {
        row['id']: {
            'id': row['id'],
            'name': row['name'],
            'parent_id': row['parent_id'],
            'sort': row['sort'],
            'is_system': row['is_system'],
            'children': [],
        }
        for row in rows
    }

    roots = []
    for row in rows:
        node = node_map[row['id']]
        if row['parent_id'] == 0:
            roots.append(node)
        elif row['parent_id'] in node_map:
            node_map[row['parent_id']]['children'].append(node)

    return roots


@goods_category_bp.route('/goods-category/tree', methods=['GET'])
def goods_category_tree():
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''SELECT id, name, parent_id, sort, is_system
                   FROM goods_category
                   ORDER BY parent_id, sort, id'''
            )
            rows = cur.fetchall()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(data=_build_tree(rows))


@goods_category_bp.route('/goods-category/add', methods=['POST'])
def goods_category_add():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    parent_id = data.get('parent_id', 0)

    if not name:
        return _err('分类名称不能为空')
    try:
        parent_id = int(parent_id)
    except (TypeError, ValueError):
        return _err('父分类参数无效')
    if parent_id < 0:
        return _err('父分类参数无效')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if parent_id != 0:
                parent = _fetch_category(cur, parent_id)
                if not parent:
                    return _err('父分类不存在', 404)
                if parent['is_system'] == 1:
                    return _err('未分类下不允许新增子分类')
                if _get_category_level(cur, parent) >= 3:
                    return _err('商品分类最多支持三级结构')

            cur.execute(
                'SELECT id FROM goods_category WHERE parent_id = %s AND name = %s',
                (parent_id, name)
            )
            if cur.fetchone():
                return _err('同级分类名称已存在')

            cur.execute(
                '''INSERT INTO goods_category (name, parent_id)
                   VALUES (%s, %s)
                   RETURNING id''',
                (name, parent_id)
            )
            new_id = cur.fetchone()['id']
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'uq_goods_category_parent_name' in str(e):
            return _err('同级分类名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(data={'id': new_id}, msg='新建成功')


@goods_category_bp.route('/goods-category/update', methods=['PUT'])
def goods_category_update():
    data = request.get_json(silent=True) or {}
    category_id = data.get('id')
    name = (data.get('name') or '').strip()

    if not category_id:
        return _err('id 不能为空')
    if not name:
        return _err('分类名称不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            category = _fetch_category(cur, category_id)
            if not category:
                return _err('分类不存在', 404)
            if category['is_system'] == 1:
                return _err('系统默认分类不允许修改')

            cur.execute(
                '''SELECT id FROM goods_category
                   WHERE parent_id = %s AND name = %s AND id != %s''',
                (category['parent_id'], name, category_id)
            )
            if cur.fetchone():
                return _err('同级分类名称已存在')

            cur.execute(
                'UPDATE goods_category SET name = %s WHERE id = %s',
                (name, category_id)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if 'uq_goods_category_parent_name' in str(e):
            return _err('同级分类名称已存在')
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='更新成功')


@goods_category_bp.route('/goods-category/delete', methods=['DELETE'])
def goods_category_delete():
    data = request.get_json(silent=True) or {}
    category_id = data.get('id')
    if not category_id:
        return _err('id 不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            category = _fetch_category(cur, category_id)
            if not category:
                return _err('分类不存在', 404)
            if category['is_system'] == 1:
                return _err('系统默认分类不允许删除')

            cur.execute('SELECT id FROM goods_category WHERE parent_id = %s LIMIT 1', (category_id,))
            if cur.fetchone():
                return _err('请先删除子分类')

            cur.execute('DELETE FROM goods_category WHERE id = %s', (category_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()

    return _ok(msg='删除成功')