<template>
  <div class="page-container goods-page">
    <div class="toolbar">
      <div class="toolbar-actions">
        <a-input
          v-model:value="keyword"
          allow-clear
          placeholder="请输入商品名称或编码"
          style="width: 260px"
          @change="onKeywordChange"
          @pressEnter="onSearch"
        />
        <a-button @click="onSearch">查询</a-button>
        <a-button type="primary" @click="openAddGoods">
          <PlusOutlined />新建商品
        </a-button>
      </div>
    </div>

    <div class="main-layout">
      <div class="category-sidebar">
        <div class="sidebar-title">商品分类</div>
        <div class="sidebar-body">
          <a-spin :spinning="categoryLoading">
            <a-tree
              :tree-data="categoryTreeNodes"
              :selected-keys="[selectedCategoryId]"
              :default-expand-all="true"
              block-node
              @select="onCategorySelect"
            />
          </a-spin>
        </div>
      </div>

      <div class="table-area">
        <div class="table-wrapper">
          <a-table
            :columns="columns"
            :data-source="goodsList"
            :loading="loading"
            :pagination="false"
            :scroll="{ x: 1420 }"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'seq'">
                {{ (page - 1) * pageSize + index + 1 }}
              </template>

              <template v-else-if="priceColumnKeys.includes(column.key)">
                {{ formatMoney(record[column.dataIndex]) }}
              </template>

              <template v-else-if="column.key === 'category_name'">
                {{ record.category_name || '-' }}
              </template>

              <template v-else-if="column.key === 'shelf_life'">
                {{ record.shelf_life || 0 }}
              </template>

              <template v-else-if="column.key === 'stock_total'">
                <span :class="{ 'stock-danger': Number(record.stock_total) <= Number(record.stock_min) }">
                  {{ record.stock_total }}
                </span>
              </template>

              <template v-else-if="column.key === 'enable_points' || column.key === 'enable_discount'">
                {{ Number(record[column.dataIndex]) === 1 ? '是' : '否' }}
              </template>

              <template v-else-if="column.key === 'action'">
                <a-dropdown trigger="click" :destroyPopupOnHide="true">
                  <EllipsisOutlined class="action-btn" />
                  <template #overlay>
                    <a-menu>
                      <a-menu-item key="edit" @click="openEditGoods(record)">
                        <EditOutlined style="margin-right: 6px" />编辑
                      </a-menu-item>
                      <a-menu-item v-if="Number(record.stock_total) === 0" key="delete" @click="confirmDeleteGoods(record)">
                        <DeleteOutlined style="margin-right: 6px" /><span class="danger-text">删除</span>
                      </a-menu-item>
                      <a-menu-item key="stock-list" @click="openStockList(record)">
                        <UnorderedListOutlined style="margin-right: 6px" />库存清单
                      </a-menu-item>
                      <a-menu-item key="stock-add" @click="openAddStock(record)">
                        <PlusCircleOutlined style="margin-right: 6px" />增加库存
                      </a-menu-item>
                      <a-menu-item v-if="Number(record.stock_total) > 0" key="stock-check" @click="openStockCheck(record)">
                        <ToolOutlined style="margin-right: 6px" />库存盘点
                      </a-menu-item>
                      <a-menu-item v-if="Number(record.stock_total) > 0" key="stock-transfer" @click="openTransfer(record)">
                        <SwapOutlined style="margin-right: 6px" />仓库调拨
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </template>
            </template>
          </a-table>
        </div>

        <div class="pagination-bar">
          <a-pagination
            v-model:current="page"
            v-model:page-size="pageSize"
            :total="total"
            show-size-changer
            show-quick-jumper
            :show-total="(count) => `共 ${count} 条`"
            :page-size-options="['10', '20', '50']"
            @change="loadGoods"
            @show-size-change="onPageSizeChange"
          />
        </div>
      </div>
    </div>

    <a-modal
      v-model:open="goodsModalVisible"
      :title="goodsModalTitle"
      :confirm-loading="goodsSubmitting"
      ok-text="确定"
      cancel-text="取消"
      width="720px"
      @ok="handleGoodsSubmit"
      @cancel="resetGoodsForm"
    >
      <a-form ref="goodsFormRef" :model="goodsForm" :rules="goodsRules" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="商品编码" name="code">
              <a-input v-model:value="goodsForm.code" placeholder="请输入商品编码" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="其他编码">
              <a-input v-model:value="goodsForm.other_code" placeholder="请输入其他编码" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="商品名称" name="name">
              <a-input v-model:value="goodsForm.name" placeholder="请输入商品名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="分类">
              <a-tree-select
                v-model:value="goodsForm.category_id"
                :tree-data="categorySelectTree"
                :dropdown-style="{ maxHeight: '320px', overflow: 'auto' }"
                allow-clear
                tree-default-expand-all
                placeholder="请选择分类，留空则不设置"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="采购价">
              <a-input-number v-model:value="goodsForm.purchase_price" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="销售价">
              <a-input-number v-model:value="goodsForm.sale_price" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="会员价">
              <a-input-number v-model:value="goodsForm.member_price" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="批发价">
              <a-input-number v-model:value="goodsForm.wholesale_price" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="单位">
              <a-select v-model:value="goodsForm.unit_id" allow-clear placeholder="请选择单位">
                <a-select-option v-for="item in unitOptions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="生产厂家">
              <a-select v-model:value="goodsForm.manufacturer_id" allow-clear placeholder="请选择厂家">
                <a-select-option v-for="item in manufacturerOptions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="库存下限">
              <a-input-number v-model:value="goodsForm.stock_min" :min="0" :precision="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="保质期（天）">
              <a-input-number v-model:value="goodsForm.shelf_life" :min="0" :precision="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="参与积分">
              <a-switch v-model:checked="goodsPointsChecked" checked-children="是" un-checked-children="否" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="会员折扣">
              <a-switch v-model:checked="goodsDiscountChecked" checked-children="是" un-checked-children="否" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item v-if="goodsModalMode === 'edit'" label="当前库存">
          <a-input :value="String(goodsForm.stock_total || 0)" disabled />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="stockListVisible"
      :title="stockListTitle"
      :footer="null"
      width="960px"
    >
      <a-table
        :columns="stockColumns"
        :data-source="stockList"
        :loading="stockListLoading"
        :pagination="false"
        row-key="id"
        size="small"
      />
    </a-modal>

    <a-modal
      v-model:open="addStockVisible"
      title="增加库存"
      :confirm-loading="addStockSubmitting"
      ok-text="确定"
      cancel-text="取消"
      width="640px"
      @ok="handleAddStock"
      @cancel="resetAddStockForm"
    >
      <a-form ref="addStockFormRef" :model="addStockForm" :rules="addStockRules" layout="vertical">
        <a-form-item label="商品名称">
          <a-input :value="activeGoods?.name || ''" disabled />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="存放仓库" name="warehouse_id">
              <a-select v-model:value="addStockForm.warehouse_id" placeholder="请选择仓库">
                <a-select-option v-for="item in warehouseOptions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="增加数量" name="quantity">
              <a-input-number v-model:value="addStockForm.quantity" :min="1" :precision="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="规格">
              <a-input v-model:value="addStockForm.spec" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="批号">
              <a-input v-model:value="addStockForm.batch_no" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="尺码">
              <a-input v-model:value="addStockForm.size" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="颜色">
              <a-input v-model:value="addStockForm.color" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="生产日期">
          <a-date-picker v-model:value="addStockForm.produce_date" value-format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="stockCheckVisible"
      title="库存盘点"
      :confirm-loading="stockCheckSubmitting"
      ok-text="保存"
      cancel-text="取消"
      width="980px"
      @ok="handleStockCheckSave"
      @cancel="resetStockCheck"
    >
      <a-form layout="vertical">
        <a-form-item label="选择仓库">
          <a-select v-model:value="stockCheckWarehouseId" placeholder="请选择有库存的仓库">
            <a-select-option v-for="item in stockCheckWarehouseOptions" :key="item.id" :value="item.id">
              {{ item.name }}（库存 {{ item.quantity }}）
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>

      <a-table
        :columns="stockCheckColumns"
        :data-source="selectedWarehouseStockRows"
        :pagination="false"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'spec'">
            <a-input v-model:value="record.spec" />
          </template>
          <template v-else-if="column.key === 'batch_no'">
            <a-input v-model:value="record.batch_no" />
          </template>
          <template v-else-if="column.key === 'size'">
            <a-input v-model:value="record.size" />
          </template>
          <template v-else-if="column.key === 'color'">
            <a-input v-model:value="record.color" />
          </template>
          <template v-else-if="column.key === 'produce_date'">
            <a-date-picker v-model:value="record.produce_date" value-format="YYYY-MM-DD" style="width: 100%" />
          </template>
          <template v-else-if="column.key === 'quantity'">
            <a-input-number v-model:value="record.quantity" :min="0" :precision="0" style="width: 100%" />
          </template>
        </template>
      </a-table>
    </a-modal>

    <a-modal
      v-model:open="transferVisible"
      title="仓库调拨"
      :confirm-loading="transferSubmitting"
      ok-text="调拨"
      cancel-text="取消"
      width="640px"
      @ok="handleTransfer"
      @cancel="resetTransferForm"
    >
      <a-form ref="transferFormRef" :model="transferForm" :rules="transferRules" layout="vertical">
        <a-form-item label="商品名称">
          <a-input :value="activeGoods?.name || ''" disabled />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="源仓库" name="from_warehouse_id">
              <a-select v-model:value="transferForm.from_warehouse_id" placeholder="请选择源仓库">
                <a-select-option v-for="item in stockCheckWarehouseOptions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="目标仓库" name="to_warehouse_id">
              <a-select v-model:value="transferForm.to_warehouse_id" placeholder="请选择目标仓库">
                <a-select-option
                  v-for="item in filteredTargetWarehouseOptions"
                  :key="item.id"
                  :value="item.id"
                >
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="源仓库库存">
              <a-input :value="String(selectedSourceWarehouseQuantity)" disabled />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="调拨数量" name="quantity">
              <a-input-number v-model:value="transferForm.quantity" :min="1" :precision="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  DeleteOutlined,
  EditOutlined,
  EllipsisOutlined,
  PlusCircleOutlined,
  PlusOutlined,
  SwapOutlined,
  ToolOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons-vue'
