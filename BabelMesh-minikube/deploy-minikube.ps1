# ===================================================================
# Minikube部署脚本 - Windows PowerShell
# VPN代理Web应用微服务部署
# ===================================================================

Write-Host "🚀 开始部署VPN代理Web应用到Minikube..." -ForegroundColor Green

# ===================================================================
# 第一步：检查环境
# ===================================================================
Write-Host "`n📋 检查环境..." -ForegroundColor Yellow

# 检查Minikube状态
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Minikube未运行，正在启动..." -ForegroundColor Red
    minikube start --driver=docker --memory=4096 --cpus=2
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Minikube启动失败！" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Minikube已运行" -ForegroundColor Green
}

# 配置Docker环境使用Minikube的Docker daemon
Write-Host "🔧 配置Docker环境..." -ForegroundColor Yellow
& minikube docker-env | Invoke-Expression

# ===================================================================
# 第二步：构建Docker镜像
# ===================================================================
Write-Host "`n🏗️ 构建Docker镜像..." -ForegroundColor Yellow

# 构建后端镜像
Write-Host "📦 构建后端镜像..." -ForegroundColor Cyan
docker build -f Dockerfile.backend -t vpn-backend:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 后端镜像构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 后端镜像构建成功" -ForegroundColor Green

# 构建前端镜像
Write-Host "📦 构建前端镜像..." -ForegroundColor Cyan
docker build -f Dockerfile.frontend -t vpn-frontend:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 前端镜像构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 前端镜像构建成功" -ForegroundColor Green

# ===================================================================
# 第三步：部署Kubernetes资源
# ===================================================================
Write-Host "`n☸️ 部署Kubernetes资源..." -ForegroundColor Yellow

# 创建命名空间
Write-Host "🏷️ 创建命名空间..." -ForegroundColor Cyan
kubectl apply -f k8s/namespace.yaml
Start-Sleep -Seconds 2

# 部署ConfigMap
Write-Host "⚙️ 部署配置文件..." -ForegroundColor Cyan
kubectl apply -f k8s/nginx-configmap.yaml

# 部署Redis服务
Write-Host "🗃️ 部署Redis缓存服务..." -ForegroundColor Cyan
kubectl apply -f k8s/redis-deployment.yaml
Start-Sleep -Seconds 5

# 部署后端服务
Write-Host "🔧 部署后端服务..." -ForegroundColor Cyan
kubectl apply -f k8s/backend-deployment.yaml
Start-Sleep -Seconds 10

# 部署前端服务
Write-Host "🎨 部署前端服务..." -ForegroundColor Cyan
kubectl apply -f k8s/frontend-deployment.yaml
Start-Sleep -Seconds 10

# 部署外部服务和HPA
Write-Host "🌐 部署外部服务和自动扩展..." -ForegroundColor Cyan
kubectl apply -f k8s/services-hpa.yaml

# ===================================================================
# 第四步：等待服务就绪
# ===================================================================
Write-Host "`n⏳ 等待服务就绪..." -ForegroundColor Yellow

# 等待Pod就绪
Write-Host "📊 检查Pod状态..." -ForegroundColor Cyan
kubectl wait --for=condition=ready pod -l app=redis -n vpn-proxy --timeout=60s
kubectl wait --for=condition=ready pod -l app=vpn-backend -n vpn-proxy --timeout=120s
kubectl wait --for=condition=ready pod -l app=vpn-frontend -n vpn-proxy --timeout=60s

# ===================================================================
# 第五步：显示部署信息
# ===================================================================
Write-Host "`n📊 部署完成！服务信息如下：" -ForegroundColor Green

# 获取Minikube IP
$minikubeIP = minikube ip

Write-Host "`n🌐 访问地址：" -ForegroundColor Yellow
Write-Host "   前端Web界面: http://$($minikubeIP):30080" -ForegroundColor White
Write-Host "   代理服务端口: $($minikubeIP):30888" -ForegroundColor White

Write-Host "`n📋 服务状态：" -ForegroundColor Yellow
kubectl get pods -n vpn-proxy -o wide
kubectl get services -n vpn-proxy

Write-Host "`n🔍 常用命令：" -ForegroundColor Yellow
Write-Host "   查看日志: kubectl logs -f deployment/backend-deployment -n vpn-proxy" -ForegroundColor White
Write-Host "   查看Pod: kubectl get pods -n vpn-proxy" -ForegroundColor White
Write-Host "   进入Pod: kubectl exec -it <pod-name> -n vpn-proxy -- /bin/bash" -ForegroundColor White
Write-Host "   删除部署: kubectl delete namespace vpn-proxy" -ForegroundColor White

Write-Host "`n🎉 部署完成！" -ForegroundColor Green
