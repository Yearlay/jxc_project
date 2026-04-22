<template>
  <div class="page-container">
    <!-- 顶部搜索栏 -->
    <div class="toolbar">
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索名称或编号"
        style="width: 220px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建销售终端
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
        <a-form-item label="终端名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入终端名称" />
        </a-form-item>
        <a-form-item label="终端编号" name="code">
          <a-input v-model:value="form.code" placeholder="请输入终端编号（唯一）" />
        </a-form-item>
        <a-form-item label="数据库编号" name="db_no">
          <a-input v-model:value="form.db_no" placeholder="终端独立数据库编号（可选）" />
        </a-form-item>
        <a-form-item label="默认终端" name="is_default">
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
import { getTerminalList, addTerminal, updateTerminal, deleteTerminal } from '../api/terminal'

const list = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建销售终端')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', code: '', db_no: '', is_default: 0 })
const rules = {
  name: [{ required: true, message: '终端名称不能为空', trigger: 'blur' }],
  code: [{ required: true, message: '终端编号不能为空', trigger: 'blur' }],
}

const columns = [
  { title: '序号', key: 'index', width: 60, customRender: ({ index }) => index + 1 },
  { title: '终端名称', dataIndex: 'name', key: 'name' },
  { title: '终端编号', dataIndex: 'code', key: 'code' },
  { title: '数据库编号', dataIndex: 'db_no', key: 'db_no' },
  { title: '默认终端', key: 'is_default', width: 100, align: 'center' },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getTerminalList(searchKeyword.value)
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
  modalTitle.value = '新建销售终端'
  form.value = { name: '', code: '', db_no: '', is_default: 0 }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑销售终端'
  form.value = {
    name: record.name,
    code: record.code,
    db_no: record.db_no || '',
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
    if (editingId.value) {
      await updateTerminal({ id: editingId.value, ...form.value })
      message.success('更新成功')
    } else {
      await addTerminal(form.value)
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
    title: '确定删除该销售终端？',
    content: `将删除终端"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteTerminal({ id: record.id })
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
