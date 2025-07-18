# 🚀 GitHub Pages + Render 部署

> 前端免费托管在 GitHub Pages，后端部署在 Render

## 📋 快速部署

### 1. 一键部署
```bash
# 在项目根目录运行
./deploy_github_render.sh
```

### 2. 手动部署

#### 后端 (Render)
1. 访问 [Render.com](https://render.com)
2. 连接 GitHub 仓库
3. 创建 Web Service
4. 选择 `backend-python` 目录
5. 设置构建命令: `pip install -r requirements_prod.txt`
6. 设置启动命令: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
7. 设置环境变量：
   ```
   JWT_SECRET_KEY=your_secure_key
   FLASK_ENV=production
   CORS_ORIGINS=https://your-username.github.io
   ```
8. 创建 PostgreSQL 数据库并连接

#### 前端 (GitHub Pages)
1. 进入 GitHub 仓库设置
2. 启用 GitHub Pages
3. 选择 "GitHub Actions" 作为源
4. 推送代码会自动部署

### 3. 配置 API 地址
更新 `frontend/.env.production`：
```
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

## 🔗 访问地址

- **前端**: https://your-username.github.io/quote-web
- **后端**: https://your-render-backend.onrender.com

## 💰 成本

- **GitHub Pages**: 完全免费
- **Render Web Service**: 750 小时/月免费
- **Render PostgreSQL**: 1GB 存储免费
- **总计**: 完全免费使用

## ⚡ 特点

- **自动部署**: 推送代码自动部署
- **HTTPS**: 默认提供 SSL 证书  
- **CDN**: 全球内容分发网络
- **监控**: 实时日志和监控
- **休眠**: 15分钟无活动后休眠（免费限制）

## 📚 详细指南

完整部署指南: [GITHUB_PAGES_RENDER_GUIDE.md](backend-python/docs/GITHUB_PAGES_RENDER_GUIDE.md)
