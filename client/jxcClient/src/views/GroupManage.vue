<template>
  <div class="group-manage">
    <!-- 左侧权限组列表 -->
    <div class="left-panel">
      <GroupList ref="groupListRef" @select="onGroupSelect" />
    </div>

    <!-- 右侧内容区 -->
    <div class="right-panel">
      <a-empty v-if="!currentGroup" description="请选择左侧权限组" style="margin-top:80px" />

      <a-tabs v-else v-model:activeKey="activeTab">
        <!-- ── Tab 1：权限配置 ────────────────────── -->
        <a-tab-pane key="perms" tab="权限配置">
          <a-alert
            v-if="isAdminGroup"
            message="管理员组拥有全部权限，不可修改"
            type="info"
            show-icon
            style="margin-bottom:12px"
          />
          <div v-if="!isAdminGroup" class="perms-toolbar">
            <a-checkbox :checked="isAllChecked" :indeterminate="isIndeterminate" @change="toggleAll">
              全选
            </a-checkbox>
          </div>
          <a-spin :spinning="permsLoading">
            <a-tree
              v-model:checkedKeys="checkedMenuIds"
              checkable
              :disabled="isAdminGroup"
              :tree-data="menuTreeData"
              default-expand-all
              class="perm-tree"
            />
          </a-spin>
          <!-- 常显底部保存按鈕 -->
          <div v-if="!isAdminGroup" class="perms-footer">
            <a-button type="primary" :loading="saveMenuLoading" @click="saveMenus">
              <SaveOutlined />保存配置
            </a-button>
          </div>
        </a-tab-pane>

        <!-- ── Tab 2：成员管理 ────────────────────── -->
        <a-tab-pane key="members" tab="成员管理">
          <div class="members-toolbar">
            <a-button type="primary" @click="openAddMember">
              <UserAddOutlined />添加成员
            </a-button>
            <a-button
              v-if="selectedMember"
              danger
              @click="confirmRemove"
            >
              <UserDeleteOutlined />移除成员
            </a-button>
          </div>
          <a-spin :spinning="membersLoading">
            <div class="member-list">
              <div
                v-for="m in members"
                :key="m.id"
                class="member-item"
                :class="{ active: m.id === selectedMember?.id }"
                @click="selectMember(m)"
              >
                <a-avatar :size="36" style="background:#1677ff;flex-shrink:0">
                  {{ (m.real_name || m.username).slice(0, 1) }}
                </a-avatar>
                <div class="member-info">
                  <span class="member-name">{{ m.real_name || m.username }}</span>
                  <span class="member-username">@{{ m.username }}</span>
                </div>
              </div>
              <a-empty v-if="!members.length" description="暂无成员" style="margin-top:40px" />
            </div>
          </a-spin>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 添加成员 Modal -->
    <a-modal
      v-model:open="addMemberVisible"
      title="添加成员"
      ok-text="确定"
      cancel-text="取消"
      :confirm-loading="addMemberLoading"
      @ok="doAddMember"
    >
      <a-input-search
        v-model:value="userSearch"
        placeholder="搜索用户名或姓名"
        style="margin-bottom:12px;margin-top:8px"
      />
      <div class="user-select-list">
        <div
          v-for="u in filteredUsers"
          :key="u.id"
          class="user-select-item"
          :class="{ selected: u.id === addMemberTarget?.id }"
          @click="addMemberTarget = u"
        >
          <a-avatar :size="32" style="background:#52c41a;flex-shrink:0">
            {{ (u.real_name || u.username).slice(0, 1) }}
          </a-avatar>
          <div class="member-info">
            <span class="member-name">{{ u.real_name || u.username }}</span>
            <span class="member-username">@{{ u.username }}</span>
          </div>
          <CheckCircleFilled v-if="u.id === addMemberTarget?.id" class="check-icon" />
        </div>
        <a-empty v-if="!filteredUsers.length" description="无可添加的用户" />
      </div>
    </a-modal>

    <!-- 移除成员确认 -->
    <a-modal
      v-model:open="removeConfirmVisible"
      title="移除成员"
      ok-text="确定移除"
      ok-type="danger"
      cancel-text="取消"
      :confirm-loading="removeMemberLoading"
      @ok="doRemoveMember"
    >
      <p>确定将 <b>{{ selectedMember?.real_name || selectedMember?.username }}</b> 从「{{ currentGroup?.name }}」中移除？</p>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  SaveOutlined,
  UserAddOutlined,
  UserDeleteOutlined,
  CheckCircleFilled,
} from '@ant-design/icons-vue'
import GroupList from '../components/GroupList.vue'
import { getGroupMenus, saveGroupMenus, getGroupMembers, addGroupMember, removeGroupMember } from '../api/group'
import { getUserList } from '../api/user'
import { getMenu } from '../api/menu'