import { getGoodsCategoryTree } from '../api/goodsCategory'
import {
  addGoods,
  addGoodsStock,
  deleteGoods,
  getGoodsList,
  getGoodsStockList,
  transferGoodsStock,
  updateGoods,
  updateGoodsStock,
} from '../api/goods'
import { getUnitList } from '../api/unit'
import { getManufacturerList } from '../api/manufacturer'
import { getWarehouseList } from '../api/warehouse'

const priceColumnKeys = ['purchase_price', 'sale_price', 'member_price', 'wholesale_price']

const loading = ref(false)
const categoryLoading = ref(false)
const goodsList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const selectedCategoryId = ref(0)
const categoryTree = ref([])
const unitOptions = ref([])
const manufacturerOptions = ref([])
const warehouseOptions = ref([])
const activeGoods = ref(null)

const goodsModalVisible = ref(false)
const goodsModalMode = ref('add')
const goodsModalTitle = ref('新建商品')
const goodsSubmitting = ref(false)
const goodsFormRef = ref()
const goodsForm = reactive(createGoodsForm())

const addStockVisible = ref(false)
const addStockSubmitting = ref(false)
const addStockFormRef = ref()
const addStockForm = reactive(createAddStockForm())

const stockListVisible = ref(false)
const stockListLoading = ref(false)
const stockListTitle = ref('库存清单')
const stockList = ref([])

