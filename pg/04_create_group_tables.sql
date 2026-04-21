-- ============================================================
-- 04_create_group_tables.sql
-- 创建权限组相关表：sys_group、sys_group_menu、sys_group_user
-- 同时为 sys_user 表增加 group_id 字段
-- 初始化数据：【管理员】【普通成员】两个权限组，admin 加入【管理员】
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 04_create_group_tables.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 权限组表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_group (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)   NOT NULL UNIQUE,
    remark      VARCHAR(200)  NOT NULL DEFAULT '',
    status      SMALLINT      NOT NULL DEFAULT 1,    -- 1:启用 0:禁用
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  sys_group            IS '权限组表';
COMMENT ON COLUMN sys_group.name       IS '权限组名称（唯一）';
COMMENT ON COLUMN sys_group.remark     IS '备注';
COMMENT ON COLUMN sys_group.status     IS '状态：1=启用 0=禁用';

-- ----------------------------
-- 权限组菜单关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_group_menu (
    id          SERIAL PRIMARY KEY,
    group_id    INT  NOT NULL,
    menu_id     INT  NOT NULL,
    UNIQUE (group_id, menu_id)
);

COMMENT ON TABLE  sys_group_menu           IS '权限组菜单关联表';
COMMENT ON COLUMN sys_group_menu.group_id  IS '权限组ID，关联 sys_group.id';
COMMENT ON COLUMN sys_group_menu.menu_id   IS '菜单ID，关联 sys_menu.id';

-- ----------------------------
-- 权限组成员关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_group_user (
    id          SERIAL PRIMARY KEY,
    group_id    INT  NOT NULL,
    user_id     INT  NOT NULL,
    UNIQUE (group_id, user_id)
);

COMMENT ON TABLE  sys_group_user           IS '权限组成员关联表';
COMMENT ON COLUMN sys_group_user.group_id  IS '权限组ID，关联 sys_group.id';
COMMENT ON COLUMN sys_group_user.user_id   IS '用户ID，关联 sys_user.id';

-- ----------------------------
-- sys_user 增加 group_id 字段（若已存在则跳过）
-- ----------------------------
ALTER TABLE sys_user
    ADD COLUMN IF NOT EXISTS group_id INT DEFAULT NULL;

COMMENT ON COLUMN sys_user.group_id IS '所属权限组ID，关联 sys_group.id';

-- ----------------------------
-- 初始化权限组数据
-- ----------------------------
INSERT INTO sys_group (name, remark)
VALUES
    ('管理员', '系统管理员权限组，拥有全部菜单权限'),
    ('普通成员', '普通成员权限组，默认无菜单权限')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------
-- 【管理员】权限组关联全部菜单
-- ----------------------------
INSERT INTO sys_group_menu (group_id, menu_id)
SELECT
    (SELECT id FROM sys_group WHERE name = '管理员'),
    id
FROM sys_menu
ON CONFLICT (group_id, menu_id) DO NOTHING;

-- ----------------------------
-- admin 用户加入【管理员】权限组
-- ----------------------------
INSERT INTO sys_group_user (group_id, user_id)
SELECT
    (SELECT id FROM sys_group WHERE name = '管理员'),
    (SELECT id FROM sys_user WHERE username = 'admin')
ON CONFLICT (group_id, user_id) DO NOTHING;

-- 同步更新 sys_user.group_id
UPDATE sys_user
SET group_id = (SELECT id FROM sys_group WHERE name = '管理员')
WHERE username = 'admin';
