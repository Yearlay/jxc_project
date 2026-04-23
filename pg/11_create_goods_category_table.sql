-- ============================================================
-- 11_create_goods_category_table.sql
-- 商品分类
-- ============================================================

CREATE TABLE IF NOT EXISTS goods_category (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50) NOT NULL,
    parent_id  INTEGER     NOT NULL DEFAULT 0 CHECK (parent_id >= 0),
    sort       INTEGER     NOT NULL DEFAULT 0,
    is_system  SMALLINT    NOT NULL DEFAULT 0,
    created_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_goods_category_parent_name UNIQUE (parent_id, name)
);

INSERT INTO goods_category (name, parent_id, sort, is_system)
VALUES ('未分类', 0, 0, 1);

INSERT INTO goods_category (name, parent_id, sort, is_system)
VALUES
    ('食品', 0, 10, 0),
    ('家具', 0, 20, 0),
    ('五金', 0, 30, 0),
    ('饰品', 0, 40, 0);