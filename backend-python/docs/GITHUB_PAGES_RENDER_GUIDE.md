# GitHub Pages + Render 部署指南

## 📋 部署方案概述

**前端**: GitHub Pages (免费)
**后端**: Render (免费)
**数据库**: Render PostgreSQL (免费)

## 🚀 部署步骤

### 1. 后端部署到 Render

#### 1.1 准备工作
```bash
# 确保在 backend-python 目录
cd backend-python

# 安装依赖
pip install -r requirements_prod.txt

# 测试本地运行
python app.py
```

#### 1.2 Render 部署
1. 访问 [Render.com](https://render.com)
2. 使用 GitHub 登录
3. 点击 "New +"
4. 选择 "Web Service"
5. 连接 GitHub 仓库
6. 选择 `backend-python` 目录作为根目录

#### 1.3 部署设置
- **Name**: quote-api
- **Environment**: Python
- **Build Command**: `pip install -r requirements_prod.txt`
- **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
- **Plan**: Free

#### 1.4 环境变量设置
在 Render 控制台设置以下环境变量：
```
JWT_SECRET_KEY=your_very_secure_jwt_secret_key_here
FLASK_ENV=production
CORS_ORIGINS=https://your-username.github.io
```

#### 1.5 数据库配置
1. 在 Render 控制台创建新的 PostgreSQL 数据库
2. 连接数据库到 Web Service
3. Render 会自动设置 `DATABASE_URL` 环境变量

### 2. 前端部署到 GitHub Pages

#### 2.1 启用 GitHub Pages
1. 进入 GitHub 仓库设置
2. 找到 "Pages" 部分
3. Source 选择 "GitHub Actions"

#### 2.2 配置 API 地址
更新前端配置文件，将 API 地址指向 Render 后端：

```bash
# 在 frontend 目录更新 .env.production
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

#### 2.3 自动部署
GitHub Actions 会自动：
- 监听 `frontend/` 目录的变化
- 构建 React 应用
- 部署到 GitHub Pages

### 3. 域名配置

#### 3.1 获取部署 URL
- **前端**: `https://your-username.github.io/quote-web`
- **后端**: `https://your-render-backend.onrender.com`

#### 3.2 更新 CORS 配置
在 Render 中更新 `CORS_ORIGINS` 环境变量：
```
CORS_ORIGINS=https://your-username.github.io
```

## 🔧 配置文件说明

### Render 配置
- `render.yaml` - Render 平台配置（可选）
- `requirements_prod.txt` - 生产环境依赖
- 启动命令: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### GitHub Pages 配置
- `.github/workflows/deploy-frontend.yml` - 自动部署工作流
- `frontend/.env.production` - 生产环境配置

## 📊 成本分析

| 服务 | 免费额度 | 限制 |
|------|----------|------|
| GitHub Pages | 无限制 | 100GB 带宽/月 |
| Render Web Service | 750 小时/月 | 休眠机制 |
| Render PostgreSQL | 1GB 存储 | 90天数据保留 |
| **总计** | **完全免费** | **小型项目足够** |

## 🛠️ 一键部署脚本

```bash
#!/bin/bash
echo "🚀 开始部署到 GitHub Pages + Render..."

# 1. 推送代码到 GitHub
git add .
git commit -m "Deploy to GitHub Pages + Render"
git push origin main

# 2. GitHub Actions 会自动部署前端
echo "📦 前端将自动部署到 GitHub Pages"

# 3. 在 Render 控制台手动创建 Web Service
echo "🎨 请在 Render 控制台创建 Web Service"

echo "✅ 部署完成！"
```

## 🔄 更新流程

1. **前端更新**: 推送到 `frontend/` 目录，GitHub Actions 自动部署
2. **后端更新**: 推送到 `backend-python/` 目录，Render 自动部署
3. **数据库更新**: 通过 Render 控制台或迁移脚本

## 📋 部署检查清单

- [ ] Render 后端部署成功
- [ ] 环境变量设置正确
- [ ] PostgreSQL 数据库连接正常
- [ ] GitHub Pages 部署成功
- [ ] 前端 API 地址配置正确
- [ ] CORS 配置正确
- [ ] 域名访问正常

## 🆘 常见问题

**Q: Render 免费服务休眠怎么办？**
A: 免费服务在15分钟无活动后休眠，首次访问需要等待30秒启动

**Q: 前端无法访问后端**
A: 检查 CORS 配置和 API 地址，确保没有协议错误

**Q: 数据库连接失败**
A: 确保 PostgreSQL 数据库已创建并连接到 Web Service

**Q: GitHub Pages 404 错误**
A: 检查 GitHub Pages 设置和构建路径配置

## 🎯 优势

1. **完全免费**: 所有服务都有免费套餐
2. **自动部署**: 推送代码自动部署
3. **HTTPS**: 默认提供 SSL 证书
4. **CDN**: GitHub Pages 和 Render 都有全球 CDN
5. **监控**: Render 提供日志和监控

## 🔗 有用链接

- [Render 文档](https://render.com/docs)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
