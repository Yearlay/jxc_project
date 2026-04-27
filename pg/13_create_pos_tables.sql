-- ============================================================
-- 13_create_pos_tables.sql
-- 创建 POS 前台销售相关表
-- ============================================================

\c jxc;

-- ----------------------------
-- 仓库表增加默认仓库字段
-- ----------------------------
ALTER TABLE biz_warehouse
ADD COLUMN IF NOT EXISTS is_default SMALLINT NOT NULL DEFAULT 0;

COMMENT ON COLUMN biz_warehouse.is_default IS '是否默认仓库：1=是 0=否';

UPDATE biz_warehouse SET is_default = 0;
UPDATE biz_warehouse SET is_default = 1 WHERE name = '北京总仓';

-- ----------------------------
-- POS 销售主表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_pos_order (
    id              SERIAL PRIMARY KEY,
    sale_no         VARCHAR(40)    NOT NULL UNIQUE,
    warehouse_id    INTEGER        NOT NULL REFERENCES biz_warehouse(id),
    sales_staff_id  INTEGER        REFERENCES biz_sales_staff(id) ON DELETE SET NULL,
    operator_id     INTEGER        NOT NULL REFERENCES sys_user(id),
    terminal_id     INTEGER        REFERENCES biz_terminal(id) ON DELETE SET NULL,
    customer_id     INTEGER        REFERENCES biz_customer(id) ON DELETE SET NULL,
    goods_count     INTEGER        NOT NULL DEFAULT 0,
    total_amount    NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    discount_amount NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    payable_amount  NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    payment_method  VARCHAR(20)    NOT NULL DEFAULT '现金',
    paid_amount     NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    change_amount   NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    status          SMALLINT       NOT NULL DEFAULT 0,
    remark          VARCHAR(200)   NOT NULL DEFAULT '',
    created_at      TIMESTAMP      NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP      NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE biz_pos_order IS 'POS 销售主表';
COMMENT ON COLUMN biz_pos_order.sale_no IS '销售单号';
COMMENT ON COLUMN biz_pos_order.goods_count IS '商品总数';
COMMENT ON COLUMN biz_pos_order.total_amount IS '总金额';
COMMENT ON COLUMN biz_pos_order.discount_amount IS '优惠金额';
COMMENT ON COLUMN biz_pos_order.payable_amount IS '折后价/应付金额';
COMMENT ON COLUMN biz_pos_order.payment_method IS '付款方式';
COMMENT ON COLUMN biz_pos_order.paid_amount IS '支付金额';
COMMENT ON COLUMN biz_pos_order.change_amount IS '应找金额';
COMMENT ON COLUMN biz_pos_order.status IS '状态：0=待结算 1=已结算';

-- ----------------------------
-- POS 销售明细表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_pos_order_item (
    id                   SERIAL PRIMARY KEY,
    order_id             INTEGER        NOT NULL REFERENCES biz_pos_order(id) ON DELETE CASCADE,
    goods_id             INTEGER        NOT NULL REFERENCES biz_goods(id),
    goods_name_snapshot  VARCHAR(100)   NOT NULL DEFAULT '',
    unit_name_snapshot   VARCHAR(20)    NOT NULL DEFAULT '',
    quantity             INTEGER        NOT NULL DEFAULT 1,
    sale_price           NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    discount_rate        NUMERIC(5,4)   NOT NULL DEFAULT 1.0000,
    final_price          NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    final_amount         NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    warehouse_id         INTEGER        NOT NULL REFERENCES biz_warehouse(id),
    enable_points        SMALLINT       NOT NULL DEFAULT 0,
    enable_discount      SMALLINT       NOT NULL DEFAULT 0,
    created_at           TIMESTAMP      NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE biz_pos_order_item IS 'POS 销售明细表';
COMMENT ON COLUMN biz_pos_order_item.goods_name_snapshot IS '商品名称快照';
COMMENT ON COLUMN biz_pos_order_item.unit_name_snapshot IS '单位名称快照';
COMMENT ON COLUMN biz_pos_order_item.sale_price IS '原价';
COMMENT ON COLUMN biz_pos_order_item.discount_rate IS '折扣率';
COMMENT ON COLUMN biz_pos_order_item.final_price IS '折后单价';
COMMENT ON COLUMN biz_pos_order_item.final_amount IS '折后小计';
COMMENT ON COLUMN biz_pos_order_item.enable_points IS '是否参与积分：1=是 0=否';
COMMENT ON COLUMN biz_pos_order_item.enable_discount IS '是否参与折扣：1=是 0=否';

-- ----------------------------
-- POS 挂单表
-- ----------------------------
CREATE TABLE IF NOT EXISTS biz_pos_hold_order (
    id              SERIAL PRIMARY KEY,
    hold_no         VARCHAR(40)    NOT NULL UNIQUE,
    operator_id     INTEGER        NOT NULL REFERENCES sys_user(id),
    warehouse_id    INTEGER        REFERENCES biz_warehouse(id) ON DELETE SET NULL,
    sales_staff_id  INTEGER        REFERENCES biz_sales_staff(id) ON DELETE SET NULL,
    terminal_id     INTEGER        REFERENCES biz_terminal(id) ON DELETE SET NULL,
    customer_id     INTEGER        REFERENCES biz_customer(id) ON DELETE SET NULL,
    goods_count     INTEGER        NOT NULL DEFAULT 0,
    total_amount    NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    payable_amount  NUMERIC(12,2)  NOT NULL DEFAULT 0.00,
    cart_json       TEXT           NOT NULL DEFAULT '[]',
    remark          VARCHAR(200)   NOT NULL DEFAULT '',
    created_at      TIMESTAMP      NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE biz_pos_hold_order IS 'POS 挂单表';
COMMENT ON COLUMN biz_pos_hold_order.hold_no IS '挂单号';
COMMENT ON COLUMN biz_pos_hold_order.cart_json IS '购物车快照 JSON';
