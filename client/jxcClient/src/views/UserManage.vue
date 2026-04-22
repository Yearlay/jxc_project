<template>
  <div class="page-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <a-input
        v-model:value="searchKeyword"
        placeholder="请输入用户名搜索"
        style="width: 220px"
        allow-clear
        @pressEnter="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />创建新用户
      </a-button>
    </div>

    <!-- 用户列表 -->
    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      row-key="id"
      :pagination="false"
    >
      <template #bodyCell="{ column, record }">
        <!-- 操作仓库 -->
        <template v-if="column.key === 'warehouse_names'">
          {{ (record.warehouse_names || []).join('、') || '-' }}
        </template>
        <!-- 管辖片区 -->
        <template v-else-if="column.key === 'area_names'">
          {{ (record.area_names || []).join('、') || '-' }}
        </template>
        <!-- 角色 -->
        <template v-else-if="column.key === 'role'">
          <a-tag :color="record.role === 'admin' ? 'blue' : ''">
            {{ record.role === 'admin' ? '管理员' : '普通用户' }}
          </a-tag>
        </template>
        <!-- 状态 -->
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'default'">
            {{ record.status === 1 ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <a-dropdown v-if="record.username !== 'admin'" trigger="click" :destroyPopupOnHide="true">
            <EllipsisOutlined class="action-btn" />
            <template #overlay>
              <a-menu>
                <a-menu-item key="edit" @click="openEdit(record)">
                  <EditOutlined style="margin-right:6px" />修改
                </a-menu-item>
                <a-menu-item key="resetpwd" @click="openResetPwd(record)">
                  <KeyOutlined style="margin-right:6px" />密码重置
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

    <!-- 新建/修改 Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form :model="form" :rules="formRules" ref="formRef" layout="vertical">
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="姓名" name="real_name">
          <a-input v-model:value="form.real_name" placeholder="请输入姓名（可选）" />
        </a-form-item>
        <!-- 密码仅新建时显示 -->
        <a-form-item v-if="!editingId" label="密码" name="password">
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="角色" name="role">
          <a-select v-model:value="form.role" style="width: 100%">
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="staff">普通用户</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="操作仓库" name="warehouse_ids">
          <a-select
            v-model:value="form.warehouse_ids"
            mode="multiple"
            placeholder="请选择操作仓库（可多选）"
            allow-clear
            style="width: 100%"
            :options="warehouseOptions.map(w => ({ label: w.name, value: w.id }))"
          />
        </a-form-item>
        <a-form-item label="管辖片区" name="area_ids">
          <a-select
            v-model:value="form.area_ids"
            mode="multiple"
            placeholder="请选择管辖片区（可多选）"
            allow-clear
            style="width: 100%"
            :options="areaOptions.filter(a => a.name !== '未划分').map(a => ({ label: a.name, value: a.id }))"
          />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="form.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 密码重置 Modal -->
    <a-modal
      v-model:open="pwdModalVisible"
      title="重置密码"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="pwdSubmitting"
      @ok="handleResetPwd"
      @cancel="resetPwdForm"
    >
      <a-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" layout="vertical">
        <a-form-item label="新密码" name="password">
          <a-input-password v-model:value="pwdForm.password" placeholder="请输入新密码（至少6位）" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password v-model:value="pwdForm.confirmPassword" placeholder="请再次输入密码" />
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
  KeyOutlined,
} from '@ant-design/icons-vue'
import { getManageUserList, addManageUser, updateManageUser, resetPassword, deleteManageUser } from '../api/user'
import { getWarehouseList } from '../api/warehouse'
import { getAreaList } from '../api/area'

// ── 列表 ──────────────────────────────────────────────────
const list = ref([])
const loading = ref(false)
const searchKeyword = ref('')

const columns = [
  { title: '用户名',   dataIndex: 'username',       key: 'username' },
  { title: '姓名',     dataIndex: 'real_name',      key: 'real_name' },
  { title: '角色',     dataIndex: 'role',           key: 'role' },
  { title: '操作仓库', key: 'warehouse_names' },
  { title: '管辖片区', key: 'area_names' },
  { title: '状态',     dataIndex: 'status',         key: 'status' },
  { title: '操作',     key: 'action', width: 60, align: 'center' },
]

async function loadList() {
  loading.value = true
  try {
    const res = await getManageUserList(searchKeyword.value)
    list.value = res.data || []
  } finally {
    loading.value = false
  }
}

function onSearchChange(e) {
  if (!e.target.value) loadList()
}

// ── 仓库/片区下拉 ──────────────────────────────────────────
const warehouseOptions = ref([])
const areaOptions = ref([])

async function loadOptions() {
  const [wRes, aRes] = await Promise.all([getWarehouseList(), getAreaList()])
  warehouseOptions.value = wRes.data || []
  areaOptions.value = aRes.data || []
}

// ── 新建/修改 ──────────────────────────────────────────────
const modalVisible = ref(false)
const modalTitle = ref('')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({
  username: '', real_name: '', password: '',
  role: 'staff', status: 1, warehouse_ids: [], area_ids: [],
})

const formRules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' }],
}

function openAdd() {
  editingId.value = null
  modalTitle.value = '创建新用户'
  form.value = { username: '', real_name: '', password: '', role: 'staff', status: 1, warehouse_ids: [], area_ids: [] }
  loadOptions()
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '修改用户'
  form.value = {
    username:      record.username,
    real_name:     record.real_name || '',
    password:      '',
    role:          record.role,
    status:        record.status,
    warehouse_ids: record.warehouse_ids || [],
    area_ids:      record.area_ids || [],
  }
  loadOptions()
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
      const { password: _p, ...rest } = form.value
      await updateManageUser({ id: editingId.value, ...rest })
      message.success('修改成功')
    } else {
      await addManageUser(form.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadList()
  } catch (err) {
    message.error(err.response?.data?.msg || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ── 密码重置 ────────────────────────────────────────────────
const pwdModalVisible = ref(false)
const pwdSubmitting = ref(false)
const pwdFormRef = ref()
const pwdForm = ref({ password: '', confirmPassword: '' })
const pwdTargetId = ref(null)

const validateConfirmPwd = (_rule, value) => {
  if (!value) return Promise.reject('请确认密码')
  if (value !== pwdForm.value.password) return Promise.reject('两次密码不一致')
  return Promise.resolve()
}

const pwdRules = {
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [{ validator: validateConfirmPwd, trigger: 'blur' }],
}

function openResetPwd(record) {
  pwdTargetId.value = record.id
  pwdForm.value = { password: '', confirmPassword: '' }
  pwdModalVisible.value = true
}

function resetPwdForm() {
  pwdFormRef.value?.clearValidate()
  pwdModalVisible.value = false
}

async function handleResetPwd() {
  try {
    await pwdFormRef.value.validate()
  } catch {
    return
  }
  pwdSubmitting.value = true
  try {
    await resetPassword({ id: pwdTargetId.value, password: pwdForm.value.password })
    message.success('密码重置成功')
    pwdModalVisible.value = false
  } catch (err) {
    message.error(err.response?.data?.msg || '重置失败')
  } finally {
    pwdSubmitting.value = false
  }
}

// ── 删除 ────────────────────────────────────────────────────
function confirmDelete(record) {
  Modal.confirm({
    title: '确定删除该用户？',
    content: `将删除用户"${record.username}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteManageUser({ id: record.id })
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
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #f0f0f0;
}

.danger-text {
  color: #ff4d4f;
}
</style>
