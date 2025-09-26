<template>
  <div class="dashboard">
    <!-- 控制面板 -->
    <el-row :gutter="20" class="control-panel">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span><el-icon><VideoPlay /></el-icon> 代理控制</span>
          </template>
          <div class="control-buttons">
            <el-button
              :type="proxyStatus.running ? 'danger' : 'success'"
              :icon="proxyStatus.running ? VideoPause : VideoPlay"
              @click="toggleProxy"
              :loading="loading"
              size="large"
            >
              {{ proxyStatus.running ? '停止代理' : '启动代理' }}
            </el-button>
            <el-button
              type="primary"
              :icon="Refresh"
              @click="testConnection"
              :loading="testing"
              size="large"
            >
              测试连接
            </el-button>
          </div>          <div class="config-section">
            <el-form-item label="代理类型:">
              <el-select
                v-model="proxyType"
                :disabled="proxyStatus.running"
                style="width: 140px;"
              >
                <el-option label="HTTP 代理" value="http" />
                <el-option label="SOCKS5 代理" value="socks5" />
              </el-select>
            </el-form-item>
            <el-form-item label="端口:">
              <el-input-number
                v-model="port"
                :min="1024"
                :max="65535"
                :disabled="proxyStatus.running"
              />
            </el-form-item>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span><el-icon><Monitor /></el-icon> 实时状态</span>
          </template>
          <el-row :gutter="20">            <el-col :span="5">
              <el-statistic
                title="代理类型"
                :value="proxyStatus.proxy_type ? proxyStatus.proxy_type.toUpperCase() : 'HTTP'"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="当前连接"
                :value="proxyStatus.connections"
                suffix="个"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="总流量"
                :value="formatBytes(proxyStatus.total_bytes)"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="运行端口"
                :value="proxyStatus.port"
              />
            </el-col>
            <el-col :span="4">
              <el-statistic
                title="运行时间"
                :value="uptime"
              />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 连接监控 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><Connection /></el-icon> 活跃连接</span>
          </template>
          <div class="connections-list">
            <el-empty v-if="activeConnections.length === 0" description="暂无活跃连接" />
            <div v-else>
              <div
                v-for="connection in activeConnections"
                :key="connection"
                class="connection-item"
              >
                <el-tag size="small">{{ connection }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><DataAnalysis /></el-icon> 流量图表</span>
          </template>
          <div class="chart-container">
            <v-chart :option="chartOption" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>      </el-row>
    
    <!-- 连接测试 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">        <el-card>
          <template #header>
            <span><el-icon><Link /></el-icon> 代理连接测试</span>
          </template>
          <div style="margin-bottom: 15px;">
            <el-alert
              title="测试说明"
              :description="getTestDescription()"
              type="info"
              show-icon
              :closable="false"
            />
          </div><el-form :model="testForm" inline>
            <el-form-item label="测试目标:">
              <el-select v-model="testForm.url" placeholder="选择测试目标" style="width: 300px;">
                <el-option label="httpbin.org (IP检测)" value="http://httpbin.org/ip" />
                <el-option label="Google (搜索引擎)" value="http://www.google.com" />
                <el-option label="百度 (搜索引擎)" value="http://www.baidu.com" />
                <el-option label="GitHub (代码托管)" value="https://github.com" />
                <el-option label="自定义URL" value="custom" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="testForm.url === 'custom'" label="自定义URL:">
              <el-input
                v-model="testForm.customUrl"
                placeholder="输入域名或完整URL (如: google.com 或 http://example.com)"
                style="width: 350px;"
              />
            </el-form-item>
            <el-form-item>              <el-button 
                type="primary" 
                @click="testConnection" 
                :loading="testing"
                :disabled="!proxyStatus.running"
              >
                {{ testing ? '测试中...' : `测试${(proxyStatus.proxy_type || 'HTTP').toUpperCase()}代理` }}
              </el-button>
            </el-form-item>
          </el-form>
          <div v-if="testResult" class="test-result" style="margin-top: 15px;">
            <el-alert
              :title="testResult.success ? '✅ 代理连接成功' : '❌ 代理连接失败'"
              :type="testResult.success ? 'success' : 'error'"
              :description="testResult.message"
              show-icon
            >
              <template v-if="testResult.success && testResult.details" #default>
                <div style="margin-top: 10px;">
                  <p><strong>响应时间:</strong> {{ testResult.details.response_time }}</p>
                  <p><strong>目标地址:</strong> {{ testResult.details.target }}</p>
                </div>
              </template>
            </el-alert>
          </div>
          <div v-if="!proxyStatus.running" style="margin-top: 15px;">
            <el-alert
              title="代理服务未运行"
              description="请先启动代理服务后再进行连接测试"
              type="warning"
              show-icon
              :closable="false"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Refresh, Monitor, Connection, DataAnalysis, Link } from '@element-plus/icons-vue'
import { io } from 'socket.io-client'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

