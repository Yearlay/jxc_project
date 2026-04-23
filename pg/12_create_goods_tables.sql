-- 12_create_goods_tables.sql
-- 商品表 + 商品库存表

-- ──────────────────────────────────────────────
-- 表一：biz_goods 商品表
-- ──────────────────────────────────────────────
CREATE TABLE biz_goods (
    id               SERIAL PRIMARY KEY,
    code             VARCHAR(50)    NOT NULL UNIQUE,
    other_code       VARCHAR(50)    NOT NULL DEFAULT '',
    name             VARCHAR(100)   NOT NULL,
    category_id      INTEGER        NOT NULL DEFAULT 0,
    purchase_price   NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    sale_price       NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    member_price     NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    wholesale_price  NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    unit_id          INTEGER        NOT NULL DEFAULT 0,
    manufacturer_id  INTEGER        NOT NULL DEFAULT 0,
    stock_min        INTEGER        NOT NULL DEFAULT 0,
    shelf_life       INTEGER        NOT NULL DEFAULT 0,
    enable_points    SMALLINT       NOT NULL DEFAULT 0,
    enable_discount  SMALLINT       NOT NULL DEFAULT 0,
    created_at       TIMESTAMP      NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN biz_goods.code             IS '商品编码（唯一）';
COMMENT ON COLUMN biz_goods.other_code       IS '其他编码';
COMMENT ON COLUMN biz_goods.category_id      IS '关联 goods_category.id，0=未分类';
COMMENT ON COLUMN biz_goods.purchase_price   IS '采购价（成本价）';
COMMENT ON COLUMN biz_goods.sale_price       IS '销售价（普通顾客）';
COMMENT ON COLUMN biz_goods.member_price     IS '会员价';
COMMENT ON COLUMN biz_goods.wholesale_price  IS '批发价';
COMMENT ON COLUMN biz_goods.unit_id          IS '关联 biz_unit.id，0=无';
COMMENT ON COLUMN biz_goods.manufacturer_id  IS '关联 biz_manufacturer.id，0=无';
COMMENT ON COLUMN biz_goods.stock_min        IS '库存下限（预警值）';
COMMENT ON COLUMN biz_goods.shelf_life       IS '保质期天数，0=不限';
COMMENT ON COLUMN biz_goods.enable_points    IS '参与积分：1=是 0=否';
COMMENT ON COLUMN biz_goods.enable_discount  IS '参与会员折扣：1=是 0=否';

-- ──────────────────────────────────────────────
-- 表二：biz_goods_stock 商品库存表
-- ──────────────────────────────────────────────
CREATE TABLE biz_goods_stock (
    id            SERIAL PRIMARY KEY,
    goods_id      INTEGER       NOT NULL,
    warehouse_id  INTEGER       NOT NULL,
    spec          VARCHAR(100)  NOT NULL DEFAULT '',
    batch_no      VARCHAR(100)  NOT NULL DEFAULT '',
    size          VARCHAR(50)   NOT NULL DEFAULT '',
    color         VARCHAR(50)   NOT NULL DEFAULT '',
    produce_date  DATE,
    quantity      INTEGER       NOT NULL DEFAULT 0,
    created_at    TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN biz_goods_stock.goods_id      IS '关联 biz_goods.id';
COMMENT ON COLUMN biz_goods_stock.warehouse_id  IS '关联 biz_warehouse.id';
COMMENT ON COLUMN biz_goods_stock.spec          IS '规格';
COMMENT ON COLUMN biz_goods_stock.batch_no      IS '批号';
COMMENT ON COLUMN biz_goods_stock.size          IS '尺码';
COMMENT ON COLUMN biz_goods_stock.color         IS '颜色';
COMMENT ON COLUMN biz_goods_stock.produce_date  IS '生产日期（可空）';
COMMENT ON COLUMN biz_goods_stock.quantity      IS '当前库存数量';
