<template>
  <div class="pos-page">
    <!-- 顶栏 -->
    <div class="pos-header">
      <a-button type="text" class="back-btn" @click="$emit('back')">
        <ArrowLeftOutlined />返回后台
      </a-button>
      <span class="pos-title">POS 前台销售</span>
      <div class="pos-header-right">
        <span class="pos-user">{{ userInfo.real_name || userInfo.username }}</span>
      </div>
    </div>

    <!-- 主体占位 -->
    <div class="pos-body">
      <a-empty description="POS 前台销售功能开发中..." />
    </div>
  </div>
</template>

<script setup>
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import { reactive } from 'vue'

defineEmits(['back'])

const userInfo = reactive(
  JSON.parse(localStorage.getItem('userInfo') || '{}')
)
</script>

<style scoped>
.pos-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}
.pos-header {
  height: 64px;
  background: #001529;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}
.back-btn {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.back-btn:hover {
  color: #fff !important;
  background: rgba(255, 255, 255, 0.1) !important;
}
.pos-title {
  flex: 1;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}
.pos-header-right {
  min-width: 80px;
  text-align: right;
}
.pos-user {
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
}
.pos-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
