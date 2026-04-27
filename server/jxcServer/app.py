from flask import Flask, jsonify, request, g
from flask_cors import CORS

import config
from api.auth import auth_bp, verify_token
from api.menu import menu_bp
from api.group import group_bp
from api.user import user_bp
from api.area import area_bp
from api.member_type import member_type_bp
from api.customer import customer_bp
from api.warehouse import warehouse_bp
from api.company import company_bp
from api.basic import basic_bp
from api.staff import staff_bp
from api.goods_category import goods_category_bp
from api.goods import goods_bp
from api.pos import pos_bp

app = Flask(__name__)
CORS(app)  # 允许跨域（开发阶段）

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(menu_bp, url_prefix='/api')
app.register_blueprint(group_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(area_bp, url_prefix='/api')
app.register_blueprint(member_type_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(warehouse_bp, url_prefix='/api')
app.register_blueprint(company_bp, url_prefix='/api')
app.register_blueprint(basic_bp, url_prefix='/api')
app.register_blueprint(staff_bp, url_prefix='/api')
app.register_blueprint(goods_category_bp, url_prefix='/api')
app.register_blueprint(goods_bp, url_prefix='/api')
app.register_blueprint(pos_bp, url_prefix='/api')


# ──────────────────────────────────────────────────────────
# 鉴权中间件：除登录接口外，其余接口均需验证 token
# ──────────────────────────────────────────────────────────
WHITELIST = {'/api/login'}

@app.before_request
def auth_middleware():
    if request.path in WHITELIST:
        return
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify(code=401, msg='未授权，请先登录'), 401
    token = auth_header[7:]
    payload = verify_token(token)
    if payload is None:
        return jsonify(code=401, msg='token 无效或已过期'), 401
    g.current_user = payload


# ──────────────────────────────────────────────────────────
# 统一错误处理
# ──────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify(code=404, msg='接口不存在'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(code=500, msg='服务器内部错误'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)
