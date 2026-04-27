# POS销售界面-AI

**功能**：实现二级菜单页面
- 销售管理 → POS销售

---

# 文档目标

本文档用于补全和完善“POS销售”列表页设计，作为后续 AI coding 的直接依据。

本页面不是前台收银页面，而是【POS前台销售】完成结算后产生的销售记录查询页，目标是：
- 让操作员、店长、财务能够快速查询已完成的 POS 销售记录
- 支持按多个条件筛选历史销售单
- 以列表页方式查看销售摘要，并支持查看单据详情
- 页面风格与 [client/jxcClient/src/views/AreaManage.vue](client/jxcClient/src/views/AreaManage.vue) 保持一致，采用标准增删改查列表页风格，但本页面以“查询 + 查看”为主，不强调增删改

---

# 一、输入理解

## 1. UI 风格参考

页面风格参考 [client/jxcClient/src/views/AreaManage.vue](client/jxcClient/src/views/AreaManage.vue)：
- 顶部为工具栏 / 查询栏
- 下方为 Ant Design Vue 的表格列表
- 页面整体为标准后台管理页风格
- 不需要状态列
- 不需要新建按钮作为主入口

## 2. POS销售数据来源

POS销售页面展示的是【POS前台销售】中“已完成结算”的销售记录。

建议数据来源：
- 主表：`biz_pos_order`
- 明细表：`biz_pos_order_item`

## 3. 查询业务说明

页面需支持以下筛选方式：
- 按销售单号查询
- 按客户名称查询
- 按仓库过滤查询
- 按业务员查询
- 按日期范围查询

展示字段：
- 销售单号
- 仓库
- 业务员
- 操作员
- 终端
- 顾客信息
- 商品列表
- 商品总数
- 总金额
- 折后价
- 付款方式
- 支付金额
- 应找金额
- 状态
- 日期

说明：
- 本页面默认只展示“已结算”的销售单
- “状态”字段可以不显示为单独列，但数据层仍应限定 `status = 1`

---

# 二、页面定位

## 1. 页面性质

这是一个“销售记录查询页”，不是编辑页，也不是收银页。

因此页面主行为是：
- 查询
- 列表浏览
- 查看详情

次行为可选：
- 导出销售记录
- 打印小票
- 查看完整商品明细弹窗

本阶段优先实现查询和列表展示。

## 2. 菜单归属

建议菜单路径归属：
- 一级：销售管理
- 二级：POS销售

建议前端页面文件名：
- `PosSalesManage.vue`

建议路由 path：
- `/sales/pos`

---

# 三、数据字段设计说明

## 1. 列表主字段说明

| 字段 | 来源 | 页面展示建议 |
|---|---|---|
| 销售单号 | biz_pos_order.sale_no | 文本展示，可点击查看详情 |
| 仓库 | biz_pos_order.warehouse_id + biz_warehouse.name | 展示仓库名称 |
| 业务员 | biz_pos_order.sales_staff_id + biz_sales_staff.name | 展示业务员姓名 |
| 操作员 | biz_pos_order.operator_id + sys_user.real_name/username | 展示操作员姓名 |
| 终端 | biz_pos_order.terminal_id + biz_terminal.name | 展示终端名称 |
| 顾客信息 | biz_pos_order.customer_id + biz_customer.name | 展示客户名称，若为空显示“散客” |
| 商品列表 | biz_pos_order_item | 展示概述文本，如“可乐×2、雪碧×1，共3种” |
| 商品总数 | biz_pos_order.goods_count | 数字展示 |
| 总金额 | biz_pos_order.total_amount | 金额展示，保留2位小数 |
| 折后价 | biz_pos_order.payable_amount | 金额展示，保留2位小数 |
| 付款方式 | biz_pos_order.payment_method | 文本展示 |
| 支付金额 | biz_pos_order.paid_amount | 金额展示 |
| 应找金额 | biz_pos_order.change_amount | 金额展示 |
| 日期 | biz_pos_order.created_at / updated_at | 默认展示创建时间 |

## 2. 商品列表概述规则

