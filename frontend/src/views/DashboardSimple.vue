<template>
  <div class="dashboard">
    <h2>Dashboard 测试</h2>
    <p>如果你能看到这个文字，说明路由正常工作</p>
    
    <el-card>
      <template #header>
        <span>简单测试</span>
      </template>
      <el-button type="primary">测试按钮</el-button>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'DashboardSimple',
  setup() {
    return {}
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
</style>
