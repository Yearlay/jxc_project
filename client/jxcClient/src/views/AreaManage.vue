<template>
  <div class="page-container">
    <!-- 顶部搜索栏 -->
    <div class="toolbar">
      <a-input-search
        v-model:value="searchName"
        placeholder="搜索片区名称"
        style="width: 220px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建片区
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
      <!-- 状态列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'default'">
            {{ record.status === 1 ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <a-dropdown
            v-if="record.is_default !== 1"
            trigger="click"
            :destroyPopupOnHide="true"
          >
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
        <a-form-item label="片区名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入片区名称" />
        </a-form-item>
        <a-form-item label="备注" name="remark">
          <a-input v-model:value="form.remark" placeholder="备注（可选）" />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="form.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
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
import { getAreaList, addArea, updateArea, deleteArea } from '../api/area'

const list = ref([])
const loading = ref(false)
const searchName = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建片区')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', remark: '', status: 1 })
const rules = {
  name: [{ required: true, message: '片区名称不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '片区名称', dataIndex: 'name', key: 'name' },
  { title: '备注', dataIndex: 'remark', key: 'remark' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getAreaList(searchName.value)
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
  modalTitle.value = '新建片区'
  form.value = { name: '', remark: '', status: 1 }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑片区'
  form.value = { name: record.name, remark: record.remark || '', status: record.status }
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
      await updateArea({ id: editingId.value, ...form.value })
      message.success('更新成功')
    } else {
      await addArea(form.value)
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
    title: '确定删除该片区？',
    content: `将删除片区"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteArea({ id: record.id })
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