const stockCheckVisible = ref(false)
const stockCheckSubmitting = ref(false)
const stockCheckWarehouseId = ref(undefined)
const stockCheckRows = ref([])

const transferVisible = ref(false)
const transferSubmitting = ref(false)
const transferFormRef = ref()
const transferForm = reactive(createTransferForm())

let keywordTimer = null

const columns = [
  { title: '序号', key: 'seq', width: 30, align: 'center', fixed: 'left' },
  { title: '编码', dataIndex: 'code', key: 'code', width: 60 },
  { title: '名称', dataIndex: 'name', key: 'name', width: 80, ellipsis: true },
  { title: '分类', dataIndex: 'category_name', key: 'category_name', width: 50},
  { title: '采购价', dataIndex: 'purchase_price', key: 'purchase_price', width: 40, align: 'right' },
  { title: '销售价', dataIndex: 'sale_price', key: 'sale_price', width: 40, align: 'right' },
  { title: '会员价', dataIndex: 'member_price', key: 'member_price', width: 40, align: 'right' },
  { title: '批发价', dataIndex: 'wholesale_price', key: 'wholesale_price', width: 40, align: 'right' },
  { title: '当前库存', dataIndex: 'stock_total', key: 'stock_total', width: 40, align: 'right' },
  { title: '单位', dataIndex: 'unit_name', key: 'unit_name', width: 40, align: 'right' },
  { title: '保质期', dataIndex: 'shelf_life', key: 'shelf_life', width: 40, align: 'right' },
  { title: '生产厂家', dataIndex: 'manufacturer_name', key: 'manufacturer_name', width: 80, ellipsis: true },
  { title: '操作', key: 'action', width: 36, align: 'center', fixed: 'right' },
]