const groupListRef = ref(null)
const currentGroup = ref(null)
const activeTab = ref('perms')

// 管理员组不可编辑
const isAdminGroup = computed(() => currentGroup.value?.name === '管理员')

// ── 权限配置 ──────────────────────────────────────────────
const permsLoading = ref(false)
const saveMenuLoading = ref(false)
const checkedMenuIds = ref([])   // a-tree 标准模式：纯数组（仅含叶子节点 key）
const menuTreeData = ref([])
const allMenuIds = ref([])    // 全部节点 id
const leafMenuIds = ref([])   // 仅叶子节点 id（用于保存 / 全选判断）

// 构建 a-tree 格式，分别收集全部 id 和叶子 id
function buildTreeData(nodes) {
  const allIds = []
  const leafIds = []
  const build = (list) => list.map(n => {
    allIds.push(n.id)
    const hasChildren = n.children?.length > 0
    if (!hasChildren) leafIds.push(n.id)
    return {
      title: n.name,
      key: n.id,
      children: hasChildren ? build(n.children) : undefined,
    }
  })
  const data = build(nodes)
  return { data, allIds, leafIds }
}

async function loadMenuTree() {
  const res = await getMenu()
  if (res.code === 200) {
    const { data, allIds, leafIds } = buildTreeData(res.data)
    menuTreeData.value = data
    allMenuIds.value = allIds
    leafMenuIds.value = leafIds
  }
}
loadMenuTree()

async function loadGroupMenus(groupId) {
  permsLoading.value = true
  try {
    const res = await getGroupMenus(groupId)
    if (res.code === 200) {
      // 后端存的是叶子节点 id，a-tree 非 checkStrictly 模式只需传叶子节点即可自动勾选父节点
      checkedMenuIds.value = res.data.filter(id => leafMenuIds.value.includes(id))
    }
  } finally {
    permsLoading.value = false
  }
}

const isAllChecked = computed(
  () => leafMenuIds.value.length > 0 && checkedMenuIds.value.length === leafMenuIds.value.length
)
const isIndeterminate = computed(
  () => checkedMenuIds.value.length > 0 && !isAllChecked.value
)

function toggleAll(e) {
  checkedMenuIds.value = e.target.checked ? [...leafMenuIds.value] : []
}

async function saveMenus() {
  saveMenuLoading.value = true
  try {
    // checkedMenuIds 是叶子节点 id 数组，保存时一并计算出被勾选的父节点 id
    const checkedSet = new Set(checkedMenuIds.value)
    const allCheckedIds = allMenuIds.value.filter(id => {
      // 叶子节点直接判断
      if (leafMenuIds.value.includes(id)) return checkedSet.has(id)
      // 父节点：其所有叶子后代中至少有一个被勾选才算选中
      return false  // 父节点由后端不需要，只传叶子
    })
    const res = await saveGroupMenus({
      group_id: currentGroup.value.id,
      menu_ids: checkedMenuIds.value,  // 只传叶子节点 id
    })
    if (res.code === 200) {
      message.success('保存成功')
    } else {
      message.error(res.msg)
    }
  } finally {
    saveMenuLoading.value = false
  }
}

// ── 成员管理 ──────────────────────────────────────────────
const membersLoading = ref(false)
const members = ref([])
const selectedMember = ref(null)

