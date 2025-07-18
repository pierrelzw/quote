#!/bin/bash

# GitHub Pages + Render 一键部署脚本

set -e

echo "🚀 开始部署到 GitHub Pages + Render..."

# 检查环境
check_environment() {
    echo "📋 检查部署环境..."
    
    # 检查是否在 Git 仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ 当前目录不是 Git 仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if ! git diff --quiet; then
        echo "⚠️ 有未提交的更改，将自动添加到提交中"
    fi
    
    echo "✅ 环境检查通过"
}

# 配置前端环境
configure_frontend() {
    echo "🔧 配置前端环境..."
    
    cd frontend
    
    # 检查是否有 .env.production 文件
    if [ ! -f ".env.production" ]; then
        echo "⚠️ 未找到 .env.production 文件"
        echo "请确保设置了正确的 VITE_API_BASE_URL"
        
        # 创建示例文件
        cat > .env.production << EOF
VITE_API_BASE_URL=https://your-render-backend.onrender.com
EOF
        echo "✅ 创建了示例 .env.production 文件，请根据实际情况修改"
    fi
    
    # 安装依赖
    if [ -f "package.json" ]; then
        echo "📦 安装前端依赖..."
        npm install
    fi
    
    # 测试构建
    echo "🔨 测试前端构建..."
    npm run build
    
    cd ..
    echo "✅ 前端配置完成"
}

# 配置后端环境
configure_backend() {
    echo "🔧 配置后端环境..."
    
    cd backend-python
    
    # 检查生产依赖
    if [ ! -f "requirements_prod.txt" ]; then
        echo "❌ 未找到 requirements_prod.txt"
        exit 1
    fi
    
    # 测试后端启动
    echo "🧪 测试后端配置..."
    python3 -c "
import app
print('✅ 后端配置检查通过')
"
    
    cd ..
    echo "✅ 后端配置完成"
}

# 部署到 GitHub
deploy_to_github() {
    echo "📤 部署到 GitHub..."
    
    # 添加所有更改
    git add .
    
    # 提交更改
    commit_message="Deploy to GitHub Pages + Render - $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_message" || echo "没有新的更改需要提交"
    
    # 推送到 GitHub
    git push origin main
    
    echo "✅ 代码已推送到 GitHub"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 部署准备完成！"
    echo "==================="
    echo ""
    echo "📋 接下来的步骤："
    echo ""
    echo "1. 🎨 后端部署 (Render):"
    echo "   - 访问 https://render.com"
    echo "   - 连接 GitHub 仓库"
    echo "   - 创建 Web Service"
    echo "   - 选择 backend-python 目录"
    echo "   - 设置构建命令: pip install -r requirements_prod.txt"
    echo "   - 设置启动命令: gunicorn -w 4 -b 0.0.0.0:\$PORT app:app"
    echo "   - 设置环境变量："
    echo "     * JWT_SECRET_KEY=your_secure_key"
    echo "     * FLASK_ENV=production"
    echo "     * CORS_ORIGINS=https://$(git config user.name).github.io"
    echo "   - 创建 PostgreSQL 数据库并连接"
    echo ""
    echo "2. 📦 前端部署 (GitHub Pages):"
    echo "   - 进入 GitHub 仓库设置"
    echo "   - 启用 GitHub Pages"
    echo "   - 选择 'GitHub Actions' 作为源"
    echo "   - GitHub Actions 会自动部署"
    echo ""
    echo "3. 🔗 更新 API 地址:"
    echo "   - 获取 Render 后端 URL"
    echo "   - 更新 frontend/.env.production"
    echo "   - 重新推送触发前端部署"
    echo ""
    echo "📊 预期地址："
    echo "   - 前端: https://$(git config user.name).github.io/quote-web"
    echo "   - 后端: https://your-render-backend.onrender.com"
    echo ""
    echo "📚 详细指南: backend-python/docs/GITHUB_PAGES_RENDER_GUIDE.md"
    echo ""
    echo "💡 小贴士："
    echo "   - Render 免费服务会在15分钟无活动后休眠"
    echo "   - 首次访问休眠的服务需要等待30秒启动"
    echo "   - 所有服务都完全免费使用"
    echo ""
}

# 主函数
main() {
    echo "🎯 GitHub Pages + Render 部署助手"
    echo "================================="
    
    check_environment
    configure_frontend
    configure_backend
    deploy_to_github
    show_deployment_info
}

# 运行主函数
main "$@"
