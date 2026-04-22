<template>
  <div class="page-container">
    <!-- 顶部搜索栏 -->
    <div class="toolbar">
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索姓名或电话"
        style="width: 220px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建销售业务员
      </a-button>
    </div>

    <!-- 数据列表 -->
    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      row-key="id"
      :pagination="false"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_default'">
          <a-tag v-if="record.is_default === 1" color="blue">默认</a-tag>
        </template>
        <template v-else-if="column.key === 'commission_rate'">
          {{ (Number(record.commission_rate) * 100).toFixed(2) }}%
        </template>
        <template v-else-if="column.key === 'action'">
          <a-dropdown trigger="click" :destroyPopupOnHide="true">
            <EllipsisOutlined class="action-btn" />
            <template #overlay>
              <a-menu>
                <a-menu-item key="edit" @click="openEdit(record)">编辑</a-menu-item>
                <a-menu-item key="delete" @click="confirmDelete(record)">
                  <span class="danger-text">删除</span>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
      </template>
    </a-table>

    <!-- 新建/编辑 Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="姓名" name="name">
          <a-input v-model:value="form.name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item label="电话" name="phone">
          <a-input v-model:value="form.phone" placeholder="请输入电话" />
        </a-form-item>
        <a-form-item label="地址" name="address">
          <a-input v-model:value="form.address" placeholder="请输入地址" />
        </a-form-item>
        <a-form-item label="销售提成比例（%）" name="commissionInput">
          <a-input-number
            v-model:value="form.commissionInput"
            :min="0"
            :max="100"
            :precision="2"
            placeholder="如输入5代表5%"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="默认销售员" name="is_default">
          <a-radio-group v-model:value="form.is_default">
            <a-radio :value="1">是</a-radio>
            <a-radio :value="0">否</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue'
import { getSalesStaffList, addSalesStaff, updateSalesStaff, deleteSalesStaff } from '../api/salesStaff'

const list = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建销售业务员')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', phone: '', address: '', commissionInput: 0, is_default: 0 })
const rules = {
  name: [{ required: true, message: '姓名不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '序号', key: 'index', width: 60, customRender: ({ index }) => index + 1 },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '电话', dataIndex: 'phone', key: 'phone' },
  { title: '地址', dataIndex: 'address', key: 'address' },
  { title: '销售提成比例', key: 'commission_rate', dataIndex: 'commission_rate', width: 120 },
  { title: '默认销售员', key: 'is_default', width: 100, align: 'center' },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getSalesStaffList(searchKeyword.value)
    list.value = res.data || []
  } finally {
    loading.value = false
  }
}

function onSearchChange(e) {
  if (!e.target.value) loadList()
}

function openAdd() {
  editingId.value = null
  modalTitle.value = '新建销售业务员'
  form.value = { name: '', phone: '', address: '', commissionInput: 0, is_default: 0 }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑销售业务员'
  form.value = {
    name: record.name,
    phone: record.phone || '',
    address: record.address || '',
    commissionInput: Number((Number(record.commission_rate) * 100).toFixed(2)),
    is_default: record.is_default,
  }
  modalVisible.value = true
}

function resetForm() {
  formRef.value?.resetFields()
  modalVisible.value = false
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      commission_rate: (form.value.commissionInput || 0) / 100,
    }
    delete payload.commissionInput
    if (editingId.value) {
      await updateSalesStaff({ id: editingId.value, ...payload })
      message.success('更新成功')
    } else {
      await addSalesStaff(payload)
      message.success('新建成功')
    }
    modalVisible.value = false
    loadList()
  } catch (err) {
    message.error(err.response?.data?.msg || '操作失败')
  } finally {
    submitting.value = false
  }
}

function confirmDelete(record) {
  Modal.confirm({
    title: '确定删除该销售业务员？',
    content: `将删除"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteSalesStaff({ id: record.id })
    message.success('删除成功')
    loadList()
  } catch (err) {
    Modal.error({
      title: '无法删除',
      content: err.response?.data?.msg || '删除失败',
      okText: '我知道了',
    })
  }
}

onMounted(loadList)
</script>

<style scoped>
.page-container { padding: 16px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.action-btn { cursor: pointer; font-size: 18px; padding: 4px 8px; }
.danger-text { color: #ff4d4f; }
</style>
