-- ============================================================
-- 07_create_warehouse_table.sql
-- 创建业务表：biz_warehouse（仓库管理）
-- 初始化数据：5 条示例仓库
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 07_create_warehouse_table.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 仓库信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_warehouse (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL UNIQUE,
    address     VARCHAR(200)  NOT NULL DEFAULT '',
    remark      VARCHAR(200)  NOT NULL DEFAULT '',
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  biz_warehouse            IS '仓库信息表';
COMMENT ON COLUMN biz_warehouse.name       IS '仓库名称（唯一）';
COMMENT ON COLUMN biz_warehouse.address    IS '仓库地址';
COMMENT ON COLUMN biz_warehouse.remark     IS '备注';
COMMENT ON COLUMN biz_warehouse.created_at IS '创建时间';

-- ----------------------------
-- 初始化：示例仓库数据
-- ----------------------------
INSERT INTO biz_warehouse (name, address, remark)
VALUES
    ('北京总仓',   '北京市朝阳区望京街道1号',     '集团总仓库'),
    ('上海分仓',   '上海市浦东新区张江高科技园区', '华东区分仓'),
    ('广州分仓',   '广州市天河区科韵路66号',       '华南区分仓'),
    ('成都分仓',   '成都市高新区天府大道100号',    '西南区分仓'),
    ('武汉分仓',   '武汉市江汉区建设大道200号',    '华中区分仓')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------
-- 为 sys_user 追加 warehouse_id / area_id 字段及外键约束
-- （此处执行是因为 biz_warehouse/biz_area 在本文件之前已建好）
-- ----------------------------
ALTER TABLE sys_user
    ADD COLUMN IF NOT EXISTS warehouse_ids INTEGER[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS area_ids      INTEGER[] DEFAULT '{}';

COMMENT ON COLUMN sys_user.warehouse_ids IS '操作仓库ID列表（多选）';
COMMENT ON COLUMN sys_user.area_ids      IS '管辖片区ID列表（多选）';
