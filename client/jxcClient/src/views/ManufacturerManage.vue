<template>
  <div class="page-container">
    <div class="toolbar">
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索厂家名称或电话"
        style="width: 240px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建厂家
      </a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      row-key="id"
      :pagination="false"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'index'">
          {{ list.indexOf(record) + 1 }}
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
        <a-form-item label="厂家名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入厂家名称" />
        </a-form-item>
        <a-form-item label="电话" name="phone">
          <a-input v-model:value="form.phone" placeholder="联系电话（可选）" />
        </a-form-item>
        <a-form-item label="地址" name="address">
          <a-input v-model:value="form.address" placeholder="厂家地址（可选）" />
        </a-form-item>
        <a-form-item label="营业执照" name="license">
          <a-input v-model:value="form.license" placeholder="营业执照号（可选）" />
        </a-form-item>
        <a-form-item label="银行账户" name="bank_account">
          <a-input v-model:value="form.bank_account" placeholder="银行账户（可选）" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue'
import { getManufacturerList, addManufacturer, updateManufacturer, deleteManufacturer } from '../api/manufacturer'

const list = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建厂家')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', phone: '', address: '', license: '', bank_account: '' })
const rules = {
  name: [{ required: true, message: '厂家名称不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '序号', key: 'index', width: 70 },
  { title: '厂家名称', dataIndex: 'name', key: 'name' },
  { title: '电话', dataIndex: 'phone', key: 'phone' },
  { title: '地址', dataIndex: 'address', key: 'address' },
  { title: '营业执照', dataIndex: 'license', key: 'license' },
  { title: '银行账户', dataIndex: 'bank_account', key: 'bank_account' },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getManufacturerList(searchKeyword.value)
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
  modalTitle.value = '新建厂家'
  form.value = { name: '', phone: '', address: '', license: '', bank_account: '' }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑厂家'
  form.value = {
    name: record.name,
    phone: record.phone || '',
    address: record.address || '',
    license: record.license || '',
    bank_account: record.bank_account || '',
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
    if (editingId.value) {
      await updateManufacturer({ id: editingId.value, ...form.value })
      message.success('更新成功')
    } else {
      await addManufacturer(form.value)
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
    title: '确定删除该厂家？',
    content: `将删除厂家"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteManufacturer({ id: record.id })
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
.page-container {
  padding: 16px;
}
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}
.action-btn {
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: #666;
}
.action-btn:hover {
  background: #f0f0f0;
}
.danger-text {
  color: #ff4d4f;
}
</style>
