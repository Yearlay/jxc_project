-- ============================================================
-- 08_create_basic_tables.sql
-- 计量单位 / 厂家信息 / 车辆信息 / 付款方式
-- ============================================================

-- 计量单位
CREATE TABLE IF NOT EXISTS biz_unit (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO biz_unit (name) VALUES
    ('个'), ('件'), ('瓶'), ('包'), ('箱'), ('KG'), ('升'), ('套');

-- 厂家信息
CREATE TABLE IF NOT EXISTS biz_manufacturer (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    phone        VARCHAR(50)  NOT NULL DEFAULT '',
    address      VARCHAR(200) NOT NULL DEFAULT '',
    license      VARCHAR(100) NOT NULL DEFAULT '',
    bank_account VARCHAR(100) NOT NULL DEFAULT '',
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 车辆信息
CREATE TABLE IF NOT EXISTS biz_vehicle (
    id          SERIAL PRIMARY KEY,
    plate       VARCHAR(20)  NOT NULL UNIQUE,
    owner       VARCHAR(50)  NOT NULL DEFAULT '',
    owner_phone VARCHAR(50)  NOT NULL DEFAULT '',
    remark      VARCHAR(200) NOT NULL DEFAULT '',
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 付款方式
CREATE TABLE IF NOT EXISTS biz_payment (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO biz_payment (name) VALUES
    ('现金'), ('信用卡'), ('支付宝'), ('微信'), ('银行转账');
