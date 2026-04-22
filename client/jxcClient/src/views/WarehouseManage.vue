<template>
  <div class="page-container">
    <!-- 顶部搜索栏 -->
    <div class="toolbar">
      <a-input-search
        v-model:value="searchName"
        placeholder="请输入仓库名称"
        style="width: 220px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />创建新仓库
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
        <!-- 操作列 -->
        <template v-if="column.key === 'action'">
          <a-dropdown trigger="click" :destroyPopupOnHide="true">
            <EllipsisOutlined class="action-btn" />
            <template #overlay>
              <a-menu>
                <a-menu-item key="edit" @click="openEdit(record)">
                  <EditOutlined style="margin-right:6px" />修改
                </a-menu-item>
                <a-menu-item key="delete" @click="confirmDelete(record)">
                  <DeleteOutlined style="margin-right:6px; color:#ff4d4f" />
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
        <a-form-item label="仓库名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入仓库名称" />
        </a-form-item>
        <a-form-item label="仓库地址" name="address">
          <a-input v-model:value="form.address" placeholder="请输入仓库地址（可选）" />
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
import {
  PlusOutlined,
  EllipsisOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons-vue'
import {
  getWarehouseList,
  addWarehouse,
  updateWarehouse,
  deleteWarehouse,
} from '../api/warehouse'

const list = ref([])
const loading = ref(false)
const searchName = ref('')

const modalVisible = ref(false)
const modalTitle = ref('创建新仓库')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', address: '', remark: '' })
const rules = {
  name: [{ required: true, message: '仓库名称不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '仓库名称', dataIndex: 'name', key: 'name' },
  { title: '地址', dataIndex: 'address', key: 'address' },
  { title: '备注', dataIndex: 'remark', key: 'remark' },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getWarehouseList(searchName.value)
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
  modalTitle.value = '创建新仓库'
  form.value = { name: '', address: '', remark: '' }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '修改仓库'
  form.value = { name: record.name, address: record.address || '', remark: record.remark || '' }
  modalVisible.value = true
}

function resetForm() {
  formRef.value?.clearValidate()
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
      await updateWarehouse({ id: editingId.value, ...form.value })
      message.success('修改成功')
    } else {
      await addWarehouse(form.value)
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
    title: '确定删除该仓库？',
    content: `将删除仓库"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteWarehouse({ id: record.id })
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
