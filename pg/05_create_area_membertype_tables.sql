-- ============================================================
-- 05_create_area_membertype_tables.sql
-- 创建业务表：biz_area（片区信息）、biz_member_type（会员类型）
-- 初始化数据：默认片区【未划分】，常见会员类型4条
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 05_create_area_membertype_tables.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 片区信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_area (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)   NOT NULL UNIQUE,
    remark      VARCHAR(200)  NOT NULL DEFAULT '',
    is_default  SMALLINT      NOT NULL DEFAULT 0,    -- 1:系统默认（未划分）0:普通
    status      SMALLINT      NOT NULL DEFAULT 1,    -- 1:启用 0:禁用
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  biz_area             IS '片区信息表';
COMMENT ON COLUMN biz_area.name        IS '片区名称（唯一）';
COMMENT ON COLUMN biz_area.remark      IS '备注';
COMMENT ON COLUMN biz_area.is_default  IS '是否默认片区：1=是（未划分）0=否';
COMMENT ON COLUMN biz_area.status      IS '状态：1=启用 0=禁用';

-- ----------------------------
-- 会员类型表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_member_type (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)   NOT NULL UNIQUE,
    discount    NUMERIC(4,2)  NOT NULL DEFAULT 1.00, -- 折扣率，如 0.88 = 88折
    remark      VARCHAR(200)  NOT NULL DEFAULT '',
    status      SMALLINT      NOT NULL DEFAULT 1,    -- 1:启用 0:禁用
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  biz_member_type           IS '会员类型表';
COMMENT ON COLUMN biz_member_type.name      IS '会员类型名称（唯一）';
COMMENT ON COLUMN biz_member_type.discount  IS '折扣率（0.01~1.00，如0.88=88折）';
COMMENT ON COLUMN biz_member_type.remark    IS '备注';
COMMENT ON COLUMN biz_member_type.status    IS '状态：1=启用 0=禁用';

-- ----------------------------
-- 初始化：默认片区【未划分】
-- ----------------------------
-- 初始化：默认片区【未划分】及常用片区
-- ----------------------------
INSERT INTO biz_area (name, remark, is_default, status)
VALUES
    ('未划分', '系统默认片区，不可删除', 1, 1),
    ('华东片区', '上海/江苏/浙江等', 0, 1),
    ('华北片区', '北京/天津/河北等', 0, 1),
    ('华南片区', '广州/深圳/广西等', 0, 1),
    ('华中片区', '武汉/成都/重庆等', 0, 1),
    ('华西片区', '陕西/四川/云南等', 0, 1)
ON CONFLICT (name) DO NOTHING;

-- ----------------------------
-- 初始化：常见会员类型
-- ----------------------------
INSERT INTO biz_member_type (name, discount, remark)
VALUES
    ('普通会员', 1.00, '无折扣'),
    ('银卡会员', 0.95, '95折优惠'),
    ('金卡会员', 0.88, '88折优惠'),
    ('钻石会员', 0.80, '8折优惠')
ON CONFLICT (name) DO NOTHING;
