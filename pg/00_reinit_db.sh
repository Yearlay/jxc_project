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
# step 8: 创建系统表：sys_company（企业/门店信息），不插入数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 08_create_company_table.sql
# step 9: 创建业务表：biz_unit/biz_manufacturer/biz_vehicle/biz_payment，并初始化默认数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 09_create_basic_tables.sql
# step 10: 创建业务表：biz_purchase_staff/biz_sales_staff/biz_terminal，并初始化默认数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 10_create_staff_terminal_tables.sql
# step 11: 创建业务表：goods_category，并初始化默认分类数据
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 11_create_goods_category_table.sql
# step 12: 创建业务表：biz_goods（商品表）、biz_goods_stock（商品库存表）
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f 12_create_goods_tables.sql
