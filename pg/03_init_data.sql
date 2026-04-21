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
(23, 3, '库存信息', '/goods/stock',    2, 2),
(24, 3, '商品报溢', '/goods/surplus',  2, 3),
(25, 3, '商品拆装', '/goods/assembly', 2, 4),
(26, 3, '商品报损', '/goods/damage',   2, 5);

-- ── 库存信息 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(27, 23, '增加新物品', '/goods/stock/add',      3, 1),
(28, 23, '修改物品信息','/goods/stock/edit',    3, 2),
(29, 23, '增加库存',   '/goods/stock/increase', 3, 3),
(30, 23, '库存盘点',   '/goods/stock/check',    3, 4),
(31, 23, '库存调拨',   '/goods/stock/transfer', 3, 5);

-- ── 商品报溢 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(32, 24, '商品报溢单', '/goods/surplus/order', 3, 1),
(33, 24, '报溢单查询', '/goods/surplus/query', 3, 2);

-- ── 商品拆装 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(34, 25, '商品拆装单', '/goods/assembly/order', 3, 1),
(35, 25, '拆装单查询', '/goods/assembly/query', 3, 2);

-- ── 商品报损 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(36, 26, '商品报损单', '/goods/damage/order', 3, 1),
(37, 26, '报损单查询', '/goods/damage/query', 3, 2);

-- ── 财务管理 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(38, 4, '应收应付', '/finance/payable', 2, 1),
(39, 4, '日常收支', '/finance/daily',   2, 2),
(40, 4, '数据报表', '/finance/report',  2, 3);

-- ── 应收应付 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(41, 38, '应收款', '/finance/payable/receivable', 3, 1),
(42, 38, '应付款', '/finance/payable/payable',    3, 2),
(43, 38, '还款',   '/finance/payable/repay',      3, 3);

-- ── 营业统计 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(44, 5, '商品采购明细查询', '/statistics/purchase-detail',   2, 1),
(45, 5, '商品采购统计',     '/statistics/purchase-summary',  2, 2),
(46, 5, '营业统计',         '/statistics/business',          2, 3),
(47, 5, '商品销售明细查询', '/statistics/sales-detail',      2, 4),
(48, 5, '商品销售统计',     '/statistics/sales-summary',     2, 5),
(49, 5, '畅销商品排行榜',   '/statistics/bestseller',        2, 6),
(50, 5, '低库存统计',       '/statistics/low-stock',         2, 7),
(51, 5, '过期商品统计',     '/statistics/expired',           2, 8),
(52, 5, '销售利润统计',     '/statistics/profit',            2, 9);

-- ── 系统维护 二级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(53, 6, '设置企业信息',     '/system/company',     2, 1),
(54, 6, '基础信息设置',     '/system/basic',       2, 2),
(55, 6, '商品基础信息设置', '/system/goods-basic', 2, 3),
(56, 6, '登陆密码修改',     '/system/password',    2, 4),
(57, 6, '用户管理',         '/system/user',        2, 5),
(58, 6, '生日提醒',         '/system/birthday',    2, 6),
(59, 6, '顾客管理',         '/system/customer',    2, 7),
(60, 6, '供货商管理',       '/system/supplier',    2, 8),
(61, 6, '积分管理',         '/system/points',      2, 9);

-- ── 基础信息设置 三级菜单 ──────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(62, 54, '仓库',     '/system/basic/warehouse',      3, 1),
(63, 54, '计量单位', '/system/basic/unit',           3, 2),
(64, 54, '厂家信息', '/system/basic/manufacturer',   3, 3),
(65, 54, '会员类型', '/system/basic/member-type',    3, 4),
(66, 54, '片区信息', '/system/basic/area',           3, 5),
(67, 54, '车辆信息', '/system/basic/vehicle',        3, 6),
(68, 54, '付款方式', '/system/basic/payment',        3, 7),
(69, 54, '采购业务员','/system/basic/purchase-staff',3, 8),
(70, 54, '销售业务员','/system/basic/sales-staff',   3, 9),
(71, 54, '分店终端', '/system/basic/branch',         3, 10);

-- ── 用户管理 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(72, 57, '增加用户',   '/system/user/add',    3, 1),
(73, 57, '修改用户',   '/system/user/edit',   3, 2),
(74, 57, '删除用户',   '/system/user/delete', 3, 3),
(75, 57, '权限组管理', '/system/user/role',   3, 4);

-- ── 顾客管理 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(76, 59, '创建客户',     '/system/customer/add',      3, 1),
(77, 59, '修改客户信息', '/system/customer/edit',     3, 2),
(78, 59, '删除客户',     '/system/customer/delete',   3, 3),
(79, 59, '账户充值',     '/system/customer/recharge', 3, 4),
(80, 59, '客户信息查询', '/system/customer/query',    3, 5);

-- ── 积分管理 三级菜单 ──────────────────────────────────────
INSERT INTO sys_menu (id, parent_id, name, path, level, sort) VALUES
(81, 61, '积分兑换',     '/system/points/exchange',  3, 1),
(82, 61, '礼品设置',     '/system/points/gift-setup',3, 2),
(83, 61, '选择礼品',     '/system/points/select',    3, 3),
(84, 61, '确认兑换',     '/system/points/confirm',   3, 4),
(85, 61, '积分兑换记录', '/system/points/records',   3, 5);

-- 重置序列，避免后续 INSERT 冲突
SELECT setval('sys_menu_id_seq', (SELECT MAX(id) FROM sys_menu));

-- ----------------------------
-- admin 角色全量权限（绑定全部 85 个菜单）
-- ----------------------------
INSERT INTO sys_role_menu (role, menu_id)
SELECT 'admin', id FROM sys_menu
ON CONFLICT (role, menu_id) DO NOTHING;
