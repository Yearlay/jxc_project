-- ============================================================
-- 03_create_user_and_menu.sql
-- 创建业务表：sys_user、sys_menu、sys_role_menu
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 03_create_user_and_menu.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 用户表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_user (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(64)  NOT NULL,              -- MD5 加密
    real_name   VARCHAR(50)  NOT NULL DEFAULT '',
    role        VARCHAR(20)  NOT NULL DEFAULT 'staff', -- admin / staff
    status      SMALLINT     NOT NULL DEFAULT 1,    -- 1:启用 0:禁用
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  sys_user             IS '系统用户表';
COMMENT ON COLUMN sys_user.username    IS '登录用户名';
COMMENT ON COLUMN sys_user.password    IS '登录密码（MD5）';
COMMENT ON COLUMN sys_user.real_name   IS '真实姓名';
COMMENT ON COLUMN sys_user.role        IS '角色：admin=管理员 staff=普通用户';
COMMENT ON COLUMN sys_user.status      IS '状态：1=启用 0=禁用';

-- ----------------------------
-- 菜单表（三级结构）
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_menu (
    id          SERIAL PRIMARY KEY,
    parent_id   INT          NOT NULL DEFAULT 0,    -- 0 表示顶级菜单
    name        VARCHAR(50)  NOT NULL,
    path        VARCHAR(100) NOT NULL DEFAULT '',   -- 前端路由路径
    level       SMALLINT     NOT NULL DEFAULT 1,    -- 1/2/3
    sort        SMALLINT     NOT NULL DEFAULT 0,
    status      SMALLINT     NOT NULL DEFAULT 1     -- 1:显示 0:隐藏
);

COMMENT ON TABLE  sys_menu            IS '系统菜单表';
COMMENT ON COLUMN sys_menu.parent_id  IS '父菜单ID，0表示顶级';
COMMENT ON COLUMN sys_menu.path       IS '前端路由路径';
COMMENT ON COLUMN sys_menu.level      IS '菜单层级：1/2/3';
COMMENT ON COLUMN sys_menu.sort       IS '同级排序（越小越靠前）';

-- ----------------------------
-- 角色权限关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id      SERIAL PRIMARY KEY,
    role    VARCHAR(20) NOT NULL,  -- 对应 sys_user.role
    menu_id INT         NOT NULL,
    UNIQUE (role, menu_id)
);

COMMENT ON TABLE  sys_role_menu         IS '角色菜单权限关联表';
COMMENT ON COLUMN sys_role_menu.role    IS '角色名称，与 sys_user.role 一致';
COMMENT ON COLUMN sys_role_menu.menu_id IS '菜单ID，关联 sys_menu.id';

-- ----------------------------
-- 默认用户（admin / 123456）
-- password = MD5('123456') = e10adc3949ba59abbe56e057f20f883e
-- ----------------------------
INSERT INTO sys_user (username, password, real_name, role, status)
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin', 1)
ON CONFLICT (username) DO NOTHING;

-- ----------------------------
-- 菜单数据（三级，与 design/account_and_menu.md 保持一致）
-- ----------------------------
TRUNCATE TABLE sys_role_menu;
TRUNCATE TABLE sys_menu RESTART IDENTITY CASCADE;

-- ── 一级菜单 ──────────────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(1,  0, '采购管理', '/purchase',   1, 1),
(2,  0, '销售管理', '/sales',      1, 2),
(3,  0, '商品管理', '/goods',      1, 3),
(4,  0, '客户管理', '/customer',   1, 4),
(5,  0, '财务管理', '/finance',    1, 5),
(6,  0, '营业统计', '/statistics', 1, 6),
(7,  0, '系统维护', '/system',     1, 7);

-- ── 采购管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(8,  1, '商品采购单', '/purchase/order',        2, 1),
(9,  1, '采购单查询', '/purchase/query',        2, 2),
(10,  1, '采购退货',   '/purchase/return',       2, 3),
(11, 1, '采购退货单', '/purchase/return-order', 2, 4);

-- ── 销售管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(12, 2, 'POS销售',    '/sales/pos',        2, 1),
(13, 2, '商品销售',   '/sales/goods',      2, 2),
(14, 2, '销售退货',   '/sales/return',     2, 3),
(15, 2, '应收款查询', '/sales/receivable', 2, 4);

-- ── 商品管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(16, 3, '商品分类', '/goods/category', 2, 1),
(17, 3, '商品列表', '/goods/list', 2, 2),
(18, 3, '商品报溢', '/goods/surplus',  2, 3),
(19, 3, '商品报损', '/goods/damage',   2, 4);

-- ── 财务管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(20, 5, '应收应付', '/finance/payable', 2, 1),
(21, 5, '日常收支', '/finance/daily',   2, 2),
(22, 5, '数据报表', '/finance/report',  2, 3);

-- ── 应收应付 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(23, 20, '应收款', '/finance/payable/receivable', 3, 1),
(24, 20, '应付款', '/finance/payable/payable',    3, 2),
(25, 20, '还款',   '/finance/payable/repay',      3, 3);

-- ── 营业统计 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(26, 6, '商品采购明细查询', '/statistics/purchase-detail',   2, 1),
(27, 6, '商品采购统计',     '/statistics/purchase-summary',  2, 2),
(28, 6, '营业统计',         '/statistics/business',          2, 3),
(29, 6, '商品销售明细查询', '/statistics/sales-detail',      2, 4),
(30, 6, '商品销售统计',     '/statistics/sales-summary',     2, 5),
(31, 6, '畅销商品排行榜',   '/statistics/bestseller',        2, 6),
(32, 6, '低库存统计',       '/statistics/low-stock',         2, 7),
(33, 6, '过期商品统计',     '/statistics/expired',           2, 8),
(34, 6, '销售利润统计',     '/statistics/profit',            2, 9);

-- ── 系统维护 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(35, 7, '设置企业信息',      '/system/company',     2, 1),
(36, 7, '用户管理',         '/system/user/manage', 2, 2),
(37, 7, '权限组管理',       '/system/user/role',   2, 3),
(38, 7, '生日提醒',         '/system/birthday',    2, 4),
(39, 7, '供货商管理',       '/system/supplier',    2, 5),
(40, 7, '积分管理',         '/system/points',      2, 6),
(41, 7, '基础信息设置',      '/system/basic',       2, 7);

-- ── 基础信息设置 三级菜单 ──────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(49, 41, '仓库',     '/system/basic/warehouse',      3, 1),
(50, 41, '计量单位', '/system/basic/unit',           3, 2),
(51, 41, '厂家信息', '/system/basic/manufacturer',   3, 3),
(52, 41, '会员类型', '/system/basic/member-type',    3, 4),
(53, 41, '片区信息', '/system/basic/area',           3, 5),
(54, 41, '车辆信息', '/system/basic/vehicle',        3, 6),
(55, 41, '付款方式', '/system/basic/payment',        3, 7),
(56, 41, '采购业务员','/system/basic/purchase-staff',3, 8),
(57, 41, '销售业务员','/system/basic/sales-staff',   3, 9),
(58, 41, '销售终端', '/system/basic/branch',         3, 10);

-- 重置序列，避免后续 INSERT 冲突
SELECT setval('sys_menu_id_seq', (SELECT MAX(id) FROM sys_menu));

-- ----------------------------
-- admin 角色全量权限（绑定全部菜单）
-- ----------------------------
INSERT INTO sys_role_menu (role, menu_id)
SELECT 'admin', id FROM sys_menu
ON CONFLICT (role, menu_id) DO NOTHING;