async function loadMembers(groupId) {
  membersLoading.value = true
  selectedMember.value = null
  try {
    const res = await getGroupMembers(groupId)
    if (res.code === 200) {
      members.value = res.data
    }
  } finally {
    membersLoading.value = false
  }
}

function selectMember(m) {
  selectedMember.value = m.id === selectedMember.value?.id ? null : m
}

// 添加成员
const addMemberVisible = ref(false)
const addMemberLoading = ref(false)
const addMemberTarget = ref(null)
const userSearch = ref('')
const allUsers = ref([])

const filteredUsers = computed(() => {
  const existIds = new Set(members.value.map(m => m.id))
  return allUsers.value.filter(u => {
    if (existIds.has(u.id)) return false
    const kw = userSearch.value.trim().toLowerCase()
    if (!kw) return true
    return u.username.toLowerCase().includes(kw) || u.real_name.toLowerCase().includes(kw)
  })
})

async function openAddMember() {
  addMemberTarget.value = null
  userSearch.value = ''
  const res = await getUserList()
  if (res.code === 200) allUsers.value = res.data
  addMemberVisible.value = true
}

async function doAddMember() {
  if (!addMemberTarget.value) {
    message.warning('请选择要添加的用户')
    return
  }
  addMemberLoading.value = true
  try {
    const res = await addGroupMember({
      group_id: currentGroup.value.id,
      user_id: addMemberTarget.value.id,
    })
    if (res.code === 200) {
      message.success('添加成功')
      addMemberVisible.value = false
      await loadMembers(currentGroup.value.id)
      groupListRef.value?.loadGroups()  // 刷新成员数
    } else {
      message.error(res.msg)
    }
  } finally {
    addMemberLoading.value = false
  }
}

// 移除成员
const removeConfirmVisible = ref(false)
const removeMemberLoading = ref(false)

function confirmRemove() {
  removeConfirmVisible.value = true
}

async function doRemoveMember() {
  removeMemberLoading.value = true
  try {
    const res = await removeGroupMember({
      group_id: currentGroup.value.id,
      user_id: selectedMember.value.id,
    })
    if (res.code === 200) {
      message.success('移除成功')
      removeConfirmVisible.value = false
      await loadMembers(currentGroup.value.id)
      groupListRef.value?.loadGroups()  // 刷新成员数
    } else {
      message.error(res.msg)
    }
  } finally {
    removeMemberLoading.value = false
  }
}

// ── 切换权限组 ────────────────────────────────────────────
function onGroupSelect(group) {
  currentGroup.value = group
  if (group) {
    loadGroupMenus(group.id)
    loadMembers(group.id)
  }
}

// tab 切换时不需额外处理，数据已加载
</script>

<style scoped>
.group-manage {
  display: flex;
  height: calc(100vh - 180px);
  min-height: 500px;
  gap: 0;
}

.left-panel {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.right-panel {
  flex: 1;
  padding: 0 20px;
  overflow-y: auto;
}

/* 权限配置 */
.perms-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 4px 0;
}

.perm-tree {
  background: transparent;
  padding-bottom: 60px; /* 留出底部 footer 高度，防止树内容被遮挡 */
}

.perms-footer {
  position: sticky;
  bottom: 0;
  background: #fff;
  padding: 10px 0 6px;
  border-top: 1px solid #f0f0f0;
  z-index: 10;
}

/* 成员管理 */
.members-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  border: 1px solid transparent;
}

.member-item:hover {
  background: #f5f5f5;
}

.member-item.active {
  background: #e6f4ff;
  border-color: #91caff;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
}

.member-username {
  font-size: 12px;
  color: #999;
}

/* 添加成员弹窗 */
.user-select-list {
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-select-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
  position: relative;
}

.user-select-item:hover {
  background: #f5f5f5;
}

.user-select-item.selected {
  background: #e6f4ff;
  border-color: #91caff;
}

.check-icon {
  position: absolute;
  right: 12px;
  color: #1677ff;
  font-size: 16px;
}
</style>