const stockColumns = [
  { title: '仓库', dataIndex: 'warehouse_name', key: 'warehouse_name', width: 120 },
  { title: '规格', dataIndex: 'spec', key: 'spec', width: 120 },
  { title: '批号', dataIndex: 'batch_no', key: 'batch_no', width: 120 },
  { title: '尺码', dataIndex: 'size', key: 'size', width: 100 },
  { title: '颜色', dataIndex: 'color', key: 'color', width: 100 },
  { title: '生产日期', dataIndex: 'produce_date', key: 'produce_date', width: 120 },
  { title: '有效日期', dataIndex: 'expire_date', key: 'expire_date', width: 120 },
  { title: '当前库存', dataIndex: 'quantity', key: 'quantity', width: 100, align: 'right' },
]

const stockCheckColumns = [
  { title: '规格', dataIndex: 'spec', key: 'spec' },
  { title: '批号', dataIndex: 'batch_no', key: 'batch_no' },
  { title: '尺码', dataIndex: 'size', key: 'size' },
  { title: '颜色', dataIndex: 'color', key: 'color' },
  { title: '生产日期', dataIndex: 'produce_date', key: 'produce_date', width: 160 },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 120 },
]

const goodsRules = {
  code: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
}

const addStockRules = {
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入增加数量', trigger: 'change' }],
}

