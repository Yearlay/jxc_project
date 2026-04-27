<template>
  <div class="page-container">
    <div class="toolbar">
      <span class="page-title">POS销售</span>
      <a-input
        v-model:value="filters.saleNo"
        placeholder="请输入销售单号"
        style="width: 180px"
        allow-clear
        @pressEnter="onSearch"
      />
      <a-input
        v-model:value="filters.customerName"
        placeholder="请输入客户名称"
        style="width: 180px"
        allow-clear
        @pressEnter="onSearch"
      />
      <a-select
        v-model:value="filters.warehouseId"
        placeholder="全部仓库"
        allow-clear
        style="width: 160px"
      >
        <a-select-option v-for="item in warehouseOptions" :key="item.id" :value="item.id">
          {{ item.name }}
        </a-select-option>
      </a-select>
      <a-select
        v-model:value="filters.salesStaffId"
        placeholder="全部业务员"
        allow-clear
        style="width: 160px"
      >
        <a-select-option v-for="item in salesStaffOptions" :key="item.id" :value="item.id">
          {{ item.name }}
        </a-select-option>
      </a-select>
      <a-range-picker
        v-model:value="filters.dateRange"
        value-format="YYYY-MM-DD"
        style="width: 260px"
      />
      <a-button @click="onSearch">查询</a-button>
      <a-button @click="onReset">重置</a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      row-key="id"
      :pagination="false"
      :scroll="{ x: 1800 }"
      size="small"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'seq'">
          {{ (filters.page - 1) * filters.pageSize + index + 1 }}
        </template>
        <template v-else-if="column.key === 'sale_no'">
          <a @click="openDetail(record)">{{ record.sale_no }}</a>
        </template>
        <template v-else-if="column.key === 'goods_summary'">
          <a-tooltip :title="record.goods_summary || '-'">
            <span class="ellipsis-text">{{ record.goods_summary || '-' }}</span>
          </a-tooltip>
        </template>
        <template v-else-if="column.key === 'customer_name'">
          {{ record.customer_name || '散客' }}
        </template>
        <template v-else-if="column.key === 'total_amount' || column.key === 'payable_amount' || column.key === 'paid_amount' || column.key === 'change_amount'">
          <span :class="['money-text', { 'highlight-money': column.key === 'payable_amount' }]">
            {{ formatMoney(record[column.key]) }}
          </span>
        </template>
        <template v-else-if="column.key === 'action'">
          <a @click="openDetail(record)">查看详情</a>
        </template>
      </template>
    </a-table>

    <div class="pagination-bar">
      <a-pagination
        :current="filters.page"
        :page-size="filters.pageSize"
        :total="total"
        show-size-changer
        show-quick-jumper
        :show-total="(value) => `共 ${value} 条`"
        :page-size-options="['10', '20', '50']"
        @change="handlePageChange"
        @show-size-change="handlePageSizeChange"
      />
    </div>

    <a-modal
      v-model:open="detailVisible"
      title="销售详情"
      width="980px"
      :footer="null"
      :confirm-loading="detailLoading"
    >
      <a-spin :spinning="detailLoading">
        <template v-if="detailData">
          <a-descriptions :column="3" size="small" bordered>
            <a-descriptions-item label="销售单号">{{ detailData.sale_no }}</a-descriptions-item>
            <a-descriptions-item label="仓库">{{ detailData.warehouse_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="业务员">{{ detailData.sales_staff_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="顾客">{{ detailData.customer_name || '散客' }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ detailData.customer_phone || '-' }}</a-descriptions-item>
            <a-descriptions-item label="付款方式">{{ detailData.payment_method || '-' }}</a-descriptions-item>
            <a-descriptions-item label="日期">{{ detailData.created_at || '-' }}</a-descriptions-item>
            <a-descriptions-item label="备注" :span="3">{{ detailData.remark || '-' }}</a-descriptions-item>
          </a-descriptions>

          <a-table
            class="detail-table"
            :columns="detailColumns"
            :data-source="detailData.items || []"
            :pagination="false"
            row-key="id"
            size="small"
            :scroll="{ x: 960 }"
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'seq'">
                {{ index + 1 }}
              </template>
              <template v-else-if="column.key === 'sale_price' || column.key === 'final_price' || column.key === 'final_amount'">
                {{ formatMoney(record[column.key]) }}
              </template>
              <template v-else-if="column.key === 'discount_rate'">
                {{ formatDiscount(record.discount_rate) }}
              </template>
            </template>
          </a-table>

          <div class="summary-bar">
            <span>商品总数：{{ detailData.goods_count || 0 }}</span>
            <span>总金额：{{ formatMoney(detailData.total_amount) }}</span>
            <span>折后价：{{ formatMoney(detailData.payable_amount) }}</span>
            <span>支付金额：{{ formatMoney(detailData.paid_amount) }}</span>
            <span>应找金额：{{ formatMoney(detailData.change_amount) }}</span>
          </div>
        </template>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { getPosSalesDetail, getPosSalesList } from '../api/posSales'
import { getWarehouseList } from '../api/warehouse'
import { getSalesStaffList } from '../api/salesStaff'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const warehouseOptions = ref([])
const salesStaffOptions = ref([])

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)

const filters = reactive({
  saleNo: '',
  customerName: '',
  warehouseId: undefined,
  salesStaffId: undefined,
  dateRange: [],
  page: 1,
  pageSize: 10,
})

const columns = [
  { title: '序号', key: 'seq', width: 30, align: 'center', fixed: 'left' },
  { title: '销售单号', dataIndex: 'sale_no', key: 'sale_no', width: 80, fixed: 'left' },
  { title: '仓库', dataIndex: 'warehouse_name', key: 'warehouse_name', width: 35 },
  { title: '业务员', dataIndex: 'sales_staff_name', key: 'sales_staff_name', width: 35 },
  { title: '顾客信息', dataIndex: 'customer_name', key: 'customer_name', width: 50},
  { title: '商品列表', dataIndex: 'goods_summary', key: 'goods_summary', width: 120, ellipsis: true },
  { title: '商品总数', dataIndex: 'goods_count', key: 'goods_count', width: 35, align: 'right' },
  { title: '总金额', dataIndex: 'total_amount', key: 'total_amount', width: 35, align: 'right' },
  { title: '折后价', dataIndex: 'payable_amount', key: 'payable_amount', width: 35, align: 'right' },
  { title: '付款方式', dataIndex: 'payment_method', key: 'payment_method', width: 35 },
  { title: '支付金额', dataIndex: 'paid_amount', key: 'paid_amount', width: 35, align: 'right' },
  { title: '应找金额', dataIndex: 'change_amount', key: 'change_amount', width: 35, align: 'right' },
  { title: '日期', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 40, align: 'center', fixed: 'right' },
]

const detailColumns = [
  { title: '序号', key: 'seq', width: 60, align: 'center' },
  { title: '商品名称', dataIndex: 'goods_name_snapshot', key: 'goods_name_snapshot', width: 180 },
  { title: '单位', dataIndex: 'unit_name_snapshot', key: 'unit_name_snapshot', width: 80 },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80, align: 'right' },
  { title: '原价', dataIndex: 'sale_price', key: 'sale_price', width: 100, align: 'right' },
  { title: '折扣率', dataIndex: 'discount_rate', key: 'discount_rate', width: 100, align: 'right' },
  { title: '折后单价', dataIndex: 'final_price', key: 'final_price', width: 110, align: 'right' },
  { title: '折后小计', dataIndex: 'final_amount', key: 'final_amount', width: 110, align: 'right' },
  { title: '仓库', dataIndex: 'warehouse_name', key: 'warehouse_name', width: 120 },
]

function formatMoney(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

function formatDiscount(value) {
  return `${(Number(value || 0) * 100).toFixed(2)}%`
}

async function loadOptions() {
  try {
    const [warehouseRes, salesStaffRes] = await Promise.all([
      getWarehouseList(),
      getSalesStaffList(),
    ])
    warehouseOptions.value = warehouseRes.data || []
    salesStaffOptions.value = salesStaffRes.data || []
  } catch (err) {
    message.error(err.response?.data?.msg || '加载筛选项失败')
  }
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      sale_no: filters.saleNo || undefined,
      customer_name: filters.customerName || undefined,
      warehouse_id: filters.warehouseId || undefined,
      sales_staff_id: filters.salesStaffId || undefined,
      start_date: filters.dateRange?.[0] || undefined,
      end_date: filters.dateRange?.[1] || undefined,
      page: filters.page,
      page_size: filters.pageSize,
    }
    const res = await getPosSalesList(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (err) {
    message.error(err.response?.data?.msg || '加载POS销售记录失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  filters.page = 1
  loadList()
}

function onReset() {
  filters.saleNo = ''
  filters.customerName = ''
  filters.warehouseId = undefined
  filters.salesStaffId = undefined
  filters.dateRange = []
  filters.page = 1
  filters.pageSize = 10
  loadList()
}

function handlePageChange(page, pageSize) {
  filters.page = page
  filters.pageSize = pageSize
  loadList()
}

function handlePageSizeChange(page, pageSize) {
  filters.page = page
  filters.pageSize = pageSize
  loadList()
}

async function openDetail(record) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    const res = await getPosSalesDetail(record.id)
    detailData.value = res.data || null
  } catch (err) {
    detailVisible.value = false
    message.error(err.response?.data?.msg || '加载销售详情失败')
  } finally {
    detailLoading.value = false
  }
}

onMounted(async () => {
  await loadOptions()
  await loadList()
})
</script>

<style scoped>
.page-container {
  padding: 6px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin-right: 8px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.ellipsis-text {
  display: inline-block;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.money-text {
  font-variant-numeric: tabular-nums;
}

.highlight-money {
  color: #cf1322;
  font-weight: 600;
}

.detail-table {
  margin-top: 16px;
}

.summary-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  flex-wrap: wrap;
  font-weight: 500;
}
</style>