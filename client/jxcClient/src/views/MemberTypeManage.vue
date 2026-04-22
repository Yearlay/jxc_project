<template>
  <div class="page-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <a-input-search
        v-model:value="searchName"
        placeholder="搜索会员名称"
        style="width: 220px"
        allow-clear
        @search="loadList"
        @change="onSearchChange"
      />
      <a-button type="primary" @click="openAdd">
        <PlusOutlined />新建会员类型
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
        <!-- 折扣率列：显示为百分比 -->
        <template v-if="column.key === 'discount'">
          {{ discountLabel(record.discount) }}
        </template>

        <!-- 状态列 -->
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'default'">
            {{ record.status === 1 ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <!-- 操作列 -->
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
        <a-form-item label="类型名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入类型名称" />
        </a-form-item>
        <a-form-item label="折扣率" name="discount">
          <a-input-number
            v-model:value="form.discount"
            :min="0.01"
            :max="1.00"
            :step="0.01"
            :precision="2"
            style="width: 100%"
            placeholder="0.01 ~ 1.00（如 0.88 表示 88 折）"
          />
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
import { getMemberTypeList, addMemberType, updateMemberType, deleteMemberType } from '../api/memberType'

const list = ref([])
const loading = ref(false)
const searchName = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新建会员类型')
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = ref({ name: '', discount: 1.00, remark: '', status: 1 })

const rules = {
  name: [{ required: true, message: '类型名称不能为空', trigger: 'blur' }],
  discount: [
    { required: true, message: '折扣率不能为空', trigger: 'change' },
    {
      validator: (_, value) => {
        if (value === null || value === undefined) return Promise.reject('折扣率不能为空')
        if (value < 0.01 || value > 1.00) return Promise.reject('折扣率必须在 0.01 ~ 1.00 之间')
        return Promise.resolve()
      },
      trigger: 'change',
    },
  ],
}

const columns = [
  { title: '类型名称', dataIndex: 'name', key: 'name' },
  { title: '折扣率', dataIndex: 'discount', key: 'discount', width: 120 },
  { title: '备注', dataIndex: 'remark', key: 'remark' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '操作', key: 'action', width: 60, align: 'center' },
]

function discountLabel(val) {
  if (val === 1 || val === 1.0) return '无折扣'
  return Math.round(val * 100) + ' 折'
}

async function loadList() {
  loading.value = true
  try {
    const res = await getMemberTypeList(searchName.value)
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
  modalTitle.value = '新建会员类型'
  form.value = { name: '', discount: 1.00, remark: '', status: 1 }
  modalVisible.value = true
}

function openEdit(record) {
  editingId.value = record.id
  modalTitle.value = '编辑会员类型'
  form.value = { name: record.name, discount: record.discount, remark: record.remark || '', status: record.status }
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
      await updateMemberType({ id: editingId.value, ...form.value })
      message.success('更新成功')
    } else {
      await addMemberType(form.value)
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
    title: '确定删除该会员类型？',
    content: `将删除会员类型"${record.name}"，删除后不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(record),
  })
}

async function doDelete(record) {
  try {
    await deleteMemberType({ id: record.id })
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