export default {
  name: 'Dashboard',
  components: {
    VChart,
    VideoPlay,
    VideoPause,
    Refresh,
    Monitor,
    Connection,
    DataAnalysis,
    Link
  },
  setup() {    const proxyStatus = ref({
      running: false,
      port: 8888,
      proxy_type: 'http',
      connections: 0,
      total_bytes: 0,
      active_connections: [],
      start_time: null
    })

    const port = ref(8888)
    const proxyType = ref('http')
    const loading = ref(false)
    const testing = ref(false)
    const testForm = ref({ 
      url: 'http://httpbin.org/ip',
      customUrl: ''
    })
    const testResult = ref(null)
    const trafficData = ref([])
    const timeLabels = ref([])

    let socket = null
    let trafficInterval = null

    const activeConnections = computed(() => proxyStatus.value.active_connections || [])

    const uptime = computed(() => {
      if (!proxyStatus.value.start_time) return '未运行'
      const start = new Date(proxyStatus.value.start_time)
      const now = new Date()
      const diff = Math.floor((now - start) / 1000)
      const hours = Math.floor(diff / 3600)
      const minutes = Math.floor((diff % 3600) / 60)
      const seconds = diff % 60
      return `${hours}h ${minutes}m ${seconds}s`
    })

    const chartOption = computed(() => ({
      title: {
        text: '实时流量监控'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: timeLabels.value
      },
      yAxis: {
        type: 'value',
        name: '字节数'
      },
      series: [{
        name: '流量',
        type: 'line',
        data: trafficData.value,
        smooth: true
      }]
    }))

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getTestDescription = () => {
      const type = proxyStatus.value.proxy_type || 'HTTP'
      if (type === 'http') {
        return 'HTTP代理测试：验证代理服务器处理HTTP/HTTPS请求的能力，兼容所有主流浏览器'
      } else {
        return 'SOCKS5代理测试：验证SOCKS5代理服务器功能，支持更高级的网络转发'
      }
    }

    const toggleProxy = async () => {
      loading.value = true
      try {        const endpoint = proxyStatus.value.running ? '/api/proxy/stop' : '/api/proxy/start'
        const body = proxyStatus.value.running ? {} : { 
          port: port.value,
          proxy_type: proxyType.value
        }
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)        })

        const data = await response.json();
        if (response.ok) {
          proxyStatus.value = data.status;
          ElMessage.success(data.message);
        } else {
          ElMessage.error(data.error);
        }      } catch (error) {
        ElMessage.error('操作失败: ' + error.message);
      } finally {
        loading.value = false;
      }
    };

    const testConnection = async () => {
      if (!proxyStatus.value.running) {
        ElMessage.warning('请先启动代理服务')
        return
      }

      testing.value = true
      testResult.value = null
      
      try {
        let testUrl = testForm.value.url === 'custom' ? testForm.value.customUrl : testForm.value.url
        
        if (!testUrl) {
          ElMessage.error('请输入测试URL')
          testing.value = false
          return
        }

        // 如果是自定义URL，自动添加协议
        if (testForm.value.url === 'custom') {
          if (!testUrl.startsWith('http://') && !testUrl.startsWith('https://')) {
            testUrl = 'http://' + testUrl
          }
        }

        const response = await fetch('/api/proxy/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: testUrl })
        })

        const data = await response.json()
        
        if (data.success) {
          testResult.value = {
            success: true,
            message: data.message,
            details: {
              response_time: data.response_time,
              target: data.target
            }
          }
          ElMessage.success('代理测试成功！')
        } else {
          testResult.value = {
            success: false,
            message: data.error
          }
          ElMessage.error('代理测试失败')
        }
      } catch (error) {
        testResult.value = {
          success: false,
          message: '网络错误: ' + error.message
        }
        ElMessage.error('测试失败: ' + error.message)      } finally {
        testing.value = false;
      }
    };

    const updateTrafficChart = () => {      const now = new Date().toLocaleTimeString();
      trafficData.value.push(proxyStatus.value.total_bytes);
      timeLabels.value.push(now);

      // 只保留最近20个数据点
      if (trafficData.value.length > 20) {
        trafficData.value.shift();
        timeLabels.value.shift();
      }
    };

    const fetchProxyStatus = async () => {      try {
        const response = await fetch('/api/proxy/status');
        const data = await response.json();
        proxyStatus.value = data;
      } catch (error) {
        console.error('Failed to fetch proxy status:', error);
      }
    };    onMounted(() => {
      socket = io('http://localhost:5000');
      
      socket.on('proxy_stats', (data) => {
        proxyStatus.value = data;
      });

      socket.on('connect', () => {
        console.log('Connected to server');
        fetchProxyStatus();
      });

      socket.on('disconnect', () => {
        console.log('Disconnected from server');
      });      // 获取初始状态
      fetchProxyStatus();
      
      // 定期更新图表
      trafficInterval = setInterval(updateTrafficChart, 2000);
    });

    onUnmounted(() => {
      if (socket) socket.disconnect();
      if (trafficInterval) clearInterval(trafficInterval);
    });

    return {
      proxyStatus,
      port,
      loading,
      testing,
      testForm,
      testResult,
      activeConnections,
      uptime,
      chartOption,
      formatBytes,
      toggleProxy,
      testConnection,
      VideoPlay,
      VideoPause,
      Refresh
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.control-panel {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.control-buttons .el-button {
  flex: 1;
}

.connections-list {
  max-height: 300px;
  overflow-y: auto;
}

.connection-item {
  margin-bottom: 8px;
}

.test-result {
  margin-top: 15px;
}

.chart-container {
  height: 300px;
}
</style>
