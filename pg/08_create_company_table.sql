-- ============================================================
-- 08_create_company_table.sql
-- 创建系统表：sys_company（企业/门店信息）
-- 全局仅一条数据，初始化时不插入数据
-- 执行方式：psql -U onepiece -d jxc -h 192.168.0.116 -p 5432 -W -f 08_create_company_table.sql
-- ============================================================

\c jxc;

-- ----------------------------
-- 企业/门店信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_company (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    phone       VARCHAR(50)   NOT NULL,
    address     VARCHAR(200)  NOT NULL DEFAULT '',
    updated_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  sys_company            IS '企业/门店信息表（全局唯一一条）';
COMMENT ON COLUMN sys_company.name       IS '企业/门店名称';
COMMENT ON COLUMN sys_company.phone      IS '企业/门店电话';
COMMENT ON COLUMN sys_company.address    IS '企业/门店地址';
COMMENT ON COLUMN sys_company.updated_at IS '最后更新时间';
