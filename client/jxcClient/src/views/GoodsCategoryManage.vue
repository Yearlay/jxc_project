<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="toolbar-copy">
        <div class="page-title">商品分类</div>
        <div class="page-subtitle">维护一级、二级和三级分类结构</div>
      </div>
      <a-button type="primary" class="create-btn" @click="openAddRoot">
        <PlusOutlined />新增一级分类
      </a-button>
    </div>

    <div class="tree-shell">
      <div class="tree-shell-header">
        <div>
          <div class="tree-shell-title">商品分类列表</div>
        </div>
        <div class="tree-stat">共 {{ categoryCount }} 个分类</div>
      </div>

      <a-spin :spinning="loading">
        <a-empty v-if="!treeData.length" description="暂无分类数据" class="empty-block" />
        <a-tree
          v-else
          :tree-data="displayTreeData"
          :field-names="treeFieldNames"
          :default-expand-all="true"
          :show-line="{ showLeafIcon: false }"
          :selectable="false"
          block-node
          class="category-tree"
        >
          <template #switcherIcon="{ expanded }">
            <span class="tree-switcher-box" aria-hidden="true">
              <MinusSquareOutlined v-if="expanded" />
              <PlusSquareOutlined v-else />
            </span>
          </template>
          <template #title="node">
            <div :class="['tree-node', { 'is-virtual-root': node.is_virtual }]">
              <div class="tree-node-main">
                <span
                  :class="['tree-node-name', {
                    'is-root': node.parent_id === 0,
                    'is-virtual-root-name': node.is_virtual,
                  }]"
                >
                  {{ node.name || node.title }}
                </span>
                <span v-if="!node.is_virtual" class="tree-level-badge">
                  {{ levelText(node) }}
                </span>
                <a-tag v-if="node.is_system === 1" color="default">系统默认</a-tag>
              </div>

              <a-dropdown v-if="showActions(node)" trigger="click" :destroyPopupOnHide="true">
                <EllipsisOutlined class="action-btn" @click.stop />
                <template #overlay>
                  <a-menu>
                    <a-menu-item v-if="canAddChild(node)" key="add" @click="openAddChild(node)">
                      <PlusOutlined style="margin-right: 6px" />新增子分类
                    </a-menu-item>
                    <a-menu-item key="edit" @click="openEdit(node)">
                      <EditOutlined style="margin-right: 6px" />修改
                    </a-menu-item>
                    <a-menu-item key="delete" @click="confirmDelete(node)">
                      <DeleteOutlined style="margin-right: 6px" /><span class="danger-text">删除</span>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>
          </template>
        </a-tree>
      </a-spin>
    </div>

    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form ref="formRef" :model="form" :rules="rules" layout="vertical">
        <a-form-item v-if="modalMode === 'add-child'" label="父分类">
          <a-input :value="parentName" disabled />
        </a-form-item>
        <a-form-item v-if="modalMode === 'edit'" label="上级分类">
          <a-input :value="parentName || '一级分类'" disabled />
        </a-form-item>
        <a-form-item label="分类名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入分类名称" :maxlength="50" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  EllipsisOutlined,
  EditOutlined,
  DeleteOutlined,
  MinusSquareOutlined,
  PlusSquareOutlined,
} from '@ant-design/icons-vue'
import {
  getGoodsCategoryTree,
  addGoodsCategory,
  updateGoodsCategory,
  deleteGoodsCategory,
} from '../api/goodsCategory'

const loading = ref(false)
const treeData = ref([])
const modalVisible = ref(false)
const modalTitle = ref('新增一级分类')
const modalMode = ref('add-root')
const submitting = ref(false)
const formRef = ref()
const editingId = ref(null)
const parentName = ref('')
const form = reactive({
  name: '',
  parent_id: 0,
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

const treeFieldNames = {
  title: 'name',
  key: 'id',
  children: 'children',
}

const flatNodeMap = computed(() => {
  const map = new Map()
  const walk = (nodes) => {
    nodes.forEach((node) => {
      map.set(node.id, node)
      if (node.children?.length) {
        walk(node.children)
      }
    })
  }
  walk(treeData.value)
  return map
})

const displayTreeData = computed(() => [{
  id: 'all-categories',
  name: '所有分类',
  parent_id: -1,
  is_virtual: true,
  children: treeData.value,
}])

const categoryCount = computed(() => flatNodeMap.value.size)

async function loadTree() {
  loading.value = true
  try {
    const res = await getGoodsCategoryTree()
    treeData.value = res.data || []
  } catch (err) {
    message.error(err.response?.data?.msg || '加载分类失败')
  } finally {
    loading.value = false
  }
}

function openAddRoot() {
  modalMode.value = 'add-root'
  modalTitle.value = '新增一级分类'
  editingId.value = null
  parentName.value = ''
  form.name = ''
  form.parent_id = 0
  modalVisible.value = true
}

function openAddChild(node) {
  modalMode.value = 'add-child'
  modalTitle.value = '新增子分类'
  editingId.value = null
  parentName.value = node.name
  form.name = ''
  form.parent_id = node.id
  modalVisible.value = true
}

function openEdit(node) {
  modalMode.value = 'edit'
  modalTitle.value = '修改分类'
  editingId.value = node.id
  const parent = node.parent_id ? flatNodeMap.value.get(node.parent_id) : null
  parentName.value = parent?.name || ''
  form.name = node.name
  form.parent_id = node.parent_id
  modalVisible.value = true
}

function resetForm() {
  formRef.value?.clearValidate()
  modalVisible.value = false
  form.name = ''
  form.parent_id = 0
  parentName.value = ''
  editingId.value = null
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (modalMode.value === 'edit') {
      const res = await updateGoodsCategory({ id: editingId.value, name: form.name.trim() })
      if (res.code === 200) {
        message.success('修改成功')
      }
    } else {
      const res = await addGoodsCategory({ name: form.name.trim(), parent_id: form.parent_id })
      if (res.code === 200) {
        message.success('新建成功')
      }
    }
    modalVisible.value = false
    resetForm()
    loadTree()
  } catch (err) {
    message.error(err.response?.data?.msg || '操作失败')
  } finally {
    submitting.value = false
  }
}

function confirmDelete(node) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除分类“${node.name}”吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        const res = await deleteGoodsCategory({ id: node.id })
        if (res.code === 200) {
          message.success('删除成功')
          loadTree()
        }
      } catch (err) {
        message.error(err.response?.data?.msg || '删除失败')
      }
    },
  })
}

