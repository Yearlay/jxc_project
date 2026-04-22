<template>
  <div class="page-container">
    <!-- 顶部提示 -->
    <a-alert
      type="info"
      show-icon
      message="请设置您的企业或门店的基本信息，这些信息会显示在您打印的单据上，请确保信息真实有效。"
      style="margin-bottom: 24px"
    />

    <!-- 表单 -->
    <a-form
      :model="form"
      layout="horizontal"
      :label-col="{ style: { width: '160px' } }"
      :wrapper-col="{ style: { maxWidth: '400px' } }"
    >
      <a-form-item label="企业/门店名称">
        <a-input
          v-model:value="form.name"
          placeholder="请输入企业或门店名称"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="企业/门店电话">
        <a-input
          v-model:value="form.phone"
          placeholder="请输入联系电话"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="企业/门店地址">
        <a-input
          v-model:value="form.address"
          placeholder="请输入详细地址"
          allow-clear
        />
      </a-form-item>
      <a-form-item :wrapper-col="{ style: { maxWidth: '400px', marginLeft: '160px' } }">
        <a-button
          type="primary"
          :disabled="!canSave"
          :loading="submitting"
          @click="handleSave"
        >
          保存
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, ref } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'

const form = reactive({ name: '', phone: '', address: '' })
const submitting = ref(false)

const canSave = computed(
  () => !!form.name?.trim() && !!form.phone?.trim() && !!form.address?.trim()
)

async function loadData() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/company/get', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.data.code === 200 && res.data.data) {
      const { name, phone, address } = res.data.data
      form.name = name || ''
      form.phone = phone || ''
      form.address = address || ''
    }
  } catch {
    // 忽略加载失败，保持空白
  }
}

async function handleSave() {
  submitting.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post(
      '/api/company/save',
      { name: form.name.trim(), phone: form.phone.trim(), address: form.address.trim() },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    if (res.data.code === 200) {
      message.success('保存成功')
    } else {
      message.error(res.data.msg || '保存失败')
    }
  } catch {
    message.error('网络错误，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  padding: 8px 0;
}
</style>
