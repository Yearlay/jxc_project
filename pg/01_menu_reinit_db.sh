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

run_sql() {
  PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $DB_NAME -h $PG_ADDRESS -p $PG_PORT -c "$1"
}

echo "==========================================="
echo " JXC 数据库重置工具"
echo "==========================================="
echo "  1) ALL      - 删除数据库，全部重建"
echo "  2) 账户菜单 - 重置账户/权限/菜单数据/基础数据  (step 3~9)"
echo "  3) 客户数据 - 重置客户数据             (step 10)"
echo "  4) 商品数据 - 重置商品分类/商品/库存   (step 11~12)"
echo "  5) POS数据  - 重置前台销售/挂单数据    (step 13)"
echo "  q) 退出"
echo "==========================================="
read -p "请选择 [1-5/q]: " CHOICE
echo ""

case "$CHOICE" in
  1)
    echo ">>> [ALL] 全部重建..."
    PGPASSWORD=$PG_PASSWORD dropdb -U $PG_USER -h $PG_ADDRESS -p $PG_PORT --if-exists $DB_NAME
    PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d postgres -h $PG_ADDRESS -p $PG_PORT -f "$DIR/02_create_db.sql"
    run_file 03_create_user_and_menu.sql
    run_file 04_create_group_tables.sql
    run_file 05_create_area_membertype_tables.sql
    run_file 06_create_warehouse_table.sql
    run_file 07_create_company_table.sql
    run_file 08_create_basic_tables.sql
    run_file 09_create_staff_terminal_tables.sql
    run_file 10_create_customer_table.sql
    run_file 11_create_goods_category_table.sql
    run_file 12_create_goods_tables.sql
    run_file 13_create_pos_tables.sql
    echo ">>> 全部重建完成！"
    ;;

  2)
    echo ">>> [账户菜单] 重置账户/权限/菜单/基础数据..."
    run_sql "
      DROP TABLE IF EXISTS sys_group_user  CASCADE;
      DROP TABLE IF EXISTS sys_group_menu  CASCADE;
      DROP TABLE IF EXISTS sys_role_menu   CASCADE;
      DROP TABLE IF EXISTS sys_menu        CASCADE;
      DROP TABLE IF EXISTS sys_user        CASCADE;
      DROP TABLE IF EXISTS sys_group       CASCADE;
      DROP TABLE IF EXISTS biz_goods_stock    CASCADE;
      DROP TABLE IF EXISTS biz_goods          CASCADE;
      DROP TABLE IF EXISTS goods_category     CASCADE;
      DROP TABLE IF EXISTS biz_customer       CASCADE;
      DROP TABLE IF EXISTS biz_purchase_staff CASCADE;
      DROP TABLE IF EXISTS biz_sales_staff    CASCADE;
      DROP TABLE IF EXISTS biz_terminal       CASCADE;
      DROP TABLE IF EXISTS biz_payment        CASCADE;
      DROP TABLE IF EXISTS biz_vehicle        CASCADE;
      DROP TABLE IF EXISTS biz_manufacturer   CASCADE;
      DROP TABLE IF EXISTS biz_unit           CASCADE;
      DROP TABLE IF EXISTS sys_company        CASCADE;
      DROP TABLE IF EXISTS biz_warehouse      CASCADE;
      DROP TABLE IF EXISTS biz_member_type    CASCADE;
      DROP TABLE IF EXISTS biz_area           CASCADE;
    "
    run_file 03_create_user_and_menu.sql
    run_file 04_create_group_tables.sql
    run_file 05_create_area_membertype_tables.sql
    run_file 06_create_warehouse_table.sql
    run_file 07_create_company_table.sql
    run_file 08_create_basic_tables.sql
    run_file 09_create_staff_terminal_tables.sql
    echo ">>> 账户和菜单重置完成！"
    ;;

  3)
    echo ">>> [客户数据] 重置客户数据..."
    run_sql "DROP TABLE IF EXISTS biz_customer CASCADE;"
    run_file 10_create_customer_table.sql
    echo ">>> 客户数据重置完成！"
    ;;

  4)
    echo ">>> [商品数据] 重置商品分类/商品/库存..."
    run_sql "
      DROP TABLE IF EXISTS biz_pos_order_item CASCADE;
      DROP TABLE IF EXISTS biz_pos_order      CASCADE;
      DROP TABLE IF EXISTS biz_goods_stock CASCADE;
      DROP TABLE IF EXISTS biz_goods       CASCADE;
      DROP TABLE IF EXISTS goods_category  CASCADE;
    "
    run_file 11_create_goods_category_table.sql
    run_file 12_create_goods_tables.sql
    run_file 13_create_pos_tables.sql
    echo ">>> 商品数据重置完成！"
    ;;

  5)
    echo ">>> [POS数据] 重置前台销售/挂单数据..."
    run_sql "
      DROP TABLE IF EXISTS biz_pos_order_item CASCADE;
      DROP TABLE IF EXISTS biz_pos_order      CASCADE;
      DROP TABLE IF EXISTS biz_pos_hold_order CASCADE;
    "
    run_file 13_create_pos_tables.sql
    echo ">>> POS 数据重置完成！"
    ;;

  q|Q)
    echo "已退出。"
    exit 0
    ;;

  *)
    echo "无效选项，请输入 1~5 或 q"
    exit 1
    ;;
esac
