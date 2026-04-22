from flask import Blueprint, request, jsonify
import db

company_bp = Blueprint('company', __name__)


def _ok(data=None, msg='success'):
    return jsonify(code=200, msg=msg, data=data)


def _err(msg, code=400):
    return jsonify(code=code, msg=msg), code


# ──────────────────────────────────────────────────────────
# GET /api/company/get  获取企业信息（全局唯一一条）
# ──────────────────────────────────────────────────────────
@company_bp.route('/company/get', methods=['GET'])
def company_get():
    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, phone, address FROM sys_company LIMIT 1')
            row = cur.fetchone()
    except Exception as e:
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(data=row)


# ──────────────────────────────────────────────────────────
# POST /api/company/save  保存企业信息（upsert）
# Body: { name, phone, address }
# ──────────────────────────────────────────────────────────
@company_bp.route('/company/save', methods=['POST'])
def company_save():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()

    if not name:
        return _err('企业名称不能为空')
    if not phone:
        return _err('企业电话不能为空')
    if not address:
        return _err('企业地址不能为空')

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM sys_company LIMIT 1')
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    'UPDATE sys_company SET name=%s, phone=%s, address=%s, updated_at=NOW() WHERE id=%s',
                    (name, phone, address, existing['id'])
                )
            else:
                cur.execute(
                    'INSERT INTO sys_company (name, phone, address) VALUES (%s, %s, %s)',
                    (name, phone, address)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return _err(str(e), 500)
    finally:
        conn.close()
    return _ok(msg='保存成功')
