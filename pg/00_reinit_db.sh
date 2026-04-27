#!/bin/bash

# 数据库连接参数
PG_USER="onepiece"
PG_PASSWORD="yearlay_1987"
PG_ADDRESS="192.168.0.116"
PG_PORT="5432"
DB_NAME="jxc"
DIR="$(cd "$(dirname "$0")" && pwd)"

run_file() {
  PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -f "$DIR/$1"
}

# step 1: 删除数据库 jxc
PGPASSWORD=$PG_PASSWORD dropdb -U $PG_USER -h $PG_ADDRESS -p $PG_PORT --if-exists $DB_NAME
# 按顺序执行 sql 文件
# step 2: 创建数据库
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d postgres -h $PG_ADDRESS -p $PG_PORT -f "$DIR/02_create_db.sql"

# step 3: 创建业务表：sys_user、sys_menu、sys_role_menu，并初始化数据
run_file 03_create_user_and_menu.sql
# step 4: 创建分组表：sys_group、sys_group_menu； 并初始化分组数据
run_file 04_create_group_tables.sql

# step 5: 创建业务表：biz_area（片区信息）、biz_member_type（会员类型），并初始化数据
run_file 05_create_area_membertype_tables.sql
# step 6: 创建业务表：biz_warehouse（仓库管理），并初始化数据
run_file 06_create_warehouse_table.sql
# step 6: 创建系统表：sys_company（企业/门店信息），不插入数据
run_file 07_create_company_table.sql
# step 7: 创建业务表：biz_unit/biz_manufacturer/biz_vehicle/biz_payment，并初始化默认数据
run_file 08_create_basic_tables.sql
# step 9: 创建业务表：biz_purchase_staff/biz_sales_staff/biz_terminal，并初始化默认数据
run_file 09_create_staff_terminal_tables.sql

# step 10: 创建业务表：biz_customer（客户管理），并初始化数据
run_file 10_create_customer_table.sql

# step 11: 创建业务表：goods_category，并初始化默认分类数据
run_file 11_create_goods_category_table.sql
# step 12: 创建业务表：biz_goods（商品表）、biz_goods_stock（商品库存表）
run_file 12_create_goods_tables.sql
# step 13: 创建业务表：POS 销售主表/明细表/挂单表
run_file 13_create_pos_tables.sql