const transferRules = {
  from_warehouse_id: [{ required: true, message: '请选择源仓库', trigger: 'change' }],
  to_warehouse_id: [{ required: true, message: '请选择目标仓库', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入调拨数量', trigger: 'change' }],
}

const goodsPointsChecked = computed({
  get: () => Number(goodsForm.enable_points) === 1,
  set: (value) => {
    goodsForm.enable_points = value ? 1 : 0
  },
})

const goodsDiscountChecked = computed({
  get: () => Number(goodsForm.enable_discount) === 1,
  set: (value) => {
    goodsForm.enable_discount = value ? 1 : 0
  },
})

const categoryTreeNodes = computed(() => [{
  title: '所有商品',
  key: 0,
  children: convertCategoryTree(categoryTree.value),
}])

const categorySelectTree = computed(() => [
  ...convertCategorySelectTree(categoryTree.value),
])

const unclassifiedCategoryId = computed(() => {
  const found = categoryTree.value.find((n) => n.is_system === 1)
  return found ? found.id : null
})

const stockCheckWarehouseOptions = computed(() => {
  const map = new Map()
  stockCheckRows.value.forEach((row) => {
    if (Number(row.quantity) <= 0) {
      return
    }
    const current = map.get(row.warehouse_id) || { id: row.warehouse_id, name: row.warehouse_name, quantity: 0 }
    current.quantity += Number(row.quantity)
    map.set(row.warehouse_id, current)
  })
  return Array.from(map.values())
})

const selectedWarehouseStockRows = computed(() => {
  if (!stockCheckWarehouseId.value) {
    return []
  }
  return stockCheckRows.value.filter((item) => item.warehouse_id === stockCheckWarehouseId.value)
})

const filteredTargetWarehouseOptions = computed(() => {
  return warehouseOptions.value.filter((item) => item.id !== transferForm.from_warehouse_id)
})

const selectedSourceWarehouseQuantity = computed(() => {
  const target = stockCheckWarehouseOptions.value.find((item) => item.id === transferForm.from_warehouse_id)
  return target ? target.quantity : 0
})

onMounted(async () => {
  await Promise.all([loadCategories(), loadAuxiliary()])
  await loadGoods()
})

onBeforeUnmount(() => {
  if (keywordTimer) {
    clearTimeout(keywordTimer)
  }
})

function createGoodsForm() {
  return {
    id: null,
    code: '',
    other_code: '',
    name: '',
    category_id: 0,
    purchase_price: 0,
    sale_price: 0,
    member_price: 0,
    wholesale_price: 0,
    unit_id: undefined,
    manufacturer_id: undefined,
    stock_min: 0,
    shelf_life: 0,
    enable_points: 0,
    enable_discount: 0,
    stock_total: 0,
  }
}

function createAddStockForm() {
  return {
    warehouse_id: undefined,
    spec: '',
    batch_no: '',
    size: '',
    color: '',
    produce_date: undefined,
    quantity: 1,
  }
}

function createTransferForm() {
  return {
    from_warehouse_id: undefined,
    to_warehouse_id: undefined,
    quantity: 1,
  }
}

function assignGoodsForm(payload = {}) {
  Object.assign(goodsForm, createGoodsForm(), payload)
}

function assignAddStockForm(payload = {}) {
  Object.assign(addStockForm, createAddStockForm(), payload)
}

function assignTransferForm(payload = {}) {
  Object.assign(transferForm, createTransferForm(), payload)
}

function convertCategoryTree(nodes = []) {
  return nodes.map((item) => ({
    title: item.name,
    key: item.id,
    children: convertCategoryTree(item.children || []),
  }))
}

function convertCategorySelectTree(nodes = []) {
  return nodes.map((item) => ({
    title: item.name,
    value: item.id,
    key: item.id,
    children: convertCategorySelectTree(item.children || []),
  }))
}

function formatMoney(value) {
  return Number(value || 0).toFixed(2)
}

async function loadCategories() {
  categoryLoading.value = true
  try {
    const res = await getGoodsCategoryTree()
    if (res.code === 200) {
      categoryTree.value = res.data || []
    }
  } catch (err) {
    message.error(err.response?.data?.msg || '加载分类失败')
  } finally {
    categoryLoading.value = false
  }
}

async function loadAuxiliary() {
  try {
    const [unitRes, manufacturerRes, warehouseRes] = await Promise.all([
      getUnitList(),
      getManufacturerList(),
      getWarehouseList(),
    ])
    unitOptions.value = unitRes.data || []
    manufacturerOptions.value = manufacturerRes.data || []
    warehouseOptions.value = warehouseRes.data || []
  } catch (err) {
    message.error(err.response?.data?.msg || '加载基础数据失败')
  }
}

async function loadGoods() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    if (selectedCategoryId.value > 0) {
      params.category_id = selectedCategoryId.value
    }
    const res = await getGoodsList(params)
    if (res.code === 200) {
      goodsList.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (err) {
    message.error(err.response?.data?.msg || '加载商品列表失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadGoods()
}

function onKeywordChange() {
  if (keywordTimer) {
    clearTimeout(keywordTimer)
  }
  keywordTimer = setTimeout(() => {
    page.value = 1
    loadGoods()
  }, 500)
}

function onCategorySelect(keys) {
  selectedCategoryId.value = Number(keys?.[0] ?? 0)
  page.value = 1
  loadGoods()
}

function onPageSizeChange(current, size) {
  page.value = 1
  pageSize.value = size
  loadGoods()
}

function openAddGoods() {
  activeGoods.value = null
  goodsModalMode.value = 'add'
  goodsModalTitle.value = '新建商品'
  assignGoodsForm({ category_id: unclassifiedCategoryId.value })
  goodsModalVisible.value = true
}

function openEditGoods(record) {
  activeGoods.value = record
  goodsModalMode.value = 'edit'
  goodsModalTitle.value = '编辑商品'
  assignGoodsForm({
    ...record,
    unit_id: record.unit_id || undefined,
    manufacturer_id: record.manufacturer_id || undefined,
    category_id: record.category_id || 0,
  })
  goodsModalVisible.value = true
}

function resetGoodsForm() {
  goodsFormRef.value?.clearValidate()
  assignGoodsForm()
  goodsModalVisible.value = false
}

async function handleGoodsSubmit() {
  try {
    await goodsFormRef.value.validate()
  } catch {
    return
  }
  goodsSubmitting.value = true
  try {
    const payload = {
      ...goodsForm,
      category_id: goodsForm.category_id || 0,
      unit_id: goodsForm.unit_id || 0,
      manufacturer_id: goodsForm.manufacturer_id || 0,
    }
    if (goodsModalMode.value === 'edit') {
      await updateGoods(payload)
      message.success('修改成功')
    } else {
      await addGoods(payload)
      message.success('新建成功')
    }
    resetGoodsForm()
    loadGoods()
  } catch (err) {
    message.error(err.response?.data?.msg || '保存商品失败')
  } finally {
    goodsSubmitting.value = false
  }
}

function confirmDeleteGoods(record) {
  Modal.confirm({
    title: '确认删除商品',
    content: `确认删除商品《${record.name}》？删除后不可恢复。`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await deleteGoods({ id: record.id })
        message.success('删除成功')
        if (goodsList.value.length === 1 && page.value > 1) {
          page.value -= 1
        }
        loadGoods()
      } catch (err) {
        message.error(err.response?.data?.msg || '删除失败')
      }
    },
  })
}

async function fetchStockList(goodsId) {
  const res = await getGoodsStockList(goodsId)
  return (res.data || []).map((item) => ({ ...item }))
}

async function openStockList(record) {
  activeGoods.value = record
  stockListTitle.value = `《${record.name}》- 库存清单`
  stockListVisible.value = true
  stockListLoading.value = true
  try {
    stockList.value = await fetchStockList(record.id)
  } catch (err) {
    message.error(err.response?.data?.msg || '加载库存清单失败')
  } finally {
    stockListLoading.value = false
  }
}

function openAddStock(record) {
  activeGoods.value = record
  assignAddStockForm()
  addStockVisible.value = true
}

function resetAddStockForm() {
  addStockFormRef.value?.clearValidate()
  assignAddStockForm()
  addStockVisible.value = false
}

async function handleAddStock() {
  try {
    await addStockFormRef.value.validate()
  } catch {
    return
  }
  addStockSubmitting.value = true
  try {
    await addGoodsStock({
      ...addStockForm,
      goods_id: activeGoods.value.id,
    })
    message.success('库存增加成功')
    resetAddStockForm()
    loadGoods()
  } catch (err) {
    message.error(err.response?.data?.msg || '增加库存失败')
  } finally {
    addStockSubmitting.value = false
  }
}

async function openStockCheck(record) {
  activeGoods.value = record
  stockCheckVisible.value = true
  stockCheckWarehouseId.value = undefined
  try {
    stockCheckRows.value = await fetchStockList(record.id)
    const firstWarehouse = stockCheckWarehouseOptions.value[0]
    stockCheckWarehouseId.value = firstWarehouse?.id
  } catch (err) {
    message.error(err.response?.data?.msg || '加载库存数据失败')
  }
}

function resetStockCheck() {
  stockCheckVisible.value = false
  stockCheckWarehouseId.value = undefined
  stockCheckRows.value = []
}

async function handleStockCheckSave() {
  if (!stockCheckWarehouseId.value) {
    message.warning('请先选择仓库')
    return
  }
  if (!selectedWarehouseStockRows.value.length) {
    message.warning('当前仓库暂无可盘点记录')
    return
  }
  stockCheckSubmitting.value = true
  try {
    await Promise.all(
      selectedWarehouseStockRows.value.map((row) => updateGoodsStock({
        id: row.id,
        warehouse_id: row.warehouse_id,
        spec: row.spec || '',
        batch_no: row.batch_no || '',
        size: row.size || '',
        color: row.color || '',
        produce_date: row.produce_date || null,
        quantity: Number(row.quantity || 0),
      }))
    )
    message.success('库存盘点已保存')
    resetStockCheck()
    loadGoods()
  } catch (err) {
    message.error(err.response?.data?.msg || '库存盘点失败')
  } finally {
    stockCheckSubmitting.value = false
  }
}

async function openTransfer(record) {
  activeGoods.value = record
  assignTransferForm()
  transferVisible.value = true
  try {
    stockCheckRows.value = await fetchStockList(record.id)
    const firstWarehouse = stockCheckWarehouseOptions.value[0]
    if (firstWarehouse) {
      transferForm.from_warehouse_id = firstWarehouse.id
    }
  } catch (err) {
    message.error(err.response?.data?.msg || '加载调拨数据失败')
  }
}

function resetTransferForm() {
  transferFormRef.value?.clearValidate()
  assignTransferForm()
  transferVisible.value = false
}

async function handleTransfer() {
  try {
    await transferFormRef.value.validate()
  } catch {
    return
  }
  if (transferForm.from_warehouse_id === transferForm.to_warehouse_id) {
    message.warning('源仓库和目标仓库不能相同')
    return
  }
  if (Number(transferForm.quantity || 0) > selectedSourceWarehouseQuantity.value) {
    message.warning('调拨数量不能超过源仓库库存')
    return
  }
  transferSubmitting.value = true
  try {
    await transferGoodsStock({
      goods_id: activeGoods.value.id,
      from_warehouse_id: transferForm.from_warehouse_id,
      to_warehouse_id: transferForm.to_warehouse_id,
      quantity: transferForm.quantity,
    })
    message.success('调拨成功')
    resetTransferForm()
    loadGoods()
  } catch (err) {
    message.error(err.response?.data?.msg || '调拨失败')
  } finally {
    transferSubmitting.value = false
  }
}
</script>

<style scoped>
.goods-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
  border: 1px solid #dbe7ff;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #173b72;
}

.page-subtitle {
  margin-top: 4px;
  color: #5f6f89;
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main-layout {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.category-sidebar,
.table-area {
  min-height: 0;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #edf1f7;
  box-shadow: 0 10px 30px rgba(15, 36, 84, 0.06);
}

.category-sidebar {
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  padding: 16px 18px;
  border-bottom: 1px solid #edf1f7;
  font-weight: 600;
  color: #1f2f46;
}

.sidebar-body {
  flex: 1;
  min-height: 0;
  padding: 12px;
  overflow: auto;
}

.table-area {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  padding: 12px 12px 0;
  overflow: auto;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #edf1f7;
}

.action-btn {
  cursor: pointer;
  font-size: 18px;
  color: #365d9b;
}

.action-btn:hover {
  color: #1677ff;
}

.danger-text,
.stock-danger {
  color: #cf1322;
  font-weight: 600;
}

:deep(.ant-table-cell) {
  white-space: nowrap;
}

:deep(.ant-tree .ant-tree-node-content-wrapper.ant-tree-node-selected) {
  background: #e6f4ff;
}

@media (max-width: 1100px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .main-layout {
    grid-template-columns: 1fr;
  }
}
</style>