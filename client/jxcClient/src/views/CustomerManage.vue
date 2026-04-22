<template>
  <div class="page-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <span class="page-title">客户信息</span>
      <a-input
        v-model:value="keyword"
        placeholder="请输入客户名称/联系人/电话"
        style="width: 260px"
        allow-clear
        @pressEnter="onSearch"
        @change="onKeywordChange"
      />
      <a-button @click="onSearch">查询</a-button>
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />创建新客户
      </a-button>
    </div>

    <!-- 主体：左右布局 -->
    <div class="main-layout">
      <!-- 左侧片区菜单 -->
      <div class="area-sidebar">
        <div class="sidebar-title">片区管理</div>
        <a-menu
          mode="inline"
          :selected-keys="[String(selectedAreaId)]"
          @click="onAreaClick"
        >
          <a-menu-item key="0">
            <span class="area-toggle" @click.stop="areaExpanded = !areaExpanded">
              <DownOutlined v-if="areaExpanded" class="toggle-icon" />
              <RightOutlined v-else class="toggle-icon" />
            </span>
            所有区域
          </a-menu-item>
          <template v-if="areaExpanded">
            <a-menu-item
              v-for="area in areaList"
              :key="String(area.id)"
              class="area-child-item"
            >
              {{ area.name }}
            </a-menu-item>
          </template>
        </a-menu>
      </div>

      <!-- 右侧客户列表 -->
      <div class="table-area">
        <a-table
          :columns="columns"
          :data-source="list"
          :loading="loading"
          row-key="id"
          :pagination="false"
          size="small"
        >
          <template #bodyCell="{ column, record, index }">
            <!-- 序号 -->
            <template v-if="column.key === 'seq'">
              {{ (page - 1) * pageSize + index + 1 }}
            </template>

            <!-- 会员类型标签 -->
            <template v-else-if="column.key === 'member_type_name'">
              <a-tag :color="memberTypeColor(record.member_type_name)">
                {{ record.member_type_name || '-' }}
              </a-tag>
            </template>

            <!-- 余额 -->
            <template v-else-if="column.key === 'balance'">
              ¥{{ (record.balance ?? 0).toFixed(2) }}
            </template>

            <!-- 操作 -->
            <template v-else-if="column.key === 'action'">
              <a-dropdown trigger="click" :destroyPopupOnHide="true">
                <EllipsisOutlined class="action-btn" />
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="edit" @click="openEdit(record)">
                      <EditOutlined style="margin-right:6px" />修改
                    </a-menu-item>
                    <a-menu-item key="recharge" @click="openRecharge(record)">
                      <WalletOutlined style="margin-right:6px" />充值
                    </a-menu-item>
                    <a-menu-item key="delete" @click="confirmDelete(record)">
                      <DeleteOutlined style="margin-right:6px" /><span class="danger-text">删除</span>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </template>
          </template>
        </a-table>

        <!-- 分页 -->
        <div class="pagination-bar">
          <a-pagination
            v-model:current="page"
            v-model:page-size="pageSize"
            :total="total"
            show-size-changer
            show-quick-jumper
            :show-total="(t) => `共 ${t} 条`"
            :page-size-options="['10', '20', '50']"
            @change="loadList"
            @show-size-change="onPageSizeChange"
          />
        </div>
      </div>
    </div>

    <!-- 新建/修改弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="submitting"
      :ok-button-props="{ disabled: !canSubmit }"
      width="600px"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <!-- 基本信息 -->
        <a-divider orientation="left">基本信息</a-divider>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="客户名称" name="name">
              <a-input v-model:value="form.name" placeholder="请输入客户名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系人" name="contact">
              <a-input v-model:value="form.contact" placeholder="请输入联系人" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="联系电话" name="phone">
              <a-input v-model:value="form.phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="所属片区" name="area_id">
              <a-select
                v-model:value="form.area_id"
                placeholder="请选择片区"
                allow-clear
                style="width: 100%"
              >
                <a-select-option v-for="a in areaList" :key="a.id" :value="a.id">
                  {{ a.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="所属业务员" name="salesman">
              <a-select
                v-model:value="form.salesman"
                placeholder="请选择业务员"
                allow-clear
                style="width: 100%"
              >
                <a-select-option v-for="u in userList" :key="u.id" :value="u.id">
                  {{ u.real_name || u.username }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系地址" name="address">
              <a-input v-model:value="form.address" placeholder="请输入地址" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 会员信息 -->
        <a-divider orientation="left">会员信息</a-divider>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="会员类型" name="member_type_id">
              <a-select
                v-model:value="form.member_type_id"
                placeholder="请选择会员类型"
                allow-clear
                style="width: 100%"
              >
                <a-select-option v-for="mt in memberTypeList" :key="mt.id" :value="mt.id">
                  {{ mt.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="会员号" name="member_no">
              <a-input v-model:value="form.member_no" placeholder="留空自动生成" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="会员生日" name="birthday">
              <a-date-picker
                v-model:value="form.birthday"
                value-format="YYYY-MM-DD"
                placeholder="请选择生日"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 充值弹窗 -->
    <a-modal
      v-model:open="rechargeVisible"
      title="账户充值"
      ok-text="确认充值"
      cancel-text="取消"
      :confirm-loading="rechargeSubmitting"
      @ok="handleRecharge"
      @cancel="rechargeVisible = false"
    >
      <a-form layout="vertical">
        <a-form-item label="当前余额">
          <a-input :value="`¥ ${rechargeForm.balance}`" disabled />
        </a-form-item>
        <a-form-item label="充值金额" required>
          <a-input-number
            v-model:value="rechargeForm.amount"
            :min="0.01"
            :precision="2"
            style="width: 100%"
            placeholder="请输入充值金额"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { PlusOutlined, EllipsisOutlined, EditOutlined, WalletOutlined, DeleteOutlined, DownOutlined, RightOutlined } from '@ant-design/icons-vue'
import { getCustomerList, addCustomer, updateCustomer, rechargeCustomer, deleteCustomer } from '../api/customer'
import { getAreaList } from '../api/area'
import { getMemberTypeList } from '../api/memberType'
import { getUserList } from '../api/user'

// ── 列表状态 ──────────────────────────────────────────────
const list    = ref([])
const loading = ref(false)
const total   = ref(0)
const page    = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const selectedAreaId = ref(0)
const areaExpanded   = ref(true)  // 片区列表默认展开

// ── 下拉数据 ──────────────────────────────────────────────
const areaList       = ref([])
const memberTypeList = ref([])
const userList       = ref([])
// ── 表格列定义 ────────────────────────────────────────────
const columns = [
  { title: '序号',     key: 'seq',              width: 60,  align: 'center' },
  { title: '所属区域', dataIndex: 'area_name',  key: 'area_name',  width: 80,  ellipsis: true },
  { title: '名称',     dataIndex: 'name',       key: 'name',       width: 160,  ellipsis: true },
  { title: '联系人',   dataIndex: 'contact',    key: 'contact',    width: 70 },
  { title: '电话',     dataIndex: 'phone',      key: 'phone',      width: 125 },
  { title: '地址',     dataIndex: 'address',    key: 'address',    ellipsis: true },
  { title: '会员类型', key: 'member_type_name', width: 110 },
  { title: '会员号',   dataIndex: 'member_no',  key: 'member_no',  width: 105 },
  { title: '生日',     dataIndex: 'birthday',   key: 'birthday',   width: 100 },
  { title: '余额',     dataIndex: 'balance',    key: 'balance',    width: 80,  align: 'right' },
  { title: '积分',     dataIndex: 'points',     key: 'points',     width: 70,  align: 'right' },
  { title: '业务员',   dataIndex: 'salesman_name', key: 'salesman_name', width: 90 },
  { title: '操作',     key: 'action',           width: 60,  align: 'center', fixed: 'right' },
]

// ── 会员类型颜色 ──────────────────────────────────────────
function memberTypeColor(name) {
  if (!name) return 'default'
  if (name.includes('金')) return 'gold'
  if (name.includes('银')) return 'blue'
  if (name.includes('普通')) return 'default'
  return 'green'
}

// ── 加载列表 ──────────────────────────────────────────────
async function loadList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (keyword.value) params.keyword = keyword.value
    if (selectedAreaId.value > 0) params.area_id = selectedAreaId.value

    const res = await getCustomerList(params)
    if (res.code === 200) {
      list.value  = res.data.list
      total.value = res.data.total
    }
  } catch (e) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadList()
}

function onKeywordChange(e) {
  if (!e.target.value) {
    page.value = 1
    loadList()
  }
}

function onPageSizeChange(cur, size) {
  page.value = 1
  pageSize.value = size
  loadList()
}

function onAreaClick({ key }) {
  selectedAreaId.value = Number(key)
  page.value = 1
  loadList()
}

// ── 新建/修改弹窗 ─────────────────────────────────────────
const modalVisible = ref(false)
const modalTitle   = ref('创建新客户')
const submitting   = ref(false)
const formRef      = ref(null)
const editId       = ref(null)

const form = reactive({
  name: '', contact: '', phone: '', address: '',
  area_id: null, salesman: null,
  member_type_id: null, member_no: '', birthday: null,
})

const rules = {
  name:  [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}

const canSubmit = computed(() => !!form.name?.trim() && !!form.phone?.trim())

function openAdd() {
  editId.value   = null
  modalTitle.value = '创建新客户'
  resetForm()
  modalVisible.value = true
}

function openEdit(record) {
  editId.value   = record.id
  modalTitle.value = '修改客户信息'
  Object.assign(form, {
    name:           record.name,
    contact:        record.contact || '',
    phone:          record.phone   || '',
    address:        record.address || '',
    area_id:        record.area_id || null,
    salesman:       record.salesman || null,
    member_type_id: record.member_type_id || null,
    member_no:      record.member_no || '',
    birthday:       record.birthday || null,
  })
  modalVisible.value = true
}

function resetForm() {
  Object.assign(form, {
    name: '', contact: '', phone: '', address: '',
    area_id: null, salesman: null,
    member_type_id: null, member_no: '', birthday: null,
  })
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const payload = { ...form }
    if (editId.value) {
      payload.id = editId.value
      const res = await updateCustomer(payload)
      if (res.code === 200) {
        message.success('更新成功')
        modalVisible.value = false
        loadList()
      } else {
        message.error(res.msg || '更新失败')
      }
    } else {
      const res = await addCustomer(payload)
      if (res.code === 200) {
        message.success('新建成功')
        modalVisible.value = false
        page.value = 1
        loadList()
      } else {
        message.error(res.msg || '新建失败')
      }
    }
  } catch (e) {
    message.error(e.response?.data?.msg || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ── 充值弹窗 ──────────────────────────────────────────────
const rechargeVisible   = ref(false)
const rechargeSubmitting = ref(false)
const rechargeForm = reactive({ id: null, balance: 0, amount: null })

function openRecharge(record) {
  rechargeForm.id      = record.id
  rechargeForm.balance = record.balance
  rechargeForm.amount  = null
  rechargeVisible.value = true
}

async function handleRecharge() {
  if (!rechargeForm.amount || rechargeForm.amount <= 0) {
    message.warning('请输入有效的充值金额')
    return
  }
  rechargeSubmitting.value = true
  try {
    const res = await rechargeCustomer({ id: rechargeForm.id, amount: rechargeForm.amount })
    if (res.code === 200) {
      message.success(`充值成功，余额：¥${res.data.balance}`)
      rechargeVisible.value = false
      loadList()
    } else {
      message.error(res.msg || '充值失败')
    }
  } catch (e) {
    message.error(e.response?.data?.msg || '充值失败')
  } finally {
    rechargeSubmitting.value = false
  }
}

// ── 删除 ──────────────────────────────────────────────────
function confirmDelete(record) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除客户「${record.name}」吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        const res = await deleteCustomer({ id: record.id })
        if (res.code === 200) {
          message.success('删除成功')
          loadList()
        } else {
          message.error(res.msg || '删除失败')
        }
      } catch (e) {
        Modal.error({ title: '删除失败', content: e.response?.data?.msg || '操作异常' })
      }
    },
  })
}

// ── 初始化 ────────────────────────────────────────────────
onMounted(async () => {
  const [areaRes, mtRes, userRes] = await Promise.all([
    getAreaList(),
    getMemberTypeList(),
    getUserList(),
  ])
  if (areaRes.code === 200)  areaList.value       = areaRes.data
  if (mtRes.code === 200)    memberTypeList.value  = mtRes.data
  if (userRes.code === 200)  userList.value        = userRes.data
  loadList()
})
</script>

<style scoped>
.page-container {
  padding: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  margin-right: 8px;
}

.main-layout {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.area-sidebar {
  width: 180px;
  flex-shrink: 0;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

.sidebar-title {
  padding: 10px 16px;
  font-weight: 600;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.area-sidebar :deep(.ant-menu) {
  border-inline-end: none;
}

.area-toggle {
  display: inline-flex;
  align-items: center;
  margin-right: 6px;
  cursor: pointer;
}

.toggle-icon {
  font-size: 10px;
  color: #666;
  transition: transform 0.2s;
}

.area-child-item {
  padding-left: 32px !important;
}

:deep(.area-child-item.ant-menu-item) {
  padding-left: 32px !important;
}

.table-area {
  flex: 1;
  min-width: 0;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.action-btn {
  font-size: 18px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}

.action-btn:hover {
  background: #f0f0f0;
}

.danger-text {
  color: #ff4d4f;
}
</style>
