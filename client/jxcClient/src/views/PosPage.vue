<template>
  <div class="pos-page">
    <div class="pos-header">
      <a-button type="text" class="back-btn" @click="emit('back')">
        <ArrowLeftOutlined />返回后台
      </a-button>
      <div class="pos-header-center">
        <div class="pos-title">POS 前台销售</div>
        <div class="pos-subtitle">零售收银 / 挂单 / 取单 / 结算</div>
      </div>
      <div class="pos-header-right">
        <div class="header-clock">{{ currentTime }}</div>
        <div class="header-user">{{ displayOperatorName }}</div>
      </div>
    </div>

    <div class="pos-main">
      <div class="pos-top">
        <div class="panel top-left-panel">
          <div class="panel-title">单据信息</div>
          <div class="meta-grid">
            <div class="meta-item wide">
              <span class="meta-label">销售单号</span>
              <span class="meta-value sale-no">{{ saleNo }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">操作员</span>
              <span class="meta-value">{{ displayOperatorName }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">仓库</span>
              <a-button size="small" class="meta-btn" @click="openWarehouseModal">
                <ShopOutlined />{{ selectedWarehouse?.name || '请选择' }}
              </a-button>
            </div>
            <div class="meta-item">
              <span class="meta-label">业务员</span>
              <a-button size="small" class="meta-btn" @click="openSalesStaffModal">
                <TeamOutlined />{{ selectedSalesStaff?.name || '请选择' }}
              </a-button>
            </div>
            <div class="meta-item">
              <span class="meta-label">终端</span>
              <a-button size="small" class="meta-btn" @click="openTerminalModal">
                <CreditCardOutlined />{{ selectedTerminal?.name || '请选择' }}
              </a-button>
            </div>
          </div>
        </div>

        <div class="panel top-right-panel">
          <div class="panel-title-row">
            <div class="panel-title">顾客信息</div>
            <div class="customer-actions">
              <a-button size="small" @click="openCustomerModal">F4 选顾客</a-button>
              <a-button size="small" danger ghost @click="clearCustomer">清空</a-button>
            </div>
          </div>
          <div class="customer-grid">
            <div class="customer-item">
              <span class="meta-label">名称: </span>
              <span class="meta-value">{{ customerDisplay.name }}</span>
            </div>
            <div class="customer-item">
              <span class="meta-label">余额: </span>
              <span class="meta-value">{{ formatMoney(customerDisplay.balance) }}</span>
            </div>
            <div class="customer-item">
              <span class="meta-label">积分: </span>
              <span class="meta-value">{{ customerDisplay.points }}</span>
            </div>
            <div class="customer-item">
              <span class="meta-label">会员号: </span>
              <span class="meta-value">{{ customerDisplay.memberNo }}</span>
            </div>
            <div class="customer-item">
              <span class="meta-label">会员类型: </span>
              <span class="meta-value">{{ customerDisplay.memberType }}</span>
            </div>
            <div class="customer-item">
              <span class="meta-label">折扣率: </span>
              <span class="meta-value highlight">{{ customerDisplay.discountText }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pos-middle">
        <div class="panel cart-panel">
          <div class="panel-title-row">
            <div class="panel-title">商品列表</div>
            <div class="cart-summary-inline">
              <span>总数 {{ summary.goodsCount }}</span>
              <span>总金额 {{ formatMoney(summary.totalAmount) }}</span>
              <span>折后 {{ formatMoney(summary.payableAmount) }}</span>
            </div>
          </div>

          <div class="cart-table-wrap">
            <table class="cart-table">
              <thead>
                <tr>
                  <th class="col-index">序号</th>
                  <th>商品名称</th>
                  <th class="col-qty">数量</th>
                  <th class="col-unit">单位</th>
                  <th class="col-money">原价</th>
                  <th class="col-discount">折扣</th>
                  <th class="col-money">折后价</th>
                  <th class="col-warehouse">仓库</th>
                  <th class="col-flag">积分</th>
                  <th class="col-flag">折扣</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in cart"
                  :key="item.localId"
                  :class="{ active: index === activeCartIndex }"
                  @click="activeCartIndex = index"
                >
                  <td>{{ index + 1 }}</td>
                  <td class="left">{{ item.name }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ item.unit_name || '-' }}</td>
                  <td>{{ formatMoney(item.sale_price) }}</td>
                  <td>{{ formatDiscount(item.discount_rate) }}</td>
                  <td>{{ formatMoney(item.final_price) }}</td>
                  <td>{{ item.warehouse_name || '-' }}</td>
                  <td>{{ item.enable_points ? '是' : '-' }}</td>
                  <td>{{ item.enable_discount ? '是' : '-' }}</td>
                  <td>
                    <a-button size="small" danger type="link" @click.stop="removeCartItem(index)">
                      <DeleteOutlined />
                    </a-button>
                  </td>
                </tr>
                <tr v-if="!cart.length">
                  <td colspan="11" class="empty-row">请先扫码或搜索商品后加入购物车</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="panel shortcut-panel">
          <div class="panel-title">操作快捷键</div>
          <div class="shortcut-list">
            <a-button type="primary" class="shortcut-btn checkout" @click="openCheckoutModal">
              + 结算
            </a-button>
            <a-button class="shortcut-btn" @click="openHoldModal">F8 挂单</a-button>
            <a-button class="shortcut-btn" @click="openTakeHoldModal">F9 取单</a-button>
            <a-button danger class="shortcut-btn" @click="openClearCartModal">F12 全删</a-button>
            <a-button class="shortcut-btn" @click="moveCartSelection(-1)">UP 选择商品</a-button>
            <a-button class="shortcut-btn" @click="moveCartSelection(1)">DOWN 选择商品</a-button>
            <a-button class="shortcut-btn" @click="removeActiveCartItem">Delete 删除</a-button>
            <a-button class="shortcut-btn" @click="openQuantityModal">F1 改数量</a-button>
            <a-button class="shortcut-btn" @click="openCustomerModal">F4 改顾客</a-button>
          </div>
        </div>
      </div>

      <div class="pos-bottom">
        <div class="panel search-panel" :class="{ focused: focusZone === 'input' }">
          <div class="panel-title">商品搜索</div>
          <a-input
            ref="searchInputRef"
            v-model:value="searchKeyword"
            size="large"
            placeholder="扫码 / 商品名称 / 商品编码"
            @focus="focusZone = 'input'"
            @pressEnter="handleSearchSubmit"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
          <div class="search-tips">按 Enter 搜索，搜索结果区上下键选择后回车加入购物车</div>
        </div>

        <div class="panel results-panel" :class="{ focused: focusZone === 'results' }">
          <div class="panel-title-row">
            <div class="panel-title">搜索结果</div>
            <a-button size="small" @click="clearSearchResults">清空结果</a-button>
          </div>
          <div class="results-list">
            <div
              v-for="(item, index) in searchResults"
              :key="`${item.id}-${index}`"
              class="result-row"
              :class="{ active: index === activeResultIndex }"
              @click="selectSearchResult(index)"
              @dblclick="appendActiveSearchResult"
            >
              <div class="result-main">
                <span class="code">{{ item.code }}</span>
                <span class="name">{{ item.name }}</span>
              </div>
              <div class="result-side">
                <span>￥{{ formatMoney(item.sale_price) }}</span>
                <span>库存 {{ item.stock_total }}</span>
              </div>
            </div>
            <div v-if="!searchResults.length" class="result-empty">
              输入关键字后按 Enter 搜索
            </div>
          </div>
        </div>

        <div class="panel summary-panel">
          <div class="panel-title">本单汇总</div>
          <div class="summary-metrics">
            <div class="summary-item">
              <span>总金额</span>
              <strong>{{ formatMoney(summary.totalAmount) }}</strong>
            </div>
            <div class="summary-item">
              <span>总数</span>
              <strong>{{ summary.goodsCount }}</strong>
            </div>
            <div class="summary-item">
              <span>优惠</span>
              <strong>{{ formatMoney(summary.discountAmount) }}</strong>
            </div>
            <div class="summary-item payable">
              <span>折后价</span>
              <strong>{{ formatMoney(summary.payableAmount) }}</strong>
            </div>
          </div>
          <a-button type="primary" size="large" block class="summary-checkout" @click="openCheckoutModal">
            结算
          </a-button>
        </div>
      </div>
    </div>

    <a-modal v-model:open="warehouseModalOpen" title="选择仓库" :footer="null" width="640px">
      <div class="picker-list">
        <div
          v-for="item in warehouses"
          :key="item.id"
          class="picker-row"
          :class="{ active: selectedWarehouse?.id === item.id }"
          @click="chooseWarehouse(item)"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <span class="picker-sub">{{ item.address || '无地址' }}</span>
          </div>
          <span v-if="selectedWarehouse?.id === item.id">当前</span>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:open="salesStaffModalOpen" title="选择业务员" :footer="null" width="560px">
      <div class="picker-list">
        <div
          v-for="item in salesStaffList"
          :key="item.id"
          class="picker-row"
          :class="{ active: selectedSalesStaff?.id === item.id }"
          @click="chooseSalesStaff(item)"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <span class="picker-sub">{{ item.phone || '无电话' }}</span>
          </div>
          <span v-if="item.is_default === 1">默认</span>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:open="terminalModalOpen" title="选择终端" :footer="null" width="560px">
      <div class="picker-list">
        <div
          v-for="item in terminalList"
          :key="item.id"
          class="picker-row"
          :class="{ active: selectedTerminal?.id === item.id }"
          @click="chooseTerminal(item)"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <span class="picker-sub">编码 {{ item.code || '-' }}</span>
          </div>
          <span v-if="item.is_default === 1">默认</span>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:open="customerModalOpen" title="选择顾客" width="860px" :footer="null">
      <div class="modal-toolbar">
        <a-input
          v-model:value="customerKeyword"
          placeholder="顾客名称 / 手机 / 会员号"
          @pressEnter="loadCustomerOptions"
        />
        <a-button type="primary" @click="loadCustomerOptions">搜索</a-button>
        <a-button @click="clearCustomer">设为散客</a-button>
      </div>
      <div class="picker-list customer-picker">
        <div
          v-for="item in customerOptions"
          :key="item.id"
          class="picker-row customer-row"
          :class="{ active: selectedCustomer?.id === item.id }"
          @click="chooseCustomer(item)"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <span class="picker-sub">{{ item.member_no || '-' }} / {{ item.phone || '-' }}</span>
          </div>
          <div class="customer-row-side">
            <span>{{ item.member_type_name || '普通客户' }}</span>
            <span>余额 {{ formatMoney(item.balance) }}</span>
            <span>积分 {{ item.points || 0 }}</span>
          </div>
        </div>
      </div>
    </a-modal>

    <a-modal v-model:open="holdModalOpen" title="挂单确认" @ok="confirmHoldOrder">
      <div class="confirm-box">
        <div>商品总数：{{ summary.goodsCount }}</div>
        <div>总金额：{{ formatMoney(summary.totalAmount) }}</div>
        <div>折后价：{{ formatMoney(summary.payableAmount) }}</div>
      </div>
      <a-textarea v-model:value="holdRemark" :rows="3" placeholder="挂单备注（可选）" />
    </a-modal>

    <a-modal v-model:open="takeHoldModalOpen" title="取单选择" :footer="null" width="720px">
      <div class="picker-list">
        <div
          v-for="item in holdOrders"
          :key="item.id"
          class="picker-row"
          @click="confirmTakeHold(item)"
        >
          <div>
            <strong>{{ item.hold_no }}</strong>
            <span class="picker-sub">{{ item.customer_name || '散客' }} / {{ item.created_at }}</span>
          </div>
          <div class="customer-row-side">
            <span>{{ item.goods_count }} 件</span>
            <span>￥{{ formatMoney(item.payable_amount) }}</span>
          </div>
        </div>
        <div v-if="!holdOrders.length" class="result-empty">暂无挂单</div>
      </div>
    </a-modal>

    <a-modal v-model:open="quantityModalOpen" title="修改数量" @ok="confirmQuantityChange">
      <div class="confirm-box">
        <div>{{ activeCartItem?.name || '-' }}</div>
      </div>
      <a-input-number v-model:value="quantityDraft" :min="1" :precision="0" style="width:100%" />
    </a-modal>

    <a-modal v-model:open="clearCartModalOpen" title="确认清空" @ok="confirmClearCart">
      是否清空当前购物车全部商品？
    </a-modal>

    <a-modal v-model:open="checkoutModalOpen" title="结算" @ok="confirmCheckout">
      <div class="checkout-grid">
        <div class="checkout-item">
          <span>总金额</span>
          <strong>{{ formatMoney(summary.totalAmount) }}</strong>
        </div>
        <div class="checkout-item payable">
          <span>折后金额</span>
          <strong>{{ formatMoney(summary.payableAmount) }}</strong>
        </div>
      </div>
      <a-form layout="vertical">
        <a-form-item label="付款方式">
          <a-select v-model:value="checkoutForm.paymentMethod" :options="paymentOptions" />
        </a-form-item>
        <a-form-item label="支付金额">
          <a-input-number v-model:value="checkoutForm.paidAmount" :min="0" :precision="2" style="width:100%" />
        </a-form-item>
        <a-form-item label="应找金额">
          <a-input :value="formatMoney(checkoutChangeAmount)" readonly />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="checkoutForm.remark" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import {
  ArrowLeftOutlined,
  CreditCardOutlined,
  DeleteOutlined,
  SearchOutlined,
  ShopOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'

import { getCustomerList } from '../api/customer'
import { getMemberTypeList } from '../api/memberType'
import {
  checkoutPosOrder,
  getPosBootstrap,
  getPosHoldList,
  savePosHold,
  searchPosGoods,
  takePosHold,
} from '../api/pos'
import { getSalesStaffList } from '../api/salesStaff'
import { getTerminalList } from '../api/terminal'
import { getWarehouseList } from '../api/warehouse'

const emit = defineEmits(['back'])

const searchInputRef = ref(null)
const clockTimer = ref(null)

const userInfo = reactive(JSON.parse(localStorage.getItem('userInfo') || '{}'))

const saleNo = ref('')
const currentTime = ref('')
const focusZone = ref('input')

const warehouses = ref([])
const salesStaffList = ref([])
const terminalList = ref([])
const memberTypes = ref([])
const customerOptions = ref([])
const holdOrders = ref([])
const searchResults = ref([])
const cart = ref([])

const selectedWarehouse = ref(null)
const selectedSalesStaff = ref(null)
const selectedTerminal = ref(null)
const selectedCustomer = ref(null)

const activeCartIndex = ref(-1)
const activeResultIndex = ref(-1)

const searchKeyword = ref('')
const customerKeyword = ref('')
const holdRemark = ref('')
const quantityDraft = ref(1)

const warehouseModalOpen = ref(false)
const salesStaffModalOpen = ref(false)
const terminalModalOpen = ref(false)
const customerModalOpen = ref(false)
const holdModalOpen = ref(false)
const takeHoldModalOpen = ref(false)
const quantityModalOpen = ref(false)
const clearCartModalOpen = ref(false)
const checkoutModalOpen = ref(false)

const checkoutForm = reactive({
  paymentMethod: '现金',
  paidAmount: 0,
  remark: '',
})

const paymentOptions = [
  { label: '现金', value: '现金' },
  { label: '微信', value: '微信' },
  { label: '支付宝', value: '支付宝' },
  { label: '银行卡', value: '银行卡' },
  { label: '余额', value: '余额' },
]

const displayOperatorName = computed(() => userInfo.real_name || userInfo.username || '当前用户')

const memberTypeMap = computed(() => {
  const map = {}
  for (const item of memberTypes.value) {
    map[item.id] = item
  }
  return map
})

const selectedCustomerDiscountRate = computed(() => {
  if (!selectedCustomer.value?.member_type_id) {
    return 1
  }
  return Number(memberTypeMap.value[selectedCustomer.value.member_type_id]?.discount || 1)
})

const customerDisplay = computed(() => {
  const customer = selectedCustomer.value
  if (!customer) {
    return {
      name: '散客',
      balance: 0,
      points: 0,
      memberNo: '-',
      memberType: '-',
      discountText: '-',
    }
  }
  const discount = selectedCustomerDiscountRate.value
  return {
    name: customer.name || '散客',
    balance: Number(customer.balance || 0),
    points: customer.points || 0,
    memberNo: customer.member_no || '-',
    memberType: customer.member_type_name || '-',
    discountText: discount >= 1 ? '无折扣' : `${(discount * 100).toFixed(0)}%`,
  }
})

const summary = computed(() => {
  let goodsCount = 0
  let totalAmount = 0
  let payableAmount = 0
  for (const item of cart.value) {
    goodsCount += Number(item.quantity || 0)
    totalAmount += Number(item.raw_amount || 0)
    payableAmount += Number(item.final_amount || 0)
  }
  return {
    goodsCount,
    totalAmount: roundMoney(totalAmount),
    payableAmount: roundMoney(payableAmount),
    discountAmount: roundMoney(totalAmount - payableAmount),
  }
})

const checkoutChangeAmount = computed(() => roundMoney(Number(checkoutForm.paidAmount || 0) - summary.value.payableAmount))

const activeCartItem = computed(() => cart.value[activeCartIndex.value] || null)

const hasOpenModal = computed(() => (
  warehouseModalOpen.value ||
  salesStaffModalOpen.value ||
  terminalModalOpen.value ||
  customerModalOpen.value ||
  holdModalOpen.value ||
  takeHoldModalOpen.value ||
  quantityModalOpen.value ||
  clearCartModalOpen.value ||
  checkoutModalOpen.value
))

function roundMoney(value) {
  return Math.round(Number(value || 0) * 100) / 100
}

function formatMoney(value) {
  return roundMoney(value).toFixed(2)
}

function formatDiscount(value) {
  const discount = Number(value || 1)
  if (discount >= 0.9999) {
    return '-'
  }
  return `${(discount * 100).toFixed(0)}%`
}

function localSaleNo() {
  const now = new Date()
  return `P-${String(now.getFullYear()).slice(2)}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}${Date.now()}`
}

function refreshClock() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
}

function focusSearchInput() {
  focusZone.value = 'input'
  nextTick(() => {
    searchInputRef.value?.focus?.()
  })
}

function buildCartItem(result) {
  const quantity = 1
  const discountRate = result.enable_discount ? selectedCustomerDiscountRate.value : 1
  const salePrice = Number(result.sale_price || 0)
  const finalPrice = roundMoney(salePrice * discountRate)
  return {
    localId: `${result.id}-${Date.now()}-${Math.random()}`,
    goods_id: result.id,
    code: result.code,
    name: result.name,
    quantity,
    unit_name: result.unit_name || '',
    sale_price: salePrice,
    discount_rate: discountRate,
    final_price: finalPrice,
    raw_amount: roundMoney(salePrice * quantity),
    final_amount: roundMoney(finalPrice * quantity),
    warehouse_id: selectedWarehouse.value?.id,
    warehouse_name: selectedWarehouse.value?.name,
    enable_points: Number(result.enable_points || 0),
    enable_discount: Number(result.enable_discount || 0),
  }
}

function recalculateCartItem(item) {
  const discountRate = Number(item.enable_discount ? selectedCustomerDiscountRate.value : 1)
  item.discount_rate = discountRate
  item.final_price = roundMoney(Number(item.sale_price || 0) * discountRate)
  item.raw_amount = roundMoney(Number(item.sale_price || 0) * Number(item.quantity || 0))
  item.final_amount = roundMoney(item.final_price * Number(item.quantity || 0))
  return item
}

function refreshCartPricing() {
  cart.value = cart.value.map((item) => recalculateCartItem({ ...item }))
}

function resetOrder(nextSale = '') {
  saleNo.value = nextSale || localSaleNo()
  selectedCustomer.value = null
  searchKeyword.value = ''
  searchResults.value = []
  cart.value = []
  activeCartIndex.value = -1
  activeResultIndex.value = -1
  holdRemark.value = ''
  checkoutForm.paymentMethod = '现金'
  checkoutForm.paidAmount = 0
  checkoutForm.remark = ''
  focusSearchInput()
}

async function loadBootstrapAndOptions() {
  const [bootstrapRes, warehouseRes, staffRes, terminalRes, memberTypeRes] = await Promise.all([
    getPosBootstrap(),
    getWarehouseList(),
    getSalesStaffList(),
    getTerminalList(),
    getMemberTypeList(),
  ])

  warehouses.value = warehouseRes.data || []
  salesStaffList.value = staffRes.data || []
  terminalList.value = terminalRes.data || []
  memberTypes.value = memberTypeRes.data || []

  const bootstrap = bootstrapRes.data || {}
  saleNo.value = bootstrap.sale_no || localSaleNo()
  selectedWarehouse.value = warehouses.value.find((item) => item.id === bootstrap.warehouse?.id) || bootstrap.warehouse || warehouses.value[0] || null
  selectedSalesStaff.value = salesStaffList.value.find((item) => item.id === bootstrap.sales_staff?.id) || bootstrap.sales_staff || salesStaffList.value[0] || null
  selectedTerminal.value = terminalList.value.find((item) => item.id === bootstrap.terminal?.id) || bootstrap.terminal || terminalList.value[0] || null

  if (!selectedWarehouse.value && warehouses.value.length) {
    selectedWarehouse.value = warehouses.value[0]
  }
  if (!selectedSalesStaff.value && salesStaffList.value.length) {
    selectedSalesStaff.value = salesStaffList.value[0]
  }
  if (!selectedTerminal.value && terminalList.value.length) {
    selectedTerminal.value = terminalList.value[0]
  }
}

async function handleSearchSubmit() {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    message.warning('请输入商品名称或条码')
    return
  }
  const res = await searchPosGoods({
    keyword,
    warehouse_id: selectedWarehouse.value?.id,
  })
  searchResults.value = res.data || []
  activeResultIndex.value = searchResults.value.length ? 0 : -1
  focusZone.value = searchResults.value.length ? 'results' : 'input'
  if (!searchResults.value.length) {
    message.warning('未找到匹配商品')
    focusSearchInput()
  }
}

function selectSearchResult(index) {
  activeResultIndex.value = index
  focusZone.value = 'results'
}

function clearSearchResults() {
  searchResults.value = []
  activeResultIndex.value = -1
  focusSearchInput()
}

function appendActiveSearchResult() {
  if (activeResultIndex.value < 0 || !searchResults.value[activeResultIndex.value]) {
    return
  }
  const result = searchResults.value[activeResultIndex.value]
  const existingIndex = cart.value.findIndex(
    (item) => item.goods_id === result.id && item.warehouse_id === selectedWarehouse.value?.id
  )
  if (existingIndex >= 0) {
    cart.value[existingIndex].quantity += 1
    cart.value[existingIndex] = recalculateCartItem({ ...cart.value[existingIndex] })
    activeCartIndex.value = existingIndex
  } else {
    cart.value.push(buildCartItem(result))
    activeCartIndex.value = cart.value.length - 1
  }
  searchKeyword.value = ''
  clearSearchResults()
}

function moveSearchSelection(step) {
  if (!searchResults.value.length) {
    return
  }
  const next = activeResultIndex.value < 0 ? 0 : activeResultIndex.value + step
  activeResultIndex.value = Math.max(0, Math.min(searchResults.value.length - 1, next))
  focusZone.value = 'results'
}

function moveCartSelection(step) {
  if (!cart.value.length) {
    return
  }
  const next = activeCartIndex.value < 0 ? 0 : activeCartIndex.value + step
  activeCartIndex.value = Math.max(0, Math.min(cart.value.length - 1, next))
  focusZone.value = 'cart'
}

function removeCartItem(index) {
  if (index < 0 || index >= cart.value.length) {
    return
  }
  cart.value.splice(index, 1)
  if (!cart.value.length) {
    activeCartIndex.value = -1
  } else {
    activeCartIndex.value = Math.min(index, cart.value.length - 1)
  }
}

function removeActiveCartItem() {
  if (activeCartIndex.value < 0) {
    return
  }
  removeCartItem(activeCartIndex.value)
}

function openWarehouseModal() {
  warehouseModalOpen.value = true
}

function chooseWarehouse(item) {
  selectedWarehouse.value = item
  cart.value = cart.value.map((row) => recalculateCartItem({
    ...row,
    warehouse_id: item.id,
    warehouse_name: item.name,
  }))
  warehouseModalOpen.value = false
  focusSearchInput()
}

function openSalesStaffModal() {
  salesStaffModalOpen.value = true
}

function chooseSalesStaff(item) {
  selectedSalesStaff.value = item
  salesStaffModalOpen.value = false
  focusSearchInput()
}

function openTerminalModal() {
  terminalModalOpen.value = true
}

function chooseTerminal(item) {
  selectedTerminal.value = item
  terminalModalOpen.value = false
  focusSearchInput()
}

async function openCustomerModal() {
  customerModalOpen.value = true
  if (!customerOptions.value.length) {
    await loadCustomerOptions()
  }
}

async function loadCustomerOptions() {
  const res = await getCustomerList({
    keyword: customerKeyword.value.trim(),
    page: 1,
    page_size: 30,
  })
  customerOptions.value = res.data?.list || []
}

function chooseCustomer(item) {
  selectedCustomer.value = item
  customerModalOpen.value = false
  refreshCartPricing()
  focusSearchInput()
}

function clearCustomer() {
  selectedCustomer.value = null
  refreshCartPricing()
}

function openHoldModal() {
  if (!cart.value.length) {
    message.warning('当前没有商品可挂单')
    return
  }
  holdModalOpen.value = true
}

async function confirmHoldOrder() {
  const snapshot = {
    sale_no: saleNo.value,
    warehouse: selectedWarehouse.value,
    sales_staff: selectedSalesStaff.value,
    terminal: selectedTerminal.value,
    customer: selectedCustomer.value,
    cart: cart.value,
  }
  const res = await savePosHold({
    sale_no: saleNo.value,
    warehouse_id: selectedWarehouse.value?.id,
    sales_staff_id: selectedSalesStaff.value?.id,
    terminal_id: selectedTerminal.value?.id,
    customer_id: selectedCustomer.value?.id,
    cart: cart.value,
    remark: holdRemark.value,
    snapshot,
  })
  holdModalOpen.value = false
  message.success(res.msg || '挂单成功')
  resetOrder()
}

async function openTakeHoldModal() {
  const res = await getPosHoldList()
  holdOrders.value = res.data || []
  takeHoldModalOpen.value = true
}

async function confirmTakeHold(item) {
  const res = await takePosHold({ id: item.id })
  const payload = res.data || {}
  const snapshot = payload.snapshot || {}
  saleNo.value = snapshot.sale_no || payload.hold_no || localSaleNo()
  cart.value = (snapshot.cart || payload.cart || []).map((row) => recalculateCartItem({
    ...row,
    localId: row.localId || `${row.goods_id}-${Date.now()}-${Math.random()}`,
  }))
  selectedWarehouse.value = snapshot.warehouse || selectedWarehouse.value
  selectedSalesStaff.value = snapshot.sales_staff || selectedSalesStaff.value
  selectedTerminal.value = snapshot.terminal || selectedTerminal.value
  selectedCustomer.value = snapshot.customer || null
  activeCartIndex.value = cart.value.length ? 0 : -1
  takeHoldModalOpen.value = false
  message.success(res.msg || '取单成功')
  focusSearchInput()
}

function openQuantityModal() {
  if (!activeCartItem.value) {
    message.warning('请先选择商品')
    return
  }
  quantityDraft.value = Number(activeCartItem.value.quantity || 1)
  quantityModalOpen.value = true
}

function confirmQuantityChange() {
  if (!activeCartItem.value) {
    quantityModalOpen.value = false
    return
  }
  const target = cart.value[activeCartIndex.value]
  target.quantity = Math.max(1, Number(quantityDraft.value || 1))
  cart.value[activeCartIndex.value] = recalculateCartItem({ ...target })
  quantityModalOpen.value = false
}

function openClearCartModal() {
  if (!cart.value.length) {
    message.warning('当前购物车已为空')
    return
  }
  clearCartModalOpen.value = true
}

function confirmClearCart() {
  cart.value = []
  activeCartIndex.value = -1
  clearCartModalOpen.value = false
}

function openCheckoutModal() {
  if (!cart.value.length) {
    message.warning('请先添加商品')
    return
  }
  checkoutForm.paymentMethod = '现金'
  checkoutForm.paidAmount = summary.value.payableAmount
  checkoutForm.remark = ''
  checkoutModalOpen.value = true
}

async function confirmCheckout() {
  if (Number(checkoutForm.paidAmount || 0) < summary.value.payableAmount) {
    message.error('支付金额不足')
    return
  }
  const res = await checkoutPosOrder({
    sale_no: saleNo.value,
    warehouse_id: selectedWarehouse.value?.id,
    sales_staff_id: selectedSalesStaff.value?.id,
    terminal_id: selectedTerminal.value?.id,
    customer_id: selectedCustomer.value?.id,
    payment_method: checkoutForm.paymentMethod,
    paid_amount: Number(checkoutForm.paidAmount || 0),
    remark: checkoutForm.remark,
    items: cart.value.map((item) => ({
      goods_id: item.goods_id,
      quantity: item.quantity,
      warehouse_id: item.warehouse_id,
    })),
  })
  checkoutModalOpen.value = false
  message.success(`${res.msg || '结算成功'}，找零 ${formatMoney(res.data?.change_amount || 0)}`)
  resetOrder(res.data?.next_sale_no)
}

function handleGlobalKeydown(event) {
  if (event.key === 'Escape' && hasOpenModal.value) {
    warehouseModalOpen.value = false
    salesStaffModalOpen.value = false
    terminalModalOpen.value = false
    customerModalOpen.value = false
    holdModalOpen.value = false
    takeHoldModalOpen.value = false
    quantityModalOpen.value = false
    clearCartModalOpen.value = false
    checkoutModalOpen.value = false
    focusSearchInput()
    return
  }

  if (hasOpenModal.value) {
    return
  }

  if (event.key === 'F1') {
    event.preventDefault()
    openQuantityModal()
    return
  }
  if (event.key === 'F4') {
    event.preventDefault()
    openCustomerModal()
    return
  }
  if (event.key === 'F8') {
    event.preventDefault()
    openHoldModal()
    return
  }
  if (event.key === 'F9') {
    event.preventDefault()
    openTakeHoldModal()
    return
  }
  if (event.key === 'F12') {
    event.preventDefault()
    openClearCartModal()
    return
  }
  if (event.key === 'Delete') {
    event.preventDefault()
    removeActiveCartItem()
    return
  }
  if (event.key === '+' || event.code === 'NumpadAdd') {
    event.preventDefault()
    openCheckoutModal()
    return
  }
  if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (focusZone.value === 'results' && searchResults.value.length) {
      moveSearchSelection(-1)
    } else {
      moveCartSelection(-1)
    }
    return
  }
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    if (focusZone.value === 'results' && searchResults.value.length) {
      moveSearchSelection(1)
    } else {
      moveCartSelection(1)
    }
    return
  }
  if (event.key === 'Enter') {
    if (focusZone.value === 'results' && searchResults.value.length) {
      event.preventDefault()
      appendActiveSearchResult()
    }
  }
}

