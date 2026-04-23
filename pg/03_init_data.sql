-- ============================================================
-- 03_init_data.sql
-- 初始化数据：默认用户、三级菜单、admin 全量权限
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 03_init_data.sql
-- ============================================================

\c jxc;

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
(4,  0, '财务管理', '/finance',    1, 4),
(5,  0, '营业统计', '/statistics', 1, 5),
(6,  0, '系统维护', '/system',     1, 6);

-- ── 采购管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(7,  1, '商品采购单', '/purchase/order',        2, 1),
(8,  1, '采购单查询', '/purchase/query',        2, 2),
(9,  1, '采购退货',   '/purchase/return',       2, 3),
(10, 1, '采购退货单', '/purchase/return-order', 2, 4);

-- ── 销售管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(11, 2, '商品销售',   '/sales/goods',      2, 1),
(12, 2, 'POS销售',    '/sales/pos',        2, 2),
(13, 2, '销售退货',   '/sales/return',     2, 3),
(14, 2, '应收款查询', '/sales/receivable', 2, 4);

-- ── 商品销售 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(15, 11, '商品销售单', '/sales/goods/order', 3, 1),
(16, 11, '销售单查询', '/sales/goods/query', 3, 2);

-- ── POS销售 三级菜单 ───────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(17, 12, 'POS前台销售', '/sales/pos/front',  3, 1),
(18, 12, '销售结算',    '/sales/pos/settle', 3, 2),
(19, 12, 'POS单据查询', '/sales/pos/query',  3, 3);

-- ── 销售退货 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(20, 13, '商品退货单', '/sales/return/order', 3, 1),
(21, 13, '退货单查询', '/sales/return/query', 3, 2);

-- ── 商品管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(22, 3, '商品分类', '/goods/category', 2, 1),
(23, 3, '商品列表', '/goods/list', 2, 2),
(24, 3, '商品报溢', '/goods/surplus',  2, 3),
(25, 3, '商品报损', '/goods/damage',   2, 4);

-- ── 财务管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(26, 4, '应收应付', '/finance/payable', 2, 1),
(27, 4, '日常收支', '/finance/daily',   2, 2),
(28, 4, '数据报表', '/finance/report',  2, 3);

-- ── 应收应付 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(29, 26, '应收款', '/finance/payable/receivable', 3, 1),
(30, 26, '应付款', '/finance/payable/payable',    3, 2),
(31, 26, '还款',   '/finance/payable/repay',      3, 3);

-- ── 营业统计 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(32, 5, '商品采购明细查询', '/statistics/purchase-detail',   2, 1),
(33, 5, '商品采购统计',     '/statistics/purchase-summary',  2, 2),
(34, 5, '营业统计',         '/statistics/business',          2, 3),
(35, 5, '商品销售明细查询', '/statistics/sales-detail',      2, 4),
(36, 5, '商品销售统计',     '/statistics/sales-summary',     2, 5),
(37, 5, '畅销商品排行榜',   '/statistics/bestseller',        2, 6),
(38, 5, '低库存统计',       '/statistics/low-stock',         2, 7),
(39, 5, '过期商品统计',     '/statistics/expired',           2, 8),
(40, 5, '销售利润统计',     '/statistics/profit',            2, 9);

-- ── 系统维护 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(41, 6, '设置企业信息',      '/system/company',     2, 1),
(42, 6, '用户管理',         '/system/user/manage', 2, 2),
(43, 6, '权限组管理',       '/system/user/role',   2, 3),
(44, 6, '生日提醒',         '/system/birthday',    2, 4),
(45, 6, '客户管理',         '/system/customer',    2, 5),
(46, 6, '供货商管理',       '/system/supplier',    2, 6),
(47, 6, '积分管理',         '/system/points',      2, 7),
(48, 6, '基础信息设置',      '/system/basic',       2, 8);

-- ── 基础信息设置 三级菜单 ──────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(49, 48, '仓库',     '/system/basic/warehouse',      3, 1),
(50, 48, '计量单位', '/system/basic/unit',           3, 2),
(51, 48, '厂家信息', '/system/basic/manufacturer',   3, 3),
(52, 48, '会员类型', '/system/basic/member-type',    3, 4),
(53, 48, '片区信息', '/system/basic/area',           3, 5),
(54, 48, '车辆信息', '/system/basic/vehicle',        3, 6),
(55, 48, '付款方式', '/system/basic/payment',        3, 7),
(56, 48, '采购业务员','/system/basic/purchase-staff',3, 8),
(57, 48, '销售业务员','/system/basic/sales-staff',   3, 9),
(58, 48, '销售终端', '/system/basic/branch',         3, 10);

-- 重置序列，避免后续 INSERT 冲突
SELECT setval('sys_menu_id_seq', (SELECT MAX(id) FROM sys_menu));

-- ----------------------------
-- admin 角色全量权限（绑定全部菜单）
-- ----------------------------
INSERT INTO sys_role_menu (role, menu_id)
SELECT 'admin', id FROM sys_menu
ON CONFLICT (role, menu_id) DO NOTHING;
