-- ============================================================
-- 09_create_staff_terminal_tables.sql
-- 采购业务员 / 销售业务员 / 销售终端
-- ============================================================

-- 采购业务员
CREATE TABLE IF NOT EXISTS biz_purchase_staff (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(50)   NOT NULL,
    phone          VARCHAR(50)   NOT NULL DEFAULT '',
    address        VARCHAR(200)  NOT NULL DEFAULT '',
    is_default     SMALLINT      NOT NULL DEFAULT 0,
    purchase_limit NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at     TIMESTAMP     NOT NULL DEFAULT NOW()
);

INSERT INTO biz_purchase_staff (name, is_default) VALUES ('店长', 1);

-- 销售业务员
CREATE TABLE IF NOT EXISTS biz_sales_staff (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50)  NOT NULL,
    phone           VARCHAR(50)  NOT NULL DEFAULT '',
    address         VARCHAR(200) NOT NULL DEFAULT '',
    is_default      SMALLINT     NOT NULL DEFAULT 0,
    commission_rate NUMERIC(5,4) NOT NULL DEFAULT 0,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

INSERT INTO biz_sales_staff (name, is_default) VALUES ('店长', 1);

-- 销售终端
CREATE TABLE IF NOT EXISTS biz_terminal (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    code       VARCHAR(50)  NOT NULL UNIQUE,
    is_default SMALLINT     NOT NULL DEFAULT 0,
    db_no      VARCHAR(100) NOT NULL DEFAULT '',
    created_at TIMESTAMP    NOT NULL DEFAULT NOW()
);

INSERT INTO biz_terminal (name, code, is_default) VALUES ('门店终端001', 'T001', 1);