onMounted(async () => {
  refreshClock()
  window.addEventListener('keydown', handleGlobalKeydown)
  clockTimer.value = window.setInterval(refreshClock, 1000)

  try {
    await loadBootstrapAndOptions()
  } catch (error) {
    message.error(error?.response?.data?.msg || error?.message || 'POS 初始化失败')
  }
  focusSearchInput()
})

onBeforeUnmount(() => {
  if (clockTimer.value) {
    window.clearInterval(clockTimer.value)
  }
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped>
.pos-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at top left, rgba(255, 215, 160, 0.32), transparent 32%),
    linear-gradient(180deg, #f7f1e8 0%, #f3f5f7 100%);
  color: #1f2937;
  overflow: hidden;
  font-size: 12px;
}

.pos-header {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 0 18px;
  background: linear-gradient(135deg, #0f2f4f 0%, #193d63 52%, #0e2238 100%);
  color: #fff;
  box-shadow: 0 10px 24px rgba(17, 24, 39, 0.2);
}

.back-btn {
  color: rgba(255, 255, 255, 0.9) !important;
  padding: 0 10px;
}

.pos-header-center {
  flex: 1;
  text-align: center;
}

.pos-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.pos-subtitle {
  margin-top: 2px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.pos-header-right {
  min-width: 180px;
  text-align: right;
}

.header-clock {
  font-size: 12px;
}

.header-user {
  margin-top: 2px;
  color: rgba(255, 255, 255, 0.75);
}

.pos-main {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  overflow: hidden;
}

.pos-top,
.pos-middle,
.pos-bottom {
  display: grid;
  gap: 10px;
  min-height: 0;
}

.pos-top {
  grid-template-columns: 1fr 1fr;
  height: 118px;
}

.pos-middle {
  grid-template-columns: 8fr 2fr;
  flex: 1;
}

.pos-bottom {
  grid-template-columns: 3fr 5fr 2fr;
  height: 180px;
}

.panel {
  min-height: 0;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
  padding: 12px;
  overflow: hidden;
}

.panel-title,
.panel-title-row {
  font-weight: 700;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.customer-actions,
.modal-toolbar,
.cart-summary-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cart-summary-inline {
  color: #4b5563;
}

.meta-grid,
.customer-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.meta-item,
.customer-item {
  min-width: 0;
  padding: 4px 5px;
  border-radius: 6px;
  background: rgba(248, 250, 252, 0.95);
  display: flex;
  gap: 4px;
}

.meta-item {
  flex-direction: row;
  align-items: center;
  gap: 6px;
}

.customer-item {
  flex-direction: row;
  align-items: center;
  gap: 6px;
}

.meta-item .meta-label,
.customer-item .meta-label {
  flex-shrink: 0;
}

.meta-item .meta-value,
.customer-item .meta-value {
  min-width: 0;
}

.meta-item.wide,
.customer-item.wide {
  grid-column: span 2;
}

.meta-label {
  color: #6b7280;
  font-size: 11px;
}

.meta-value {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
}

.meta-value.highlight,
.sale-no {
  color: #b45309;
}

.meta-btn {
  width: fit-content;
  max-width: 100%;
}

.cart-panel,
.results-panel {
  display: flex;
  flex-direction: column;
}

.cart-table-wrap,
.results-list,
.picker-list {
  min-height: 0;
  overflow: auto;
}

.cart-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.cart-table th,
.cart-table td {
  padding: 8px 6px;
  border-bottom: 1px solid #e5e7eb;
  text-align: center;
}

.cart-table th {
  background: #f8fafc;
  position: sticky;
  top: 0;
  z-index: 1;
}

.cart-table .left {
  text-align: left;
}

.cart-table tbody tr {
  cursor: pointer;
}

.cart-table tbody tr.active {
  background: rgba(255, 237, 213, 0.65);
}

.col-index { width: 52px; }
.col-qty { width: 58px; }
.col-unit { width: 56px; }
.col-money { width: 72px; }
.col-discount { width: 60px; }
.col-warehouse { width: 84px; }
.col-flag { width: 58px; }
.col-action { width: 54px; }

.empty-row,
.result-empty {
  text-align: center;
  color: #9ca3af;
  padding: 24px 12px;
}

.shortcut-panel {
  display: flex;
  flex-direction: column;
}

.shortcut-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-top: 10px;
}

.shortcut-btn {
  height: 36px;
}

.shortcut-btn.checkout,
.summary-checkout {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  border-color: #b45309;
}

.search-panel,
.summary-panel {
  display: flex;
  flex-direction: column;
}

.search-tips {
  margin-top: 10px;
  color: #6b7280;
  line-height: 1.6;
}

.results-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-row,
.picker-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f8fafc;
  cursor: pointer;
}

.result-row.active,
.picker-row.active {
  background: rgba(191, 219, 254, 0.65);
}

.result-main,
.result-side,
.customer-row-side {
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-main {
  min-width: 0;
}

.result-main .code {
  color: #9ca3af;
}

.result-main .name {
  font-weight: 600;
}

.picker-sub {
  display: block;
  color: #6b7280;
  margin-top: 4px;
}

.summary-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 6px;
  margin-bottom: 12px;
}

.summary-item,
.checkout-item {
  padding: 10px 12px;
  border-radius: 12px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.summary-item.payable,
.checkout-item.payable {
  background: linear-gradient(135deg, rgba(254, 215, 170, 0.9), rgba(251, 191, 36, 0.35));
}

.summary-checkout {
  margin-top: auto;
}

.confirm-box,
.checkout-grid {
  display: grid;
  gap: 10px;
  margin-bottom: 12px;
}

.checkout-grid {
  grid-template-columns: 1fr 1fr;
}

.focused {
  outline: 2px solid rgba(37, 99, 235, 0.22);
}

.customer-picker {
  max-height: 420px;
}

@media (max-width: 1280px) {
  .pos-top {
    height: 134px;
  }

  .pos-bottom {
    height: 196px;
  }

  .meta-grid,
  .customer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
