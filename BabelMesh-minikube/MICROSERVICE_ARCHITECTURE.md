# 📁 VPN代理Web应用 - 微服务架构说明

## 🗂️ 文件关系图

```
VPN代理Web应用
├── 🐳 Docker构建文件
│   ├── Dockerfile.backend      # 后端服务镜像构建
│   ├── Dockerfile.frontend     # 前端服务镜像构建
│   ├── Dockerfile              # 单体应用镜像（已弃用）
│   └── docker-compose.yml      # 单体部署配置（已弃用）
│
├── ☸️ Kubernetes部署文件
│   ├── k8s/namespace.yaml           # 命名空间定义
│   ├── k8s/backend-deployment.yaml  # 后端服务部署
│   ├── k8s/frontend-deployment.yaml # 前端服务部署
│   ├── k8s/redis-deployment.yaml    # Redis缓存部署
│   ├── k8s/nginx-configmap.yaml     # Nginx配置文件
│   └── k8s/services-hpa.yaml        # 外部服务和自动扩展
│
├── 🚀 部署脚本
│   ├── deploy-minikube.ps1     # 自动化部署脚本
│   └── cleanup-minikube.ps1    # 自动化清理脚本
│
├── 📖 文档
│   ├── DEPLOY_TO_MINIKUBE.md   # Minikube部署指南
│   ├── DEPLOY_TO_CLOUD.md      # 云部署指南（待编写）
│   └── README.md               # 项目总览
│
├── 🔧 应用代码
│   ├── backend/                # 后端Python代码
│   └── frontend/               # 前端Vue.js代码
│
└── ⚙️ 配置文件
    ├── backend/requirements.txt # Python依赖
    └── nginx.conf              # Nginx配置（已弃用）
```

## 🏗️ Docker文件关系

### 1. **Dockerfile.backend** (后端专用)
- **作用**: 构建后端Flask API服务镜像
- **包含**: Python运行时 + Flask应用 + 代理服务器
- **暴露端口**: 5000 (API), 8888 (代理)
- **用途**: 微服务架构中的后端服务

### 2. **Dockerfile.frontend** (前端专用)  
- **作用**: 构建前端Nginx静态文件服务镜像
- **包含**: Vue.js构建产物 + Nginx Web服务器
- **暴露端口**: 80 (HTTP)
- **用途**: 微服务架构中的前端服务

### 3. **Dockerfile** (单体应用)
- **作用**: 构建包含前后端的单体应用镜像
- **包含**: 前端构建 + 后端运行时 + 完整应用
- **状态**: 已弃用，建议使用微服务架构

### 4. **docker-compose.yml** (单体部署)
- **作用**: Docker Compose单体应用部署
- **状态**: 已弃用，建议使用Kubernetes部署

## ☸️ Kubernetes架构

### 微服务组件分工

| 组件 | 镜像 | 端口 | 职责 |
|------|------|------|------|
| **Frontend** | vpn-frontend:latest | 80 | 静态文件服务、API代理 |
| **Backend** | vpn-backend:latest | 5000, 8888 | API服务、代理服务器 |
| **Redis** | redis:7-alpine | 6379 | 缓存、会话存储 |

### 服务通信架构

```
外部用户 
    ↓ (NodePort:30080)
前端服务 (Nginx)
    ↓ (API请求代理)
后端服务 (Flask)
    ↓ (缓存读写)
Redis服务
```

### 网络访问方式

- **前端访问**: NodePort 30080 → Frontend:80
- **API访问**: 通过前端Nginx代理 → Backend:5000  
- **代理服务**: NodePort 30888 → Backend:8888
- **Redis**: ClusterIP，仅内部访问

## 🚀 部署流程

### 构建阶段
1. **构建后端镜像**: `docker build -f Dockerfile.backend -t vpn-backend:latest .`
2. **构建前端镜像**: `docker build -f Dockerfile.frontend -t vpn-frontend:latest .`

### 部署阶段
1. **创建命名空间**: `kubectl apply -f k8s/namespace.yaml`
2. **部署配置**: `kubectl apply -f k8s/nginx-configmap.yaml`
3. **部署缓存**: `kubectl apply -f k8s/redis-deployment.yaml`
4. **部署后端**: `kubectl apply -f k8s/backend-deployment.yaml`
5. **部署前端**: `kubectl apply -f k8s/frontend-deployment.yaml`
6. **配置服务**: `kubectl apply -f k8s/services-hpa.yaml`

## 🔄 各文件在构建中的作用

### 🏗️ 镜像构建角色

| 文件 | 阶段 | 作用 | 输出 |
|------|------|------|------|
| **Dockerfile.backend** | Build | 构建后端服务镜像 | vpn-backend:latest |
| **Dockerfile.frontend** | Build | 构建前端服务镜像 | vpn-frontend:latest |

### ☸️ Kubernetes部署角色

| 文件 | 阶段 | 作用 | 资源 |
|------|------|------|------|
| **namespace.yaml** | 1st | 创建隔离命名空间 | Namespace |
| **nginx-configmap.yaml** | 2nd | 配置Nginx | ConfigMap |
| **redis-deployment.yaml** | 3rd | 部署缓存服务 | Deployment + Service |
| **backend-deployment.yaml** | 4th | 部署后端服务 | Deployment + Service |
| **frontend-deployment.yaml** | 5th | 部署前端服务 | Deployment + Service |
| **services-hpa.yaml** | 6th | 外部访问和扩展 | NodePort + HPA |

### 🚀 自动化脚本角色

| 文件 | 作用 | 功能 |
|------|------|------|
| **deploy-minikube.ps1** | 自动化部署 | 一键构建+部署+检查 |
| **cleanup-minikube.ps1** | 自动化清理 | 一键删除+清理 |

## 🎯 推荐使用方式

### ✅ 推荐：微服务架构
- 使用 `Dockerfile.backend` + `Dockerfile.frontend`
- 使用 Kubernetes YAML 配置文件
- 使用 `deploy-minikube.ps1` 自动化部署

### ❌ 不推荐：单体架构  
- 避免使用 `Dockerfile` 单体构建
- 避免使用 `docker-compose.yml` 单体部署

### 🗑️ 可删除文件
- `Dockerfile` (单体应用)
- `docker-compose.yml` (单体部署)
- `nginx.conf` (独立配置文件)
- `DEPLOY_TO_CLOUD.md` (空文件)
- `requirements.txt` (根目录，已移至backend/)

## 🔧 故障排除

如果部署失败，按以下顺序检查：

1. **Minikube状态**: `minikube status`
2. **Docker环境**: `minikube docker-env | Invoke-Expression`  
3. **镜像构建**: `docker images | Select-String vpn`
4. **Pod状态**: `kubectl get pods -n vpn-proxy`
5. **服务状态**: `kubectl get services -n vpn-proxy`
6. **日志检查**: `kubectl logs -f deployment/backend-deployment -n vpn-proxy`
