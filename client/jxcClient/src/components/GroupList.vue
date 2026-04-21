<template>
  <div class="group-list-wrap">
    <!-- 权限组列表 -->
    <div class="group-scroll">
      <div
        v-for="g in groups"
        :key="g.id"
        class="group-item"
        :class="{ active: g.id === selectedId }"
        @click="selectGroup(g)"
      >
        <div class="group-info">
          <span class="group-name">{{ g.name }}</span>
          <span class="group-count">{{ g.member_count }} 人</span>
        </div>
        <a-dropdown v-if="g.name !== '管理员'" trigger="['click']" :destroyPopupOnHide="true">
          <EllipsisOutlined class="more-btn" @click.stop />
          <template #overlay>
            <a-menu>
              <a-menu-item key="rename" @click.stop="openRename(g)">重命名</a-menu-item>
              <a-menu-item key="delete" @click.stop="confirmDelete(g)">
                <span class="danger-text">删除</span>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 添加按钮 -->
    <div class="add-btn-wrap">
      <a-button type="dashed" block @click="openAdd">
        <PlusOutlined />添加权限组
      </a-button>
    </div>

    <!-- 添加权限组 Modal -->
    <a-modal
      v-model:open="addVisible"
      title="添加权限组"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="addLoading"
      @ok="doAdd"
    >
      <a-form layout="vertical" style="margin-top:16px">
        <a-form-item label="权限组名称" required>
          <a-input v-model:value="addForm.name" placeholder="请输入权限组名称" />
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="addForm.remark" placeholder="选填" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重命名 Modal -->
    <a-modal
      v-model:open="renameVisible"
      title="重命名权限组"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="renameLoading"
      @ok="doRename"
    >
      <a-input
        v-model:value="renameForm.name"
        placeholder="请输入新名称"
        style="margin-top:16px"
      />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { EllipsisOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getGroupList, addGroup, renameGroup, deleteGroup } from '../api/group'

const emit = defineEmits(['select'])

const groups = ref([])
const selectedId = ref(null)

// ── 加载列表 ──────────────────────────────
async function loadGroups() {
  const res = await getGroupList()
  if (res.code === 200) {
    groups.value = res.data
    // 若当前选中项仍存在则保持，否则清空
    if (selectedId.value && !groups.value.find(g => g.id === selectedId.value)) {
      selectedId.value = null
      emit('select', null)
    }
  }
}

onMounted(loadGroups)

// 暴露给父组件调用（成员变更后刷新计数）
defineExpose({ loadGroups })

function selectGroup(g) {
  selectedId.value = g.id
  emit('select', g)
}

// ── 添加 ──────────────────────────────────
const addVisible = ref(false)
const addLoading = ref(false)
const addForm = ref({ name: '', remark: '' })

function openAdd() {
  addForm.value = { name: '', remark: '' }
  addVisible.value = true
}

async function doAdd() {
  if (!addForm.value.name.trim()) {
    message.warning('请输入权限组名称')
    return
  }
  addLoading.value = true
  try {
    const res = await addGroup(addForm.value)
    if (res.code === 200) {
      message.success('添加成功')
      addVisible.value = false
      await loadGroups()
    } else {
      message.error(res.msg)
    }
  } finally {
    addLoading.value = false
  }
}

// ── 重命名 ────────────────────────────────
const renameVisible = ref(false)
const renameLoading = ref(false)
const renameForm = ref({ id: null, name: '' })

function openRename(g) {
  renameForm.value = { id: g.id, name: g.name }
  renameVisible.value = true
}

async function doRename() {
  if (!renameForm.value.name.trim()) {
    message.warning('请输入新名称')
    return
  }
  renameLoading.value = true
  try {
    const res = await renameGroup(renameForm.value)
    if (res.code === 200) {
      message.success('重命名成功')
      renameVisible.value = false
      await loadGroups()
    } else {
      message.error(res.msg)
    }
  } finally {
    renameLoading.value = false
  }
}

// ── 删除 ──────────────────────────────────
function confirmDelete(g) {
  Modal.confirm({
    title: '确定删除该权限组？',
    content: '请先确保组内无成员，删除后不可恢复。',
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => doDelete(g),
  })
}

async function doDelete(g) {
  try {
    const res = await deleteGroup({ id: g.id })
    if (res.code === 200) {
      message.success('删除成功')
      if (selectedId.value === g.id) {
        selectedId.value = null
        emit('select', null)
      }
      await loadGroups()
    } else {
      Modal.error({ title: '无法删除', content: res.msg, okText: '我知道了' })
    }
  } catch (err) {
    const msg = err.response?.data?.msg || '删除失败，请稍后重试'
    Modal.error({ title: '无法删除', content: msg, okText: '我知道了' })
  }
}
</script>

<style scoped>
.group-list-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.group-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.group-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 6px;
  margin: 2px 4px;
  transition: background 0.2s;
}

.group-item:hover {
  background: #f0f0f0;
}

.group-item.active {
  background: #e6f4ff;
  color: #1677ff;
}

.group-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.group-name {
  font-size: 14px;
  font-weight: 500;
}

.group-count {
  font-size: 12px;
  color: #999;
}

.group-item.active .group-count {
  color: #69b1ff;
}

.more-btn {
  font-size: 16px;
  color: #999;
  padding: 4px;
  border-radius: 4px;
}

.more-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #333;
}

.add-btn-wrap {
  padding: 8px;
  border-top: 1px solid #f0f0f0;
}

.danger-text {
  color: #ff4d4f;
}
</style>