由于列表页宽度有限，不适合直接展开完整明细，建议商品列表列采用“概述展示”：

规则建议：
- 取前 2~3 个商品名称拼接展示
- 格式示例：`可口可乐×2，雪碧×1，矿泉水×3`
- 若商品过多，可截断为：`可口可乐×2，雪碧×1，矿泉水×3 等4项`
- 鼠标悬停时可通过 tooltip 查看完整商品概述

---

# 四、后端 API 设计

## step 1: 后端 jxcServer 工程，创建【POS销售】相关 API

建议新增一个独立接口模块：
- `server/jxcServer/api/pos_sales.py`

也可以复用现有 `pos.py`，但从职责清晰度考虑，更建议将“收银业务接口”和“销售记录查询接口”拆开。

## 1. 列表查询接口

建议接口：
- `GET /api/pos-sales/list`

### 查询参数

| 参数 | 类型 | 说明 |
|---|---|---|
| sale_no | string | 销售单号模糊查询 |
| customer_name | string | 客户名称模糊查询 |
| warehouse_id | number | 仓库筛选 |
| sales_staff_id | number | 业务员筛选 |
| start_date | string | 开始日期，格式 YYYY-MM-DD |
| end_date | string | 结束日期，格式 YYYY-MM-DD |
| page | number | 页码，默认 1 |
| page_size | number | 每页条数，默认 10 |

### 查询规则

- 默认只查 `status = 1` 的已结算记录
- `sale_no` 使用模糊匹配
- `customer_name` 使用模糊匹配
- 日期范围按 `created_at` 查询
- 若 `start_date` 和 `end_date` 同时存在，则查询区间内数据
- 返回分页数据

