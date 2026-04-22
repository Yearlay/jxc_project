<template>
  <div class="page-container">
    <div class="toolbar">
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索车牌号/车主/电话"
        style="width: 240px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建车辆
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
        <a-form-item label="车牌号" name="plate">
          <a-input v-model:value="form.plate" placeholder="请输入车牌号" />
        </a-form-item>
        <a-form-item label="车主" name="owner">
          <a-input v-model:value="form.owner" placeholder="车主姓名（可选）" />
        </a-form-item>
        <a-form-item label="车主电话" name="owner_phone">
          <a-input v-model:value="form.owner_phone" placeholder="车主电话（可选）" />
        </a-form-item>
        <a-form-item label="备注" name="remark">
          <a-input v-model:value="form.remark" placeholder="备注（可选）" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue'
import { getVehicleList, addVehicle, updateVehicle, deleteVehicle } from '../api/vehicle'

const list = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建车辆')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ plate: '', owner: '', owner_phone: '', remark: '' })
const rules = {
  plate: [{ required: true, message: '车牌号不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '序号', key: 'index', width: 70 },
  { title: '车牌号', dataIndex: 'plate', key: 'plate' },
  { title: '车主', dataIndex: 'owner', key: 'owner' },
  { title: '车主电话', dataIndex: 'owner_phone', key: 'owner_phone' },
  { title: '备注', dataIndex: 'remark', key: 'remark' },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getVehicleList(searchKeyword.value)
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
  modalTitle.value = '新建车辆'
  form.value = { plate: '', owner: '', owner_phone: '', remark: '' }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑车辆'
  form.value = {
    plate: record.plate,
    owner: record.owner || '',
    owner_phone: record.owner_phone || '',
    remark: record.remark || '',
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
      await updateVehicle({ id: editingId.value, ...form.value })
      message.success('更新成功')
    } else {
      await addVehicle(form.value)
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
    title: '确定删除该车辆？',
    content: `将删除车辆"${record.plate}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteVehicle({ id: record.id })
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
