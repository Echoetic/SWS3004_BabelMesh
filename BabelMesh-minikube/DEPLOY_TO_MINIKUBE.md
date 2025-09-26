# 🚀 VPN代理Web应用 - Minikube微服务部署指南

## 📋 架构概述

本项目采用微服务架构，包含以下组件：

### 🏗️ 微服务组件
```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube集群                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              vpn-proxy命名空间                      │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │    │
│  │  │   前端服务    │  │   后端服务    │  │  Redis   │  │    │
│  │  │              │  │              │  │          │  │    │
│  │  │ Vue.js + Nginx│  │Flask API +   │  │  缓存    │  │    │
│  │  │   :80        │  │Proxy Server  │  │  :6379   │  │    │
│  │  │              │  │  :5000:8888  │  │          │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │    │
│  │        │                   │              │        │    │
│  │   NodePort:30080      ClusterIP       ClusterIP   │    │
│  │                      NodePort:30888                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 🧩 服务说明
- **前端服务**: Vue.js SPA + Nginx反向代理
- **后端服务**: Flask API + 代理服务器 + WebSocket
- **Redis服务**: 会话存储和数据缓存
- **外部访问**: NodePort方式暴露服务

## 🛠️ 快速部署

### 方式一：自动化脚本部署（推荐）

```powershell
# 1. 执行部署脚本
.\deploy-minikube.ps1

# 2. 等待部署完成后访问
# 前端: http://<minikube-ip>:30080
# 代理: <minikube-ip>:30888
```

### 方式二：手动部署

```powershell
# 1. 启动Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# 2. 配置Docker环境
minikube docker-env | Invoke-Expression

# 3. 构建镜像
docker build -f Dockerfile.backend -t vpn-backend:latest .
docker build -f Dockerfile.frontend -t vpn-frontend:latest .

# 4. 部署Kubernetes资源
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/nginx-configmap.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/services-hpa.yaml

# 5. 检查部署状态
kubectl get pods -n vpn-proxy
```

## 📊 监控和管理

### 查看服务状态
```powershell
# 查看所有Pod
kubectl get pods -n vpn-proxy -o wide

# 查看服务
kubectl get services -n vpn-proxy

# 查看HPA状态
kubectl get hpa -n vpn-proxy
```

### 查看日志
```powershell
# 后端服务日志
kubectl logs -f deployment/backend-deployment -n vpn-proxy

# 前端服务日志
kubectl logs -f deployment/frontend-deployment -n vpn-proxy

# Redis日志
kubectl logs -f deployment/redis-deployment -n vpn-proxy
```

### 扩缩容管理
```powershell
# 手动扩展后端服务
kubectl scale deployment backend-deployment --replicas=3 -n vpn-proxy

# 手动扩展前端服务
kubectl scale deployment frontend-deployment --replicas=3 -n vpn-proxy
```

## 🔧 故障排除

### 常见问题

1. **Pod启动失败**
```powershell
# 查看Pod详细信息
kubectl describe pod <pod-name> -n vpn-proxy

# 查看事件
kubectl get events -n vpn-proxy --sort-by=.metadata.creationTimestamp
```

2. **镜像拉取失败**
```powershell
# 确保使用Minikube的Docker环境
minikube docker-env | Invoke-Expression

# 重新构建镜像
docker build -f Dockerfile.backend -t vpn-backend:latest .
```

3. **服务无法访问**
```powershell
# 检查服务端点
kubectl get endpoints -n vpn-proxy

# 检查网络策略
kubectl get networkpolicies -n vpn-proxy
```

## 🧹 清理部署

### 方式一：使用清理脚本
```powershell
.\cleanup-minikube.ps1
```

### 方式二：手动清理
```powershell
# 删除命名空间（会删除所有资源）
kubectl delete namespace vpn-proxy

# 清理Docker镜像
minikube docker-env | Invoke-Expression
docker rmi vpn-backend:latest vpn-frontend:latest
docker image prune -f
```

## 📝 配置文件说明

### Kubernetes配置文件
```
k8s/
├── namespace.yaml           # 命名空间定义
├── backend-deployment.yaml  # 后端服务部署
├── frontend-deployment.yaml # 前端服务部署
├── redis-deployment.yaml   # Redis缓存部署
├── nginx-configmap.yaml    # Nginx配置
└── services-hpa.yaml       # 外部服务和自动扩展
```

### Docker配置文件
```
├── Dockerfile.backend      # 后端服务镜像
├── Dockerfile.frontend     # 前端服务镜像
└── backend/requirements.txt # Python依赖
```

## 🌐 访问方式

部署完成后，通过以下方式访问：

- **Web管理界面**: `http://<minikube-ip>:30080`
- **API接口**: `http://<minikube-ip>:30080/api/`
- **代理服务**: `<minikube-ip>:30888`
- **健康检查**: `http://<minikube-ip>:30080/health`

获取Minikube IP：
```powershell
minikube ip
```