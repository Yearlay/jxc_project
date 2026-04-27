<template>
  <!-- POS 全屏模式 -->
  <PosPage v-if="posMode" @back="posMode = false" />

  <a-layout v-else class="home-layout">
    <!-- 左侧菜单 -->
    <a-layout-sider v-model:collapsed="collapsed" collapsible class="sider">
      <div class="logo">{{ collapsed ? 'JXC' : '进销存系统' }}</div>
      <div class="sider-menu-scroll">
        <SideMenu
          :menu-tree="menuTree"
          :default-selected-id="defaultMenuId"
          @menu-select="onMenuSelect"
        />
      </div>
    </a-layout-sider>

    <a-layout class="main-layout">
      <!-- 顶栏 -->
      <a-layout-header class="header">
        <a-button type="primary" class="pos-btn" @click="posMode = true">
          <ShopOutlined />POS 前台销售
        </a-button>
        <div class="user-area">
          <a-dropdown placement="bottomRight">
            <span class="user-dropdown-trigger">
              {{ userInfo.real_name || userInfo.username }}
              <DownOutlined style="font-size:12px; margin-left:4px" />
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item key="logout" @click="handleLogout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <!-- 内容区 -->
      <a-layout-content class="content">
        <div class="content-inner">
          <component :is="currentComponent" v-if="currentComponent" />
          <template v-else-if="currentMenu">
            <h2>{{ currentMenu }}</h2>
            <p>功能开发中...</p>
          </template>
          <template v-else>
            <a-empty description="请从左侧菜单选择功能" />
          </template>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined, ShopOutlined } from '@ant-design/icons-vue'
import SideMenu from '../components/SideMenu.vue'
import GroupManage from './GroupManage.vue'
import AreaManage from './AreaManage.vue'
import MemberTypeManage from './MemberTypeManage.vue'
import CustomerManage from './CustomerManage.vue'
import WarehouseManage from './WarehouseManage.vue'
import UserManage from './UserManage.vue'
import CompanyInfo from './CompanyInfo.vue'
import UnitManage from './UnitManage.vue'
import ManufacturerManage from './ManufacturerManage.vue'
import VehicleManage from './VehicleManage.vue'
import PaymentManage from './PaymentManage.vue'
import PurchaseStaffManage from './PurchaseStaffManage.vue'
import SalesStaffManage from './SalesStaffManage.vue'
import TerminalManage from './TerminalManage.vue'
import GoodsCategoryManage from './GoodsCategoryManage.vue'
import GoodsManage from './GoodsManage.vue'
import PosPage from './PosPage.vue'
import { getMenu } from '../api/menu'

// 菜单路径 → 组件 映射表（后续新增页面在此注册）
const COMPONENT_MAP = {
  '/goods/category':           GoodsCategoryManage,
  '/goods/list':               GoodsManage,
  '/customer':                 CustomerManage,
  '/system/user/role':         GroupManage,
  '/system/basic/area':        AreaManage,
  '/system/basic/member-type': MemberTypeManage,
  '/system/basic/warehouse':   WarehouseManage,
  '/system/user/manage':        UserManage,
  '/system/company':             CompanyInfo,
  '/system/basic/unit':         UnitManage,
  '/system/basic/manufacturer': ManufacturerManage,
  '/system/basic/vehicle':      VehicleManage,
  '/system/basic/payment':      PaymentManage,
  '/system/basic/purchase-staff': PurchaseStaffManage,
  '/system/basic/sales-staff':    SalesStaffManage,
  '/system/basic/branch':         TerminalManage,

}

const router = useRouter()
const posMode = ref(false)
const collapsed = ref(false)
const menuTree = ref([])
const currentMenuId = ref(null)
const currentMenu = ref('')
const currentPath = ref('')

const currentComponent = computed(() => COMPONENT_MAP[currentPath.value] || null)

// 默认进入：系统维护 -> 设置企业信息（在菜单中查找）
const defaultMenuId = ref(null)

const userInfo = reactive(
  JSON.parse(localStorage.getItem('userInfo') || '{}')
)

onMounted(async () => {
  try {
    const res = await getMenu()
    if (res.code === 200) {
      menuTree.value = res.data
      // 找到 "设置企业信息" 的 id
      for (const m of res.data) {
        for (const c of m.children || []) {
          if (c.name === '设置企业信息') {
            defaultMenuId.value = c.id
            currentMenu.value = c.name
            currentPath.value = c.path || ''
            return
          }
          for (const leaf of c.children || []) {
            if (leaf.name === '设置企业信息') {
              defaultMenuId.value = leaf.id
              currentMenu.value = leaf.name
              currentPath.value = leaf.path || ''
              return
            }
          }
        }
      }
    }
  } catch {
    message.error('获取菜单失败')
  }
})

function onMenuSelect(id) {
  const findNode = (tree, targetId) => {
    for (const node of tree) {
      if (node.id === targetId) return node
      if (node.children) {
        const found = findNode(node.children, targetId)
        if (found) return found
      }
    }
    return null
  }
  const node = findNode(menuTree.value, id)
  if (node) {
    currentMenu.value = node.name
    currentPath.value = node.path || ''
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  message.success('已退出登录')
  router.replace('/login')
}
</script>

<style scoped>
.home-layout {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
  white-space: nowrap;
}
.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
.pos-btn {
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 6px;
}
.user-area {
  display: flex;
  align-items: center;
}
.user-dropdown-trigger {
  cursor: pointer;
  color: #003a8c;
  display: flex;
  align-items: center;
  gap: 4px;
}
.user-dropdown-trigger:hover {
  color: #1677ff;
}
.sider {
  height: 100vh;
  position: sticky;
  top: 0;
  left: 0;
  overflow: hidden;
}

.main-layout {
  height: 100vh;
  min-width: 0;
  width: 0;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sider-menu-scroll {
  height: calc(100vh - 64px - 48px); /* 减去 logo 高度和 collapse 触发器高度 */
  overflow-y: auto;
  overflow-x: hidden;
}
.sider-menu-scroll::-webkit-scrollbar {
  width: 4px;
}
.sider-menu-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}
.content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  margin: 16px;
}
.content-inner {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  height: 100%;
  padding: 24px;
  background: #fff;
  min-height: 360px;
  border-radius: 4px;
  box-sizing: border-box;
  overflow: hidden;
}
</style>
