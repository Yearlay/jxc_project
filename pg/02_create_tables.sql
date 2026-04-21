-- ============================================================
-- 02_create_tables.sql
-- 创建业务表：sys_user、sys_menu、sys_role_menu
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 02_create_tables.sql
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
