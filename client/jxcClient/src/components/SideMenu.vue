<template>
  <a-menu
    v-model:selectedKeys="selectedKeys"
    v-model:openKeys="openKeys"
    mode="inline"
    :theme="theme"
    @click="onMenuClick"
  >
    <template v-for="item in menuTree" :key="item.id">
      <!-- 有子菜单 -->
      <a-sub-menu v-if="item.children && item.children.length" :key="item.id">
        <template #title>
          <component :is="getIcon(item.name)" />
          <span>{{ item.name }}</span>
        </template>
        <template v-for="child in item.children" :key="child.id">
          <!-- 三级 -->
          <a-sub-menu v-if="child.children && child.children.length" :key="child.id">
            <template #title>{{ child.name }}</template>
            <a-menu-item v-for="leaf in child.children" :key="leaf.id">
              {{ leaf.name }}
            </a-menu-item>
          </a-sub-menu>
          <!-- 二级叶节点 -->
          <a-menu-item v-else :key="child.id + '_leaf'">{{ child.name }}</a-menu-item>
        </template>
      </a-sub-menu>
      <!-- 一级叶节点 -->
      <a-menu-item v-else :key="item.id + '_leaf'">
        <component :is="getIcon(item.name)" />
        <span>{{ item.name }}</span>
      </a-menu-item>
    </template>
  </a-menu>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  DatabaseOutlined,
  ShoppingCartOutlined,
  TagOutlined,
  BarcodeOutlined,
  ContainerOutlined,
  AccountBookOutlined,
  BarChartOutlined,
  PieChartOutlined,
  SettingOutlined,
  TeamOutlined,
  AppstoreOutlined,
} from '@ant-design/icons-vue'

const ICON_MAP = {
  '基础档案': DatabaseOutlined,       // 数据库圆柱
  '采购管理': ShoppingCartOutlined,   // 购物车
  '销售管理': TagOutlined,            // 价格标签
  '商品管理': BarcodeOutlined,        // 条形码
  '库存管理': ContainerOutlined,      // 集装箱/仓库
  '财务管理': AccountBookOutlined,    // 账本
  '报表查询': BarChartOutlined,       // 柱状图
  '营业统计': PieChartOutlined,       // 饼图
  '系统维护': SettingOutlined,        // 齿轮
  '权限管理': TeamOutlined,           // 团队/人员
}

function getIcon(name) {
  return ICON_MAP[name] || AppstoreOutlined
}

const props = defineProps({
  menuTree: { type: Array, default: () => [] },
  theme: { type: String, default: 'dark' },
  defaultSelectedId: { type: Number, default: null },
})

const emit = defineEmits(['menuSelect'])

const selectedKeys = ref([])
const openKeys = ref([])

// 默认展开并选中指定菜单
watch(
  () => props.defaultSelectedId,
  (id) => {
    if (id) {
      selectedKeys.value = [id]
      // 找到父级，展开
      for (const m of props.menuTree) {
        for (const c of m.children || []) {
          if (c.id === id) {
            openKeys.value = [m.id]
            return
          }
          for (const leaf of c.children || []) {
            if (leaf.id === id) {
              openKeys.value = [m.id, c.id]
              return
            }
          }
        }
      }
    }
  },
  { immediate: true }
)

function onMenuClick({ key }) {
  // key 可能是数字（三级叶节点）或 "id_leaf" 字符串（二级叶节点），统一转为数字 id
  const id = typeof key === 'string' ? parseInt(key) : key
  emit('menuSelect', id)
}
</script>