function showActions(node) {
  return !node.is_virtual && node.is_system !== 1
}

function getNodeLevel(node) {
  let level = 1
  let currentParentId = node.parent_id
  while (currentParentId && currentParentId !== 0) {
    const parent = flatNodeMap.value.get(currentParentId)
    if (!parent) break
    level += 1
    currentParentId = parent.parent_id
  }
  return level
}

function canAddChild(node) {
  return !node.is_virtual && node.is_system !== 1 && getNodeLevel(node) < 3
}

function levelText(node) {
  const level = getNodeLevel(node)
  if (level === 1) return '一级'
  if (level === 2) return '二级'
  if (level === 3) return '三级'
  return `${level}级`
}

onMounted(loadTree)
</script>

<style scoped>
.page-container {
  padding: 16px;
  min-height: 100%;
  background: linear-gradient(180deg, #fcfcfd 0%, #f5f7fa 100%);
}

.toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.toolbar-copy {
  min-width: 0;
}

.page-title {
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  color: #1b2430;
}

.create-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  box-shadow: 0 10px 24px rgba(22, 119, 255, 0.18);
}

.tree-shell {
  min-height: 480px;
  padding: 18px 18px 22px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(8px);
}

.tree-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  margin-bottom: 10px;
  border-bottom: 1px solid #eef1f5;
}

.tree-shell-title {
  font-size: 17px;
  font-weight: 700;
  color: #202939;
}

.tree-shell-subtitle {
  margin-top: 4px;
  color: #7d8694;
  font-size: 12px;
}

.tree-stat {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: #f3f7ff;
  color: #2859c5;
  font-size: 12px;
  font-weight: 600;
}

.empty-block {
  padding: 56px 0 32px;
}

.category-tree {
  padding-top: 2px;
}

.tree-switcher-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 8px;
  width: 18px;
  height: 18px;
  font-size: 14px;
  line-height: 1;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  height: 34px;
  padding: 0 8px;
  border-radius: 10px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.tree-node:hover {
  background: #f7faff;
}

.tree-node.is-virtual-root {
  margin-left: -4px;
  padding-left: 2px;
}

.tree-node-main {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  min-width: 0;
}

.tree-node-name {
  display: flex;
  align-items: center;
  color: #2a3342;
  font-size: 14px;
  height: 34px;
  line-height: 1;
}

.tree-node-name.is-root {
  font-weight: 600;
}

.tree-node-name.is-virtual-root-name {
  font-size: 16px;
  font-weight: 700;
  color: #141b26;
}

.tree-level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1px 8px;
  border-radius: 999px;
  background: #f2f4f7;
  color: #7b8494;
  font-size: 11px;
  height: 20px;
  line-height: 1;
}

.action-btn {
  font-size: 18px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 8px;
  color: #7c8596;
  opacity: 1;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #ebf2ff;
  color: #2d63d6;
}

.danger-text {
  color: #ff4d4f;
}

.category-tree :deep(.ant-tree-indent) {
  display: flex;
  align-items: center;
  height: 34px;
}

.category-tree :deep(.ant-tree-indent-unit) {
  width: 18px;
  height: 34px;
}

.category-tree :deep(.ant-tree-treenode) {
  align-items: center;
  min-height: 34px;
}

.category-tree :deep(.ant-tree-node-content-wrapper) {
  display: flex;
  align-items: center;
  flex: 1;
  height: 34px;
  min-width: 0;
  padding: 0 !important;
  background: transparent !important;
  line-height: 1 !important;
}

.category-tree :deep(.ant-tree-title) {
  display: flex;
  align-items: center;
  width: 100%;
  height: 34px;
  line-height: 1;
}

.category-tree :deep(.ant-tree-switcher) {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 18px;
  width: 18px;
  height: 34px;
  padding: 0;
  line-height: 1;
  color: #98a2b3;
}

.category-tree :deep(.ant-tree-switcher-noop),
.category-tree :deep(.ant-tree-switcher-icon),
.category-tree :deep(.ant-tree-switcher-icon svg),
.category-tree :deep(.ant-tree-switcher-leaf-line) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-tree :deep(.ant-tree-switcher-noop) {
  width: 18px;
  height: 34px;
}

.category-tree :deep(.ant-tree-switcher-leaf-line) {
  width: 18px;
  height: 18px;
}

.category-tree :deep(.ant-tree-list-holder-inner) {
  gap: 2px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .create-btn {
    width: 100%;
  }

  .tree-shell {
    padding: 16px 14px 18px;
    border-radius: 16px;
  }

  .tree-shell-header {
    flex-direction: column;
  }
}
</style>