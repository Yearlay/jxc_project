#!/bin/bash 00_reinit_db.sh

# 数据库连接参数
PG_USER="onepiece"
PG_PASSWORD="yearlay_1987"
PG_ADDRESS="192.168.0.116"
PG_PORT="5432"
DB_NAME="jxc"

# 删除数据库 jxc
PGPASSWORD=$PG_PASSWORD dropdb -U $PG_USER -h $PG_ADDRESS -p $PG_PORT --if-exists $DB_NAME

# 按顺序执行 sql 文件
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d postgres -h $PG_ADDRESS -p $PG_PORT -f 01_create_db.sql
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 02_create_tables.sql
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 03_init_data.sql
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 04_create_group_tables.sql