<template>
  <div class="login-container">
    <a-card class="login-card" title="进销存系统">
      <a-form :model="form" @finish="handleLogin" layout="vertical">
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading">
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { login } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    const res = await login(form)
    if (res.code === 200) {
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify({
        username: res.data.username,
        real_name: res.data.real_name,
        role: res.data.role,
      }))
      message.success('登录成功')
      router.replace('/home')
    } else {
      message.error(res.msg || '登录失败')
    }
  } catch (err) {
    if (err.response?.data?.msg) {
      message.error(err.response.data.msg)
    } else if (err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED') {
      message.error('无法连接到服务器，请检查后端服务是否启动')
    } else {
      message.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  width: 360px;
}
</style>
