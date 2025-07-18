#!/bin/bash

# 部署验证脚本
# 用于验证 Render 和 GitHub Pages 部署

set -e

echo "🚀 部署验证开始..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要的工具
echo -e "${BLUE}📋 检查必要工具...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 所有必要工具已安装${NC}"

# 检查 Git 状态
echo -e "${BLUE}📋 检查 Git 状态...${NC}"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}⚠️  有未提交的更改${NC}"
    git status --short
    echo -e "${YELLOW}请先提交所有更改${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git 状态干净${NC}"

# 检查当前分支
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo -e "${YELLOW}⚠️  当前分支不是 main: $current_branch${NC}"
    echo -e "${YELLOW}是否切换到 main 分支? (y/n)${NC}"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        git checkout main
        echo -e "${GREEN}✅ 已切换到 main 分支${NC}"
    else
        echo -e "${RED}❌ 部署需要在 main 分支进行${NC}"
        exit 1
    fi
fi

# 运行后端测试
echo -e "${BLUE}🧪 运行后端测试...${NC}"
cd backend-python
if python -m pytest --tb=short -q; then
    echo -e "${GREEN}✅ 后端测试通过${NC}"
else
    echo -e "${RED}❌ 后端测试失败${NC}"
    cd ..
    exit 1
fi
cd ..

# 构建前端
echo -e "${BLUE}🏗️  构建前端...${NC}"
cd frontend

echo -e "${BLUE}📦 安装前端依赖...${NC}"
if npm ci; then
    echo -e "${GREEN}✅ 前端依赖安装成功${NC}"
else
    echo -e "${RED}❌ 前端依赖安装失败${NC}"
    cd ..
    exit 1
fi

echo -e "${BLUE}🏗️  构建前端应用...${NC}"
if npm run build; then
    echo -e "${GREEN}✅ 前端构建成功${NC}"
else
    echo -e "${RED}❌ 前端构建失败${NC}"
    cd ..
    exit 1
fi

# 检查构建输出
if [[ ! -d "dist" ]]; then
    echo -e "${RED}❌ 构建输出目录不存在${NC}"
    cd ..
    exit 1
fi

if [[ ! -f "dist/index.html" ]]; then
    echo -e "${RED}❌ 构建输出缺少 index.html${NC}"
    cd ..
    exit 1
fi

echo -e "${GREEN}✅ 前端构建输出验证通过${NC}"
cd ..

# 检查部署配置文件
echo -e "${BLUE}📋 检查部署配置...${NC}"

# 检查 render.yaml
if [[ -f "render.yaml" ]]; then
    echo -e "${GREEN}✅ render.yaml 存在${NC}"
    
    # 检查是否包含占位符
    if grep -q "YOUR_USERNAME" render.yaml; then
        echo -e "${YELLOW}⚠️  render.yaml 包含占位符 YOUR_USERNAME${NC}"
        echo -e "${YELLOW}请更新 render.yaml 中的用户名${NC}"
    fi
    
    if grep -q "YOUR_RENDER_URL" render.yaml; then
        echo -e "${YELLOW}⚠️  render.yaml 包含占位符 YOUR_RENDER_URL${NC}"
    fi
else
    echo -e "${RED}❌ render.yaml 不存在${NC}"
fi

# 检查 GitHub Actions 配置
if [[ -f ".github/workflows/deploy.yml" ]]; then
    echo -e "${GREEN}✅ GitHub Actions 配置存在${NC}"
    
    # 检查是否包含占位符
    if grep -q "YOUR_RENDER_URL" .github/workflows/deploy.yml; then
        echo -e "${YELLOW}⚠️  deploy.yml 包含占位符 YOUR_RENDER_URL${NC}"
        echo -e "${YELLOW}请更新 .github/workflows/deploy.yml 中的 Render URL${NC}"
    fi
else
    echo -e "${RED}❌ GitHub Actions 配置不存在${NC}"
fi

# 推送到 GitHub
echo -e "${BLUE}📤 推送到 GitHub...${NC}"
if git push origin main; then
    echo -e "${GREEN}✅ 代码已推送到 GitHub${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi

# 显示部署指南
echo -e "\n${BLUE}📖 部署指南${NC}"
echo -e "${BLUE}===============================================${NC}"

echo -e "\n${YELLOW}🔗 Render 部署步骤:${NC}"
echo "1. 访问 https://render.com/"
echo "2. 连接你的 GitHub 账户"
echo "3. 选择 quote-web 仓库"
echo "4. 选择 'render.yaml' 配置"
echo "5. 更新环境变量中的 CORS_ORIGINS"
echo "6. 部署后端服务"

echo -e "\n${YELLOW}📄 GitHub Pages 部署步骤:${NC}"
echo "1. 访问 GitHub 仓库设置"
echo "2. 进入 Pages 设置"
echo "3. 选择 'GitHub Actions' 作为源"
echo "4. 更新 .github/workflows/deploy.yml 中的 API URL"
echo "5. 推送代码触发部署"

echo -e "\n${YELLOW}🔧 配置更新提醒:${NC}"
echo "- 更新 render.yaml 中的 YOUR_USERNAME"
echo "- 更新 .github/workflows/deploy.yml 中的 YOUR_RENDER_URL"
echo "- 在 Render 中设置正确的 CORS_ORIGINS"

echo -e "\n${GREEN}✅ 部署验证完成！${NC}"
echo -e "${BLUE}现在可以进行实际部署了${NC}"
