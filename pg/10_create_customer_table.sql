-- ============================================================
-- 10_create_customer_table.sql
-- 创建业务表：biz_customer（客户管理）
-- 初始化数据：5~8 条示例客户
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 10_create_customer_table.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 客户信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_customer (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50)     NOT NULL UNIQUE,
    name            VARCHAR(100)    NOT NULL,
    contact         VARCHAR(50)     NOT NULL DEFAULT '',
    phone           VARCHAR(20)     NOT NULL DEFAULT '',
    address         VARCHAR(200)    NOT NULL DEFAULT '',
    area_id         INTEGER         REFERENCES biz_area(id) ON DELETE SET NULL,
    salesman        INTEGER         REFERENCES sys_user(id) ON DELETE SET NULL,
    member_type_id  INTEGER         REFERENCES biz_member_type(id) ON DELETE SET NULL,
    member_no       VARCHAR(50)     NOT NULL UNIQUE,
    birthday        DATE,
    points          INTEGER         NOT NULL DEFAULT 0,
    balance         NUMERIC(10,2)   NOT NULL DEFAULT 0.00,
    status          SMALLINT        NOT NULL DEFAULT 1,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  biz_customer                  IS '客户信息表';
COMMENT ON COLUMN biz_customer.code             IS '客户编号（唯一，格式 C{年}{序号4位}）';
COMMENT ON COLUMN biz_customer.name             IS '客户名称';
COMMENT ON COLUMN biz_customer.contact          IS '联系人';
COMMENT ON COLUMN biz_customer.phone            IS '联系电话';
COMMENT ON COLUMN biz_customer.address          IS '联系地址';
COMMENT ON COLUMN biz_customer.area_id          IS '所属片区（关联 biz_area.id）';
COMMENT ON COLUMN biz_customer.salesman         IS '所属业务员（关联 sys_user.id）';
COMMENT ON COLUMN biz_customer.member_type_id   IS '会员类型（关联 biz_member_type.id）';
COMMENT ON COLUMN biz_customer.member_no        IS '会员号（唯一，格式 M{年}{序号4位}）';
COMMENT ON COLUMN biz_customer.birthday         IS '会员生日';
COMMENT ON COLUMN biz_customer.points           IS '积分（默认 0）';
COMMENT ON COLUMN biz_customer.balance          IS '账户余额（默认 0.00）';
COMMENT ON COLUMN biz_customer.status           IS '状态：1=启用 0=禁用';

-- ----------------------------
-- 初始化示例数据
-- 依赖：biz_area（id=1 未划分，id=2 华东片区，id=3 华北片区，id=4 华南片区，id=5 华中片区，id=6 华西片区）
--       biz_member_type（id=1 普通会员，id=2 银卡会员，id=3 金卡会员，id=4 钻石会员）
-- ----------------------------
INSERT INTO biz_customer (code, name, contact, phone, address, area_id, salesman, member_type_id, member_no, birthday, points, balance, status)
VALUES
  ('C20240001', '上海贸易有限公司',    '张伟', '021-88776655', '上海市浦东新区张江路88号',     2, 1, 3, 'M20240001', '1985-03-12', 1580, 500.00,  1),
  ('C20240002', '北京科技发展有限公司', '王芳', '010-66554433', '北京市海淀区中关村南大街5号',  3, 1, 2, 'M20240002', '1990-07-25', 320,  200.00,  1),
  ('C20240003', '广州南方贸易公司',    '陈刚', '020-38887766', '广州市天河区天河路385号',       4, 1, 4, 'M20240003', '1978-11-08', 2300, 1200.00, 1),
  ('C20240004', '深圳创新科技有限公司', '刘洋', '0755-86541234','深圳市南山区科技园南区3栋',    4, 1, 3, 'M20240004', '1995-01-30', 780,  350.00,  1),
  ('C20240005', '成都西部贸易中心',    '吴敏', '028-87654321', '成都市锦江区春熙路66号',       5, 1, 1, 'M20240005', NULL,         150,  0.00,    1),
  ('C20240006', '杭州互联网服务公司',  '周涛', '0571-88990011','杭州市余杭区文一西路',         2, 1, 2, 'M20240006', '1988-06-18', 560,  800.00,  1),
  ('C20240007', '武汉物流配送有限公司', '孙丽', '027-65432100', '武汉市江汉区解放大道388号',   1, NULL, 1, 'M20240007', NULL,       0,    0.00,    0);
