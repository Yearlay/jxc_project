from flask import Blueprint, jsonify, g
import db

menu_bp = Blueprint('menu', __name__)


# ──────────────────────────────────────────────────────────
# GET /api/menu
# 返回当前用户有权限的三级菜单树
# ──────────────────────────────────────────────────────────
@menu_bp.route('/menu', methods=['GET'])
def get_menu():
    role = g.current_user['role']

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            if role == 'admin':
                # admin 返回全部菜单
                cur.execute(
                    'SELECT id, parent_id, name, path, level, sort '
                    'FROM sys_menu WHERE status = 1 ORDER BY level, sort'
                )
            else:
                # 按角色权限过滤
                cur.execute(
                    'SELECT m.id, m.parent_id, m.name, m.path, m.level, m.sort '
                    'FROM sys_menu m '
                    'JOIN sys_role_menu rm ON rm.menu_id = m.id '
                    'WHERE rm.role = %s AND m.status = 1 '
                    'ORDER BY m.level, m.sort',
                    (role,),
                )
            rows = cur.fetchall()
    finally:
        conn.close()

    # 构建三级树
    tree = _build_tree([dict(r) for r in rows])
    return jsonify(code=200, msg='ok', data=tree)


def _build_tree(items: list) -> list:
    id_map = {item['id']: item for item in items}
    roots = []
    for item in items:
        item['children'] = []
        pid = item['parent_id']
        if pid == 0 or pid not in id_map:
            roots.append(item)
        else:
            id_map[pid]['children'].append(item)
    return roots
