-- ============================================================
-- 01_create_db.sql
-- 创建数据库 jxc
-- 执行方式：psql -U onepiece -d postgres -h 192.168.0.116 -p 5432 -W -f 01_create_db.sql
-- ============================================================

CREATE DATABASE jxc
    WITH
    OWNER = onepiece
    ENCODING = 'UTF8'
    TEMPLATE = template0;
