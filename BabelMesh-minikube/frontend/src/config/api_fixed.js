// filepath: c:\Users\20399\Desktop\VPN\frontend\src\config\api.js
// ===================================================================
// API配置文件 - 环境相关的API端点配置
// 支持开发环境和生产环境的不同配置
// ===================================================================

// 获取当前环境
const isDevelopment = import.meta.env.MODE === 'development'
const isProduction = import.meta.env.MODE === 'production'

// API基础配置
export const API_CONFIG = {
  // 基础URL配置
  BASE_URL: isDevelopment 
    ? 'http://localhost:5000'  // 开发环境：直连后端
    : '/api',                  // 生产环境：通过Nginx代理

  // WebSocket配置
  WEBSOCKET_URL: isDevelopment
    ? 'http://localhost:5000'  // 开发环境：直连WebSocket
    : window.location.origin,  // 生产环境：使用当前域名

  // 请求超时配置
  TIMEOUT: 10000, // 10秒

  // 重试配置
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1秒

  // API端点定义
  ENDPOINTS: {
    // 代理管理
    PROXY_STATUS: '/api/proxy/status',
    PROXY_START: '/api/proxy/start',
    PROXY_STOP: '/api/proxy/stop',
    PROXY_TEST: '/api/proxy/test',
    
    // IP检测
    IP_CHECK: '/api/ip/check',
    IP_DETAILS: '/api/ip/details',
    
    // 连接监控
    CONNECTIONS: '/api/connections',
    
    // 健康检查
    HEALTH: '/health',
    READY: '/ready'
  }
}

// 环境信息
export const ENV_INFO = {
  NODE_ENV: import.meta.env.MODE,
  DEV: isDevelopment,
  PROD: isProduction,
  BASE_URL: window.location.origin,
  BUILD_TIME: new Date().toISOString()
}

// HTTP状态码定义
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
}

// 通用HTTP请求配置
export const REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: API_CONFIG.TIMEOUT
}

// API响应状态定义
export const API_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error',
  LOADING: 'loading',
  IDLE: 'idle'
}

// 日志级别
export const LOG_LEVELS = {
  ERROR: 'error',
  WARN: 'warn',
  INFO: 'info',
  DEBUG: 'debug'
}

// 导出默认配置
export default API_CONFIG
