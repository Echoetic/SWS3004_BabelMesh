# ===================================================================
# Minikube卸载脚本 - Windows PowerShell
# 清理VPN代理Web应用部署
# ===================================================================

Write-Host "🧹 开始清理VPN代理Web应用..." -ForegroundColor Yellow

# 删除所有资源
Write-Host "🗑️ 删除Kubernetes资源..." -ForegroundColor Cyan
kubectl delete namespace vpn-proxy

# 清理Docker镜像（可选）
$cleanup = Read-Host "是否清理本地Docker镜像？(y/N)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Write-Host "🧹 清理Docker镜像..." -ForegroundColor Cyan
    
    # 配置Docker环境
    & minikube docker-env | Invoke-Expression
    
    # 删除镜像
    docker rmi vpn-backend:latest -f 2>$null
    docker rmi vpn-frontend:latest -f 2>$null
    
    # 清理未使用的镜像
    docker image prune -f
    
    Write-Host "✅ Docker镜像清理完成" -ForegroundColor Green
}

Write-Host "✅ 清理完成！" -ForegroundColor Green