### 返回字段建议

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "sale_no": "P-260427171234567",
        "warehouse_id": 1,
        "warehouse_name": "北京总仓",
        "sales_staff_id": 1,
        "sales_staff_name": "店长",
        "operator_id": 1,
        "operator_name": "管理员",
        "terminal_id": 1,
        "terminal_name": "门店终端001",
        "customer_id": 5,
        "customer_name": "广州南方贸易公司",
        "goods_summary": "可口可乐×2，雪碧×1",
        "goods_count": 3,
        "total_amount": 28.00,
        "payable_amount": 25.20,
        "payment_method": "现金",
        "paid_amount": 30.00,
        "change_amount": 4.80,
        "created_at": "2026-04-27 17:12:34"
      }
    ],
    "total": 128
  }
}
```

## 2. 销售详情接口

建议接口：
- `GET /api/pos-sales/detail?id=1`

### 用途

用于点击销售单号后，查看该单完整商品明细。

### 返回内容建议

- 主单基础信息
- 顾客信息
- 商品明细列表

### 明细字段建议

- 商品名称
- 单位
- 数量
- 原价
- 折扣率
- 折后单价
- 折后小计
- 仓库

## 3. 查询条件初始化接口

建议接口：
- `GET /api/pos-sales/options`

### 用途

返回下拉筛选所需基础数据：
- 仓库列表
- 销售业务员列表

若前端已有通用接口，也可以直接复用：
- `/api/warehouse/list`
- `/api/sales-staff/list`

因此这个接口不是必需，可按项目风格决定。

---

# 五、后端查询 SQL 设计建议

## 1. 主列表查询建议

建议以 `biz_pos_order` 为主表，左连接：
- `biz_warehouse`
- `biz_sales_staff`
- `sys_user`
- `biz_terminal`
- `biz_customer`

商品概述 `goods_summary` 可通过两种方式生成：

### 方案 A：SQL 聚合生成

使用 `string_agg` 聚合明细商品名称和数量。

优点：
- 后端一次查询直接返回概述文本

缺点：
- SQL 稍复杂

### 方案 B：后端 Python 二次组装

先查主表分页，再批量查明细并在 Python 中拼接 `goods_summary`。

优点：
- 逻辑清晰
- 便于控制截断和 tooltip 展示内容

建议优先采用方案 B。

## 2. 排序建议

- 默认按 `id DESC` 或 `created_at DESC` 倒序展示
- 最新销售单排在最前面

---

# 六、前端页面设计

## step 2: 前端 jxcClient 实现 "POS销售" 菜单页面

建议新增页面文件：
- `client/jxcClient/src/views/PosSalesManage.vue`

页面风格参考 [client/jxcClient/src/views/AreaManage.vue](client/jxcClient/src/views/AreaManage.vue)，但本页不是纯 CRUD，而是“查询 + 表格 + 详情”的结构。

## 1. 页面结构

### 上部分：查询栏

采用两行或单行自适应工具栏，建议包含：

- 输入框：按销售单号查询
- 输入框：按客户名称查询
- 下拉框：按仓库过滤
- 下拉框：按业务员过滤
- 日期范围选择器：按日期范围查询
- 查询按钮
- 重置按钮

建议布局：

```text
[销售单号输入框] [客户名称输入框] [仓库下拉] [业务员下拉] [日期范围] [查询] [重置]
```

### 下部分：销售单列表

使用 `a-table` 展示列表。

## 2. 查询栏交互建议

### 销售单号输入框

- placeholder：`请输入销售单号`
- 支持回车查询

### 客户名称输入框

- placeholder：`请输入客户名称`
- 支持回车查询

### 仓库下拉框

- 默认值为空，表示全部仓库
- 文案：`全部仓库`

### 业务员下拉框

- 默认值为空，表示全部业务员
- 文案：`全部业务员`

### 日期范围选择器

- 使用 `a-range-picker`
- 支持清空
- 日期格式建议：`YYYY-MM-DD`

### 查询按钮

- 点击后重新拉取第一页数据

### 重置按钮

- 清空全部查询条件
- 恢复默认列表

## 3. 表格列设计

建议表格列如下：

| 列名 | key | 宽度建议 | 说明 |
|---|---|---|---|
| 销售单号 | sale_no | 180 | 可点击打开详情 |
| 仓库 | warehouse_name | 100 | 文本 |
| 业务员 | sales_staff_name | 100 | 文本 |
| 操作员 | operator_name | 100 | 文本 |
| 终端 | terminal_name | 120 | 文本 |
| 顾客信息 | customer_name | 160 | 无客户显示散客 |
| 商品列表 | goods_summary | 240 | 概述文本 + tooltip |
| 商品总数 | goods_count | 80 | 数字 |
| 总金额 | total_amount | 100 | 金额 |
| 折后价 | payable_amount | 100 | 金额，建议高亮 |
| 付款方式 | payment_method | 100 | 文本 |
| 支付金额 | paid_amount | 100 | 金额 |
| 应找金额 | change_amount | 100 | 金额 |
| 日期 | created_at | 180 | 日期时间 |
| 操作 | action | 80 | 查看详情 |

说明：
- “状态”字段本需求中说明为无状态列，因此列表不单独展示状态列
- 实际查询仅返回 `status = 1` 数据即可

## 4. 表格操作建议

### 查看详情

操作列建议提供：
- `查看详情`

点击后打开详情弹窗，展示：
- 销售单号
- 仓库
- 业务员
- 操作员
- 终端
- 顾客
- 商品明细表
- 总金额
- 折后价
- 付款方式
- 支付金额
- 应找金额
- 时间

### 不建议提供的操作

本阶段不建议提供：
- 删除销售单
- 编辑销售单
- 作废销售单

原因：
- 销售记录属于结果数据，直接改删会影响库存和财务一致性

---

# 七、前端状态设计建议

建议页面状态包含：

## 1. 查询条件对象

```js
const filters = reactive({
  saleNo: '',
  customerName: '',
  warehouseId: undefined,
  salesStaffId: undefined,
  dateRange: [],
  page: 1,
  pageSize: 10,
})
```

## 2. 列表数据状态

```js
const list = ref([])
const total = ref(0)
const loading = ref(false)
```

## 3. 下拉选项状态

```js
const warehouseOptions = ref([])
const salesStaffOptions = ref([])
```

## 4. 详情弹窗状态

```js
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
```

---

# 八、接口调用建议

建议新增前端 API 文件：
- `client/jxcClient/src/api/posSales.js`

建议包含以下方法：

```js
export const getPosSalesList = (params) => request.get('/api/pos-sales/list', { params })
export const getPosSalesDetail = (id) => request.get('/api/pos-sales/detail', { params: { id } })
```

仓库与业务员可直接复用：
- `getWarehouseList()`
- `getSalesStaffList()`

---

# 九、页面交互细节建议

## 1. 默认加载

页面进入时：
- 自动查询第一页销售记录
- 自动加载仓库和业务员筛选数据

## 2. 空数据提示

若暂无数据：
- 显示 Ant Design 默认空态
- 文案建议：`暂无POS销售记录`

## 3. 金额格式

金额统一：
- 保留两位小数
- 右对齐显示

## 4. 顾客信息显示

若 `customer_id` 为空：
- 展示为 `散客`

## 5. 商品列表显示

建议：
- 列表中显示摘要
- 鼠标悬停显示完整商品内容
- 点击详情弹窗查看完整商品行明细

## 6. 分页交互

建议：
- 支持分页器
- 切换页码保留当前筛选条件
- 修改 pageSize 时回到第一页

---

# 十、详情弹窗设计建议

建议增加“销售详情”弹窗。

## 1. 头部信息

展示：
- 销售单号
- 仓库
- 业务员
- 操作员
- 终端
- 顾客
- 日期

## 2. 明细表

展示列：
- 商品名称
- 单位
- 数量
- 原价
- 折扣率
- 折后单价
- 折后小计
- 仓库

## 3. 底部汇总

展示：
- 商品总数
- 总金额
- 折后价
- 付款方式
- 支付金额
- 应找金额
- 备注

---

# 十一、实现步骤建议

## step 1: 后端 `jxcServer` 工程，创建【POS销售】相关 API

建议顺序：
1. 新建 `pos_sales.py`
2. 实现列表查询接口 `/api/pos-sales/list`
3. 实现详情接口 `/api/pos-sales/detail`
4. 在 `app.py` 注册蓝图
5. 用真实数据库验证筛选条件和分页逻辑

## step 2: 前端 `jxcClient` 实现 "POS销售" 菜单页面

建议顺序：
1. 新建 `api/posSales.js`
2. 新建 `views/PosSalesManage.vue`
3. 按 `AreaManage.vue` 风格实现查询栏和表格
4. 接入仓库、业务员下拉数据
5. 接入分页查询
6. 增加详情弹窗
7. 注册菜单 path 与组件映射

---

# 十二、验收标准

## 后端验收

- 支持按销售单号查询
- 支持按客户名称查询
- 支持按仓库过滤
- 支持按业务员过滤
- 支持按日期范围过滤
- 仅返回已结算销售单
- 支持分页
- 支持查看销售详情

## 前端验收

- 页面风格与 [client/jxcClient/src/views/AreaManage.vue](client/jxcClient/src/views/AreaManage.vue) 一致
- 查询栏完整可用
- 点击查询后表格数据正确刷新
- 支持分页
- 金额显示格式统一
- 商品列表支持摘要展示
- 支持查看销售详情弹窗

---

# 十三、修正说明

原始文档中有两处命名混淆，后续 coding 时建议修正：

## 1. 标题错误

原文标题为：`采购业务员`

实际应为：`POS销售`

## 2. step 文案错误

原文中写的是：
- 创建【采购业务员】相关 API
- 实现 "采购业务员" 菜单页面

实际应修正为：
- 创建【POS销售】相关 API
- 实现 "POS销售" 菜单页面

后续 AI coding 应以“POS销售查询页”为准，不应误实现为“采购业务员”页面。

---

# 提示词

先不进行Coding，依据 `tools/012-POS销售界面.md` 内容，仅将内容补全和完善，写入到文件 `tools/012-POS销售界面-AI.md`。
按照 `tools/012-POS销售界面-AI.md` 步骤，进行AI coding。