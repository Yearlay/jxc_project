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

# step 1: 创建数据库
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d postgres -h $PG_ADDRESS -p $PG_PORT -f 01_create_db.sql
# step 2: 创建业务表：sys_user、sys_menu、sys_role_menu
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 02_create_tables.sql
# step 3: 初始化数据：sys_user、sys_menu、sys_role_menu
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 03_init_data.sql
# step 4: 创建分组表：sys_group、sys_group_menu； 并初始化分组数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 04_create_group_tables.sql
# step 5: 创建业务表：biz_area（片区信息）、biz_member_type（会员类型），并初始化数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 05_create_area_membertype_tables.sql
# step 6: 创建业务表：biz_customer（客户管理），并初始化数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 06_create_customer_table.sql
# step 7: 创建业务表：biz_warehouse（仓库管理），并初始化数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 07_create_warehouse_table.sql
